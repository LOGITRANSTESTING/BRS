"""ILISCyber BRS builder: fills a copy of the house BRS sample (.docx) from a JSON spec.

  python tools/brs_docx.py inspect template/BRS_Sample_Accept_Release.docx
  python tools/brs_docx.py skeleton work/brs/<fn>/brs.json            # empty spec to fill in
  python tools/brs_docx.py build work/brs/<fn>/brs.json --out "output/brs/BRS - <Module> - <Function> V_1.0.docx"
  python tools/brs_docx.py check "output/brs/....docx"                 # text dump to verify the result

The template's styles, header, footer, logo, TOC field and table formats are kept: tables are refilled by
cloning their first data row, so every new row has the house format.
"""
import argparse, copy, json, re, sys, datetime
from pathlib import Path

try:
    import docx
    from docx.shared import Emu
except ImportError:
    sys.exit('python-docx is missing: pip install python-docx')

DEFAULT_TEMPLATE = 'template/BRS_Sample_Accept_Release.docx'

SKELETON = {
    "template": DEFAULT_TEMPLATE,
    "company": "YANG MING MARINE TRANSPORT CORP.",
    "module": "Agency Booking",
    "function": "",
    "version": "01.01",
    "date": "",  # DD/MM/YYYY, today when empty
    "history": [{"date": "", "version": "V01.01", "author": "",
                 "description": "Initial version created based on the confirmed screen designs"}],
    "purpose": "This document explains the purpose of <Module>'s <Function> details.",
    "images": [{"file": "work/brs/<fn>/img/01.png", "caption": "Image I"}],
    "features": [],          # leave empty = blank section
    "events": [{"event_type": "", "description": "", "triggered_when": "", "remarks": ""}],
    "search_title": "",      # optional 3.1 heading, empty = "Search"
    "search": [{"name": "", "type": "", "ui": "", "db": "", "values": ""}],
    "display_title": "",     # optional 3.2 heading, empty = "Display Area"
    "display": [{"name": "", "type": "", "ui": "", "db": "", "values": "", "remarks": ""}],
    "references": [],
    "assumptions": []
}


# ------------------------------------------------------------------ helpers
def set_par_text(p, text):
    """Replace a paragraph's text but keep the formatting of its first run."""
    runs = p.runs
    if not runs:
        p.add_run(text); return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def set_cell(cell, text):
    ps = cell.paragraphs
    set_par_text(ps[0], text or '')
    for p in ps[1:]:
        p._p.getparent().remove(p._p)


def remove_par(p):
    p._p.getparent().remove(p._p)


def find_heading(doc, text, style_prefix='Heading'):
    for i, p in enumerate(doc.paragraphs):
        if p.style.name.startswith(style_prefix) and p.text.strip().lower().startswith(text.lower()):
            return i
    raise KeyError('heading not found: ' + text)


def body_between(doc, start_idx):
    """Paragraphs after heading start_idx until the next heading."""
    out = []
    for p in doc.paragraphs[start_idx + 1:]:
        if p.style.name.startswith('Heading'): break
        out.append(p)
    return out


def fill_table(table, rows, keys, keep_header=1):
    """Keep the header, clone the first data row for every new row, remove the rest."""
    tmpl = copy.deepcopy(table.rows[keep_header]._tr) if len(table.rows) > keep_header else copy.deepcopy(table.rows[-1]._tr)
    for r in list(table.rows)[keep_header:]:
        r._tr.getparent().remove(r._tr)
    if not rows:  # one empty row so the table stays usable
        rows = [{k: '' for k in keys}]
    for row in rows:
        tr = copy.deepcopy(tmpl); table._tbl.append(tr)
        cells = table.rows[-1].cells
        for c, k in zip(cells, keys):
            set_cell(c, str(row.get(k, '') or ''))


def clear_table(table, keep_header=0):
    # Record of Approval: keep the label cells (Author/Auditor/Approver, Signature, Date), blank everything else
    labels = {'author', 'auditor', 'approver', 'signature', 'date', 'reviewer'}
    for r in table.rows:
        for c in r.cells:
            if c.text.strip().lower() not in labels:
                set_cell(c, '')


