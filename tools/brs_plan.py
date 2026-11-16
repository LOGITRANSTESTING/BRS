"""Function-wise BRS planning for a Dr.Explain user manual: one BRS per function.

  python tools/brs_plan.py plan  "<manual>.gui"            # list functions, create/refresh the plan
  python tools/brs_plan.py show  "<manual>.gui"            # plan with status per function
  python tools/brs_plan.py export "<manual>.gui" --function N   # pages + images of function N -> work dir
  python tools/brs_plan.py done  "<manual>.gui" --function N --file "output/<Module>/....docx" [--version 01.01]

What is a function:
  - every child of a "... Group Function" / "... Single Function" page (e.g. ECOR Number Generate,
    Accept Release). The same name under Group and Single = two functions (kind tells them apart).
  - a manual without Group/Single sections (e.g. ES-FL Fix, Container Stock Entry) = ONE function:
    the main screen.
  Every function BRS also uses the screen's shared pages (the screen page, Query Fields, Data Grid
  Screen and their How-to pages), because Search/Display Area come from them.

Updated manual: run `plan` again on the new .gui. Each function's pages are fingerprinted (text +
images), so the plan marks functions as new / changed / unchanged / removed. A changed function whose
BRS was done gets status "update": rebuild it with the next version and a new history row.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ilis_gui as G


def slug(s, n=50):
    return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')[:n] or 'x'


def plan_path(manual):
    return Path('work/brs') / slug(Path(manual).stem) / 'plan.json'


def tree(manual):
    root = G.load_tree(manual)
    rows = []  # (node, depth, title, path)
    stack = []
    for n, d in G._nodes(root):
        if n.tag == 'index': continue
        t = (n.findtext('m_title') or '').strip()
        stack = stack[:d] + [t]
        rows.append((n, d, t, ' > '.join(stack)))
    return rows


def fingerprint(nodes):
    h = hashlib.sha1()
    for n in nodes: h.update((n.findtext('m_title') or '').encode()); h.update((n.findtext('m_description') or '').encode())
    return h.hexdigest()[:16]


def subtree(rows, i):
    d0 = rows[i][1]; out = [rows[i]]
    for r in rows[i + 1:]:
        if r[1] <= d0: break
        out.append(r)
    return out


def functions(manual):
    rows = tree(manual)
    sections = [i for i, r in enumerate(rows) if re.search(r'(group|single)\s+function', r[2], re.I)]
    # shared pages: the main screen node (first depth-0 page with children that is not the cover) and
    # its children that are not Group/Single sections
    screen_i = next((i for i, r in enumerate(rows) if r[1] == 0 and len(subtree(rows, i)) > 1), 0)
    shared = []
    for r in subtree(rows, screen_i):
        if any(r is rows[s] or r[3].startswith(rows[s][3] + ' > ') for s in sections): continue
        shared.append(r)
    out = []
    if not sections:
        st = subtree(rows, screen_i)
        out.append({'name': rows[screen_i][2], 'kind': 'Screen', 'path': rows[screen_i][3],
                    'pages': [r[3] for r in st], 'fp': fingerprint([r[0] for r in st])})
    for s in sections:
        kind = 'Group' if re.search('group', rows[s][2], re.I) else 'Single'
        d = rows[s][1]
        for j in range(s + 1, len(rows)):
            if rows[j][1] <= d: break
            if rows[j][1] == d + 1:
                st = subtree(rows, j)
                out.append({'name': rows[j][2], 'kind': kind, 'path': rows[j][3], 'pages': [r[3] for r in st],
                            'fp': fingerprint([r[0] for r in st] + [r[0] for r in shared])})
    return out, [r[3] for r in shared], rows


def load(manual):
    p = plan_path(manual)
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def save(manual, plan):
    p = plan_path(manual); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding='utf-8')


def cmd_plan(manual):
    fns, shared, _ = functions(manual)
    old = load(manual)
    oldmap = {(f['kind'], f['name']): f for f in (old or {}).get('functions', [])}
    newkeys = set()
    for k, f in enumerate(fns, 1):
        key = (f['kind'], f['name']); newkeys.add(key)
        o = oldmap.get(key)
        f['n'] = k
        f['fn'] = slug(('%s_%s' % (f['kind'], f['name'])).lower(), 60)
        if not o: f['status'] = 'new'; f['change'] = 'new'
        else:
            for keep in ('file', 'version', 'author', 'done_fp'):
                if keep in o: f[keep] = o[keep]
            if o.get('status') in ('done', 'update'):
                f['status'] = 'update' if f['fp'] != o.get('done_fp', o['fp']) else 'done'
            else:
                f['status'] = o.get('status', 'new')
            f['change'] = 'changed' if f['fp'] != o['fp'] else 'unchanged'
    removed = [dict(o, status='removed') for key, o in oldmap.items() if key not in newkeys]
    plan = {'manual': str(manual), 'shared_pages': shared, 'functions': fns, 'removed': removed}
    save(manual, plan)
    show(plan)


def show(plan):
    print('Manual:', plan['manual'])
    print('Shared pages (used by every BRS):', '; '.join(p.split(' > ')[-1] for p in plan['shared_pages']))
    for f in plan['functions']:
        extra = (' -> ' + f['file']) if f.get('file') else ''
        print('%2d. [%-6s] %-38s %-7s %s%s' % (f['n'], f['kind'], f['name'][:38], f['status'], f['change'] if f['change'] != 'unchanged' else '', extra))
    for f in plan['removed']:
        print('  REMOVED from manual: [%s] %s %s' % (f['kind'], f['name'], f.get('file', '')))
    todo = [f for f in plan['functions'] if f['status'] in ('new', 'update', 'in progress')]
    print('%d function(s), %d to do (new/update/in progress).' % (len(plan['functions']), len(todo)))


def node_by_path(rows, path):
    for r in rows:
        if r[3] == path: return r[0]
    raise SystemExit('page not found: ' + path)


def cmd_export(manual, n):
    plan = load(manual) or sys.exit('run plan first')
    f = next((x for x in plan['functions'] if x['n'] == n), None) or sys.exit('no function %d' % n)
    _, _, rows = functions(manual)
    out = Path('work/brs') / slug(Path(manual).stem) / f['fn'] / 'pages'
    out.mkdir(parents=True, exist_ok=True)
    listing = []
    for group, paths in (('shared', plan['shared_pages']), ('function', f['pages'])):
        for p in paths:
            node = node_by_path(rows, p)
            s = slug(p.split(' > ')[-1]) + '_' + hashlib.sha1(p.encode()).hexdigest()[:4]
            md = G.desc_to_markup(node.findtext('m_description'), out / 'img', s)
            (out / (s + '.md')).write_text('---\ntitle: %s\npath: %s\nused_as: %s\n---\n%s' % (node.findtext('m_title'), p, group, md), encoding='utf-8')
            listing.append('%-8s %s -> %s.md' % (group, p, s))
    f['status'] = 'in progress'; save(manual, plan)
    print('\n'.join(listing)); print('images in', out / 'img')


def cmd_done(manual, n, file, version):
    plan = load(manual) or sys.exit('run plan first')
    f = next((x for x in plan['functions'] if x['n'] == n), None) or sys.exit('no function %d' % n)
    f.update(status='done', file=file, done_fp=f['fp'])
    if version: f['version'] = version
    save(manual, plan); print('marked done:', f['name'], file)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', choices=['plan', 'show', 'export', 'done'])
    ap.add_argument('manual'); ap.add_argument('--function', type=int); ap.add_argument('--file'); ap.add_argument('--version')
    a = ap.parse_args()
    if a.action == 'plan': cmd_plan(a.manual)
    elif a.action == 'show': show(load(a.manual) or sys.exit('run plan first'))
    elif a.action == 'export': cmd_export(a.manual, a.function)
    else: cmd_done(a.manual, a.function, a.file, a.version)


if __name__ == '__main__':
    main()
