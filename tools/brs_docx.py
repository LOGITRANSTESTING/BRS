"""ILISCyber BRS builder: fills a copy of the house BRS sample (.docx) from a JSON spec.

  python tools/brs_docx.py inspect template/BRS_Sample_Accept_Release.docx
  python tools/brs_docx.py skeleton work/brs/<fn>/brs.json            # empty spec to fill in
  python tools/brs_docx.py build work/brs/<fn>/brs.json --out "output/<Module>/BRS - <Module> - <Function> V_1.0.docx"
  python tools/brs_docx.py check "output/<Module>/....docx"                 # text dump to verify the result

The template's styles, header, footer, logo, TOC field and table formats are kept: tables are refilled by
cloning their first data row, so every new row has the house format.
"""
import argparse, copy, json, re, sys, datetime
from pathlib import Path

try:
    import docx
    from docx.shared import Emu, Pt
except ImportError:
    sys.exit('python-docx is missing: pip install python-docx')

DEFAULT_TEMPLATE = 'template/BRS_Sample_Accept_Release.docx'

SKELETON = {
    "template": DEFAULT_TEMPLATE,
    "company": "YANG MING MARINE TRANSPORT CORP.",
    "module": "Agency Booking",
    "module_line": "",       # optional exact cover line, empty = "ILISCyber – <module>" (DCSA eBK: "DCSA – eBK Process")
    "function": "",
    "version": "01.01",
    "date": "",  # DD/MM/YYYY, today when empty
    "history": [{"date": "", "version": "V01.01", "author": "Appsara",
                 "description": "Initial version created based on the confirmed screen designs"}],
    "purpose": "This document explains the purpose of <Module>'s <Screen> <Function> details.",
    "images": [{"file": "work/brs/<fn>/img/01.png", "caption": "Image I"}],  # optional "section": "Freeze" adds a 1.2.x sub-heading when it changes; an entry without "file" = sub-heading only (+ optional "text")
    "features": [],          # leave empty = blank section; {"section": "X"} adds a 2.1.x sub-title
    "events": [{"event_type": "", "description": "", "triggered_when": "", "remarks": ""}],  # optional "section": one 2.2.x heading + table per section
    "search_title": "",      # optional 3.1 heading, empty = "Search"
    "search": [{"name": "", "type": "", "ui": "", "db": "", "values": ""}],
    "display_title": "",     # optional 3.2 heading, empty = "Display Area"
    "drop_display": False,   # true = remove the 3.2 section entirely (all rows are in 3.1)
                             # 3.1 / 3.2 with no filled rows are always removed (heading + table)
    "display": [{"name": "", "type": "", "ui": "", "db": "", "values": "", "remarks": ""}],
    "extra_tables": [],      # optional 3.3, 3.4 ...: [{"title": "...", "rows": [display-style rows]}], after 3.2
    "tables": [],            # optional per-function 3.x / 3.x.y: [{"title", "level": 2|3, "text", "rows"}]; replaces 3.1/3.2
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
    vals = [spec.get('company', cover[0].text.strip()), spec.get('module_line') or 'ILISCyber – ' + spec['module'],
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
    sec = doc.sections[0]
    width = sec.page_width - sec.left_margin - sec.right_margin
    # page height left for body text (the header reaches about 24 pt below the top margin)
    body_h = sec.page_height - sec.top_margin - sec.bottom_margin - Pt(24)
    # Image I shares its page with "1. Introduction", 1.1 Purpose + text, "1.2 UI Design" and its caption
    purpose_lines = max(1, -(-len(spec.get('purpose', '')) // 140))
    first_reserve = Pt(34 + 28 + 15 * purpose_lines + 15 + 28 + 20 + 30)
    other_reserve = Pt(20 + 30)  # caption + safety: caption and image always on one page
    last = anchor
    cur_sec = None
    for k, im in enumerate(spec.get('images', []), 1):
        if im.get('section') and im['section'] != cur_sec:
            cur_sec = im['section']
            hp = doc.add_paragraph(cur_sec, style=next(st for st in doc.styles if st.style_id == 'Heading3'))
            hp.paragraph_format.keep_with_next = True
            # same numbering list as "1.2 UI Design", one level down (1.2.1, 1.2.2 ...)
            ui_num = doc.paragraphs[i]._p.pPr.numPr if doc.paragraphs[i]._p.pPr is not None else None
            if ui_num is not None:
                num = copy.deepcopy(ui_num)
                from docx.oxml.ns import qn as _qn
                num.find(_qn('w:ilvl')).set(_qn('w:val'), '2')
                hp._p.get_or_add_pPr().append(num)
            last.addnext(hp._p); last = hp._p
            if k == 1: first_reserve += Pt(28)
        if not im.get('file'):
            # heading-only entry: a function without a screen design keeps its 1.2.x sub-title
            if im.get('text'):
                tp = doc.add_paragraph(im['text']); last.addnext(tp._p); last = tp._p
            continue
        cap = copy.deepcopy(cap_xml) if cap_xml is not None else None
        if cap is not None:
            last.addnext(cap); last = cap
            cp = docx.text.paragraph.Paragraph(cap, doc.paragraphs[i]._parent)
            set_par_text(cp, im.get('caption') or 'Image ' + roman(k))
            cp.paragraph_format.keep_with_next = True
        newp = doc.add_paragraph()  # created at the end, moved below
        if img_ppr is not None: newp._p.insert(0, copy.deepcopy(img_ppr))
        from PIL import Image as _Img
        with _Img.open(im['file']) as _im: iw, ih = _im.size
        max_h = body_h - (first_reserve if k == 1 else other_reserve)
        w = min(int(width), int(max_h * iw / ih))
        newp.add_run().add_picture(im['file'], width=Emu(w))
        last.addnext(newp._p); last = newp._p

    # features & functionalities, menu items, process flow, references, assumptions: text lists (blank = empty)
    for head, key in [('Features', 'features'), ('Menu Items', 'menu_items'), ('Business Process Flow', 'process_flow'),
                      ('References', 'references'), ('Assumptions', 'assumptions')]:
        try: i = find_heading(doc, head)
        except KeyError: continue
        body = [p for p in body_between(doc, i) if not p._p.xpath('.//w:tbl')]
        for p in body:
            if p.text.strip() or 'graphic' in p._p.xml: remove_par(p)
        hpar = doc.paragraphs[i]
        last = hpar._p
        for line in spec.get(key) or []:
            if isinstance(line, dict) and line.get('section'):
                # {"section": "View Request"} = 2.1.x sub-title, same numbering list one level down
                np_ = doc.add_paragraph(line['section'], style=next(st for st in doc.styles if st.style_id == 'Heading3'))
                np_.paragraph_format.keep_with_next = True
                hnum = hpar._p.pPr.numPr if hpar._p.pPr is not None else None
                if hnum is not None:
                    from docx.oxml.ns import qn as _qn
                    num = copy.deepcopy(hnum); num.find(_qn('w:ilvl')).set(_qn('w:val'), '2')
                    np_._p.get_or_add_pPr().append(num)
            else:
                np_ = doc.add_paragraph(line)
            last.addnext(np_._p); last = np_._p

    # tables: events (2), search (3), display (4) - located by header text, not index
    from docx.oxml.ns import qn as _qn_ev

    def table_with(header):
        for t in doc.tables:
            if [c.text.strip() for c in t.rows[0].cells][:len(header)] == header: return t
        raise KeyError(header)
    ev_keys = ['event_type', 'description', 'triggered_when', 'remarks']
    ev_tbl = table_with(['Event Type', 'Description'])
    events = spec.get('events') or []
    if any(e.get('section') for e in events):
        # one 2.2.x heading + table per event "section", in first-seen order (Container Redelivery)
        groups = []
        for e in events:
            if not groups or groups[-1][0] != e.get('section', ''): groups.append((e.get('section', ''), []))
            groups[-1][1].append(e)
        ev_xml = copy.deepcopy(ev_tbl._tbl)
        h22 = doc.paragraphs[find_heading(doc, 'Event Trigger')]
        h_num = h22._p.pPr.numPr if h22._p.pPr is not None else None
        h3 = next(st for st in doc.styles if st.style_id == 'Heading3')
        before = ev_tbl._tbl
        for g, (title, rows) in enumerate(groups):
            tbl = ev_tbl._tbl if g == 0 else copy.deepcopy(ev_xml)
            hp = doc.add_paragraph(title, style=h3)
            hp.paragraph_format.keep_with_next = True
            if h_num is not None:
                num = copy.deepcopy(h_num)
                num.find(_qn_ev('w:ilvl')).set(_qn_ev('w:val'), '2')
                hp._p.get_or_add_pPr().append(num)
            if g == 0:
                before.addprevious(hp._p)
            else:
                before.addnext(hp._p); hp._p.addnext(tbl)
            fill_table(docx.table.Table(tbl, doc.paragraphs[0]._parent), rows, ev_keys)
            before = tbl
    else:
        fill_table(ev_tbl, events, ev_keys)
    tabs = [t for t in doc.tables if t.rows[0].cells[0].text.strip() == 'UI Item Name']
    fill_table(tabs[0], spec.get('search'), ['name', 'type', 'ui', 'db', 'values'])
    fill_table(tabs[1], spec.get('display'), ['name', 'type', 'ui', 'db', 'values', 'remarks'])

    # extra_tables: 3.3, 3.4 ... cloned from the 3.2 heading + table (same style, same 6 columns)
    from docx.oxml.ns import qn as _q
    extras = [x for x in (spec.get('extra_tables') or []) if any(any(str(v).strip() for v in r.values()) for r in x.get('rows') or [])]
    if extras:
        h = doc.paragraphs[find_heading(doc, 'Display Area')]._p
        part, nxt = [h], h.getnext()
        while nxt is not None and nxt.tag != _q('w:sectPr'):
            sty = nxt.find('.//' + _q('w:pStyle')) if nxt.tag == _q('w:p') else None
            if sty is not None and sty.get(_q('w:val'), '').lower().startswith('heading'): break
            part.append(nxt); nxt = nxt.getnext()
        last = part[-1]
        for x in extras:
            for e in part:
                c = copy.deepcopy(e); last.addnext(c); last = c
                if e is h:
                    set_par_text(docx.text.paragraph.Paragraph(c, doc.paragraphs[0]._parent), x.get('title') or '')
                elif c.tag == _q('w:tbl'):
                    fill_table(docx.table.Table(c, doc.paragraphs[0]._parent), x['rows'],
                               ['name', 'type', 'ui', 'db', 'values', 'remarks'])

    # tables: per-function 3.x headings with 3.x.y tables (UC BRS), cloned from the 3.2 heading + table.
    # [{"title": "View Request"}, {"title": "Basic Information", "level": 3, "rows": [...]},
    #  {"title": "Meta Query", "text": "No screen design available"}]. Leave search/display empty so 3.1/3.2 drop.
    if spec.get('tables'):
        h = doc.paragraphs[find_heading(doc, 'Display Area')]._p
        tbl = h.getnext()
        while tbl is not None and tbl.tag != _q('w:tbl'): tbl = tbl.getnext()
        h_xml, t_xml = copy.deepcopy(h), copy.deepcopy(tbl)
        last = tbl
        while last.getnext() is not None and last.getnext().tag == _q('w:p') and not last.getnext().xpath('string(.)').strip() \
                and last.getnext().find('.//' + _q('w:pStyle')) is None:
            last = last.getnext()
        for x in spec['tables']:
            hc = copy.deepcopy(h_xml); last.addnext(hc); last = hc
            hp = docx.text.paragraph.Paragraph(hc, doc.paragraphs[0]._parent)
            set_par_text(hp, x.get('title') or '')
            hp.paragraph_format.keep_with_next = True
            if x.get('level') == 3:
                hc.pPr.find(_q('w:pStyle')).set(_q('w:val'), 'Heading3')
                ilvl = hc.pPr.find('.//' + _q('w:ilvl'))
                if ilvl is not None: ilvl.set(_q('w:val'), '2')
            if x.get('text'):
                tp = doc.add_paragraph(x['text']); last.addnext(tp._p); last = tp._p
            if x.get('rows'):
                tc = copy.deepcopy(t_xml); last.addnext(tc); last = tc
                fill_table(docx.table.Table(tc, doc.paragraphs[0]._parent), x['rows'],
                           ['name', 'type', 'ui', 'db', 'values', 'remarks'])
                sp = doc.add_paragraph(); last.addnext(sp._p); last = sp._p

    # optional renames of the 3.1 / 3.2 headings (empty = keep the template's "Search" / "Display Area")
    for head, key in [('Search', 'search_title'), ('Display Area', 'display_title')]:
        if spec.get(key):
            set_par_text(doc.paragraphs[find_heading(doc, head)], spec[key])

    # drop the 3.1 / 3.2 section (heading + table) when it has no filled rows, or when asked
    # (drop_display: all rows sit in 3.1). The 3 "Column Definitions" heading always stays.
    def has_rows(rows):
        return any(any(str(v).strip() for v in r.values()) for r in (rows or []))
    from docx.oxml.ns import qn as _qn
    for key, title, flag in [('search', spec.get('search_title') or 'Search', 'drop_search'),
                             ('display', spec.get('display_title') or 'Display Area', 'drop_display')]:
        if not (spec.get(flag) or not has_rows(spec.get(key))):
            continue
        h = doc.paragraphs[find_heading(doc, title)]._p
        nxt = h.getnext()
        while nxt is not None:
            sty = nxt.find('.//' + _qn('w:pStyle')) if nxt.tag == _qn('w:p') else None
            if sty is not None and sty.get(_qn('w:val'), '').lower().startswith('heading'): break
            if nxt.tag == _qn('w:sectPr'): break
            cur, nxt = nxt, nxt.getnext()
            cur.getparent().remove(cur)
        h.getparent().remove(h)

    layout(doc)

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


def layout(doc):
    """House page layout: real page breaks instead of the sample's blank-line padding.
    History, Record of Approval, Contents, 1 Introduction and 3 Column Definitions each start a new page
    (4 and 5 follow 3). 2.1 text lines up with the 2.2 table. Empty headings are removed."""
    from docx.oxml.ns import qn
    body = doc.element.body

    def is_blank(e):
        if e.tag != qn('w:p') or ''.join(t.text or '' for t in e.iter(qn('w:t'))).strip(): return False
        if any(b.get(qn('w:type')) != 'page' for b in e.iter(qn('w:br'))): return False  # old page breaks = filler
        return not any(e.find('.//' + qn('w:' + n)) is not None for n in ('drawing', 'pict', 'object', 'fldChar', 'instrText', 'sectPr'))

    def style(e):
        s = e.find('./' + qn('w:pPr') + '/' + qn('w:pStyle'))
        return s.get(qn('w:val')) if s is not None else ''

    for p in list(doc.paragraphs):
        if style(p._p).lower().startswith('heading') and not p.text.strip():
            p._p.getparent().remove(p._p)

    starts = [('History of Modifications', None), ('Record of Approval', None), ('Contents', None),
              ('Introduction', 'Heading1'), ('Column Definitions', 'Heading1')]
    for text, sty in starts:
        p = next((p for p in doc.paragraphs if p.text.strip().lower().startswith(text.lower())
                  and (sty is None or style(p._p) == sty)), None)
        if p is None: continue
        prev = p._p.getprevious()
        while prev is not None and is_blank(prev):
            cur, prev = prev, prev.getprevious()
            body.remove(cur)
        p.paragraph_format.page_break_before = True

    from docx.oxml import OxmlElement
    # filled tables (2.2 events, 3.1, 3.2): a row never splits over two pages; the header row repeats
    for t in doc.tables:
        if t.rows[0].cells[0].text.strip() not in ('Event Type', 'UI Item Name'): continue
        for k, row in enumerate(t.rows):
            trPr = row._tr.get_or_add_trPr()
            for tag in (['w:cantSplit'] + (['w:tblHeader'] if k == 0 else [])):
                if trPr.find(qn(tag)) is None: trPr.append(OxmlElement(tag))

    # 2.1 text: same left/right edge as the 2.2 events table
    try:
        i = find_heading(doc, 'Features')
    except KeyError:
        return
    tbl = next((t for t in doc.tables if t.rows[0].cells[0].text.strip() == 'Event Type'), None)
    if tbl is None: return
    tp = tbl._tbl.tblPr
    sec = doc.sections[0]
    usable = int((sec.page_width - sec.left_margin - sec.right_margin) / 635)  # dxa
    tw = tp.find(qn('w:tblW')); jc = tp.find(qn('w:jc')); ind = tp.find(qn('w:tblInd'))
    if jc is not None and jc.get(qn('w:val')) == 'center' and tw is not None:
        off = max(0, (usable - int(tw.get(qn('w:w')))) // 2)
    else:
        off = int(ind.get(qn('w:w'))) if ind is not None else 0
    for p in body_between(doc, i):
        if p.text.strip():
            sub = 360 if re.match(r'^[a-z]\) ', p.text.strip()) else 0  # a) b) ... sub-conditions sit one step in
            p.paragraph_format.left_indent = Emu((off + sub) * 635)
            p.paragraph_format.right_indent = Emu(off * 635)


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