def roman(n):
    vals = [(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    s = ''
    for v, r in vals:
        while n >= v: s += r; n -= v
    return s


# ------------------------------------------------------------------ build
def build(spec, out):
    tpl = spec.get('template') or DEFAULT_TEMPLATE
    doc = docx.Document(tpl)
    P = doc.paragraphs

    # cover (first non-empty Normal paragraphs, in the sample's order)
    cover = [p for p in P[:20] if p.text.strip()]
    date = spec.get('date') or datetime.date.today().strftime('%d/%m/%Y')
    vals = [spec.get('company', cover[0].text.strip()), 'ILISCyber – ' + spec['module'],
            'Business Requirement Specification', spec['function'], 'Version ' + spec.get('version', '01.01'), date]
    for p, v in zip(cover[:6], vals):
        set_par_text(p, v)

    # history of modifications (table 0)
    T = doc.tables
    hist = spec.get('history') or []
    for h in hist:
        if not h.get('date'): h['date'] = datetime.date.today().strftime('%d.%m.%Y')
    fill_table(T[0], hist, ['date', 'version', 'author', 'description'])
    # record of approval (table 1): blank
    clear_table(T[1])

    # purpose
    i = find_heading(doc, 'Purpose')
    body = body_between(doc, i)
    first = next((p for p in body if p.text.strip()), body[0] if body else None)
    set_par_text(first, spec.get('purpose', ''))
    for p in body:
        if p is not first and p.text.strip(): remove_par(p)

    # UI design: drop old captions/images, insert new ones in the same caption style
    i = find_heading(doc, 'UI Design')
    body = body_between(doc, i)
    cap_tmpl = next((p for p in body if p.text.strip().startswith('Image')), None)
    img_tmpl = next((p for p in body if 'graphic' in p._p.xml), None)
    cap_xml = copy.deepcopy(cap_tmpl._p) if cap_tmpl is not None else None
    img_ppr = copy.deepcopy(img_tmpl._p.pPr) if img_tmpl is not None and img_tmpl._p.pPr is not None else None
    anchor = doc.paragraphs[i]._p
    for p in body: remove_par(p)
    width = doc.sections[0].page_width - doc.sections[0].left_margin - doc.sections[0].right_margin
    last = anchor
    for k, im in enumerate(spec.get('images', []), 1):
        cap = copy.deepcopy(cap_xml) if cap_xml is not None else None
        if cap is not None:
            last.addnext(cap); last = cap
            cp = docx.text.paragraph.Paragraph(cap, doc.paragraphs[i]._parent)
            set_par_text(cp, im.get('caption') or 'Image ' + roman(k))
            cp.paragraph_format.keep_with_next = True
        newp = doc.add_paragraph()  # created at the end, moved below
        if img_ppr is not None: newp._p.insert(0, copy.deepcopy(img_ppr))
        newp.add_run().add_picture(im['file'], width=Emu(int(width)))
        last.addnext(newp._p); last = newp._p

    # features & functionalities, menu items, process flow, references, assumptions: text lists (blank = empty)
    for head, key in [('Features', 'features'), ('Menu Items', 'menu_items'), ('Business Process Flow', 'process_flow'),
                      ('References', 'references'), ('Assumptions', 'assumptions')]:
        try: i = find_heading(doc, head)
        except KeyError: continue
        body = [p for p in body_between(doc, i) if not p._p.xpath('.//w:tbl')]
        for p in body:
            if p.text.strip() or 'graphic' in p._p.xml: remove_par(p)
        last = doc.paragraphs[i]._p
        for line in reversed(spec.get(key) or []):
            np_ = doc.add_paragraph(line)
            last.addnext(np_._p)

    # tables: events (2), search (3), display (4) - located by header text, not index
    def table_with(header):
        for t in doc.tables:
            if [c.text.strip() for c in t.rows[0].cells][:len(header)] == header: return t
        raise KeyError(header)
    fill_table(table_with(['Event Type', 'Description']), spec.get('events'), ['event_type', 'description', 'triggered_when', 'remarks'])
    tabs = [t for t in doc.tables if t.rows[0].cells[0].text.strip() == 'UI Item Name']
    fill_table(tabs[0], spec.get('search'), ['name', 'type', 'ui', 'db', 'values'])
    fill_table(tabs[1], spec.get('display'), ['name', 'type', 'ui', 'db', 'values', 'remarks'])

    # optional renames of the 3.1 / 3.2 headings (empty = keep the template's "Search" / "Display Area")
    for head, key in [('Search', 'search_title'), ('Display Area', 'display_title')]:
        if spec.get(key):
            set_par_text(doc.paragraphs[find_heading(doc, head)], spec[key])

    # document properties
    if hist and hist[0].get('author'): doc.core_properties.author = hist[0]['author']
    doc.core_properties.title = 'BRS - %s - %s' % (spec['module'], spec['function'])

    # ask Word to refresh the TOC on open
    st = doc.settings.element
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    if st.find(qn('w:updateFields')) is None:
        u = OxmlElement('w:updateFields'); u.set(qn('w:val'), 'true'); st.append(u)

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    keep_template_parts(tpl, out)
    print('saved', out)


KEEP = re.compile(r'^word/(header\d*|footer\d*|styles|stylesWithEffects|numbering|fontTable|webSettings)\.xml$|^word/theme/|^word/_rels/(header|footer)\d*\.xml\.rels$|^word/glossary/')


def keep_template_parts(tpl, out):
    """Header, footer, styles, numbering, fonts and theme are copied byte-for-byte from the sample,
    so every BRS carries exactly the house header/footer/look."""
    import zipfile, shutil, tempfile
    src = zipfile.ZipFile(tpl)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.docx').name
    with zipfile.ZipFile(out) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        names = set(src.namelist())
        for item in zin.infolist():
            data = src.read(item.filename) if (KEEP.match(item.filename) and item.filename in names) else zin.read(item.filename)
            zout.writestr(item, data)
    shutil.move(tmp, out)


def inspect(path):
    d = docx.Document(path)
    for i, p in enumerate(d.paragraphs):
        if p.text.strip() or 'graphic' in p._p.xml:
            print('%3d %-10s %s%s' % (i, p.style.name[:10], p.text[:90], ' [IMG]' if 'graphic' in p._p.xml else ''))
    for i, t in enumerate(d.tables):
        print('TABLE %d: %d rows x %d cols | %s' % (i, len(t.rows), len(t.columns), ' | '.join(c.text.strip() for c in t.rows[0].cells)))
        for r in t.rows[1:]:
            print('    ' + ' | '.join(c.text.strip()[:40] for c in r.cells))
    print('core author:', d.core_properties.author)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', choices=['inspect', 'skeleton', 'build', 'check'])
    ap.add_argument('path'); ap.add_argument('--out')
    a = ap.parse_args()
    if a.action in ('inspect', 'check'): inspect(a.path)
    elif a.action == 'skeleton':
        Path(a.path).parent.mkdir(parents=True, exist_ok=True)
        Path(a.path).write_text(json.dumps(SKELETON, indent=1, ensure_ascii=False), encoding='utf-8'); print('wrote', a.path)
    else:
        spec = json.loads(Path(a.path).read_text(encoding='utf-8'))
        if not a.out: sys.exit('--out is required')
        build(spec, a.out)


if __name__ == '__main__':
    main()
