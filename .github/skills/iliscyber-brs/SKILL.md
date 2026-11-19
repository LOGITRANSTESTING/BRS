---
name: iliscyber-brs
description: Build ILISCyber BRS (Business Requirement Specification) Word documents from Dr.Explain user manuals - one BRS per function, in the house sample format, with seamless unmarked UI images - interactively, one function at a time; re-run when a manual is updated. Use when the user asks for a BRS.
---

# ILISCyber BRS builder

Use this skill when the user asks for a BRS or Business Requirement Specification. Manuals still use `iliscyber-drexplain-manual`. Mapping documents still use `iliscyber-mapping-document`.

Reply in plain text only. When the user shares a plan, engage with it as it stands.

## Workspace rules
- **Image work:** `python tools/ilis.py` (house toolkit), `python tools/brs_img.py` (BRS image tools) and `python tools/brs_judge.py` (measurement only: marks, scan, judge, gate).
- **Donor rules:** read `references/donor-rules.md` before unmarking anything. It is the user's settled method: damage first, part swaps, per-part judging, recipes, and the gate.
- **Flip / recolour:** `brs_img.py copy --flip / --recolor` only writes a proposal. Show it, and pass `--approved` only after the user says yes to that piece. It works only inside the marked area (`--marks`).
- **Word work:** `python tools/brs_docx.py`.
- **Never write new Python for images or the .docx.** If a tool is missing a feature, say so and ask.
- **Never open a .gui directly.** Use `ilis.py gui info / gui page`.
- **Never edit the user's uploads.** Work in `work/brs/<manual>/<fn>/` (folder names come from `brs_plan.py`). The finished file goes in `output/<Module>/` (the module name, for example `output/EMS/`).
- **Template:** `template/BRS_Sample_Accept_Release.docx`, the house format. Every BRS is a copy of it.
  - **Copied byte-for-byte from the sample:** the header (Business Requirement Specification / LogiTrans Technology Pvt. Ltd.), the footer (Confidential / page number), styles, numbering, fonts and theme.
  - **Kept as in the sample:** the cover layout, logo, page setup, the History, Record of Approval and Contents pages, the heading numbering and the table formats.
  - **What changes:** only the content described below.
  - **Never edit the header or footer.** If the user wants them changed, they change the sample.
- **Show every image as soon as it exists:**
  - in VS Code, the tools open previews;
  - on github.com, commit it to `output/previews/brs_<manual>_<fn>/` and show it in the reply.
- **One BRS at a time, table by table, with questions.** Never bulk-generate. The user wants to understand what goes in the document.
- **Progress log, so a lost connection loses nothing:** keep `work/brs/<manual>/PROGRESS.md`. After every step, decision or user answer, add a dated line (function, step, what was done or decided, the next step), then commit and push it with the work files. At session start, if the log exists, read it first, tell the user where we stopped, and carry on from there.

## One BRS per function
A BRS is written per FUNCTION, never per manual.
- **What counts as a function:**
  - every page under a "Group Function" or "Single Function" section of the manual;
  - a manual with no such sections is one function, the screen itself.
- **Shared pages:** the screen page, Query Fields, Data Grid Screen and their How-to pages are used by every function's BRS. Search and Display Area come from them.

## Session start (and every time the user uploads or updates a manual)
1. Run `python tools/brs_plan.py plan "<manual>.gui"`. Show the user the numbered list it prints: kind (Group/Single/Screen), function name, status, and change.
   - **For an updated manual:**
     - `new` = a function added to the manual;
     - `update` = a function whose BRS was done but whose pages, or the shared pages, changed;
     - `REMOVED` = a function no longer in the manual. Ask what to do with its old BRS. Never delete anything without asking.
2. Ask which function to start with. The default is the first `new` or `update` one. Then go one function at a time; never bulk-generate.
3. Ask the module line for the cover once per manual (for example "Agency Booking", "EMS"). The author is always Appsara (see Step 2).
4. Run `python tools/brs_plan.py export "<manual>.gui" --function N`. This writes that function's pages and images, plus the shared pages, to `work/brs/<manual>/<fn>/pages/`. It handles functions with the same name under Group and Single.
5. Spec file:
   - new function: run `python tools/brs_docx.py skeleton work/brs/<manual>/<fn>/brs.json`;
   - `update`: reuse the existing brs.json.
6. File name: `output/<Module>/BRS - <Module> - <Function> V_<version>.docx`. Add " (Group)" or " (Single)" only when the same function name exists under both.
7. When the user approves the finished document, run `python tools/brs_plan.py done "<manual>.gui" --function N --file "<docx>" --version <v>`.
8. Ask whether to go on to the next function.

## Updating a BRS after the manual changed (status `update`)
1. Re-export the function. Redo only what changed:
   - images: compare the new pages with the old brs.json;
   - tables: compare rows.
2. Show the differences row by row with Why: lines, and ask the questions as in Step 5.
3. Raise the version: 01.01 -> 01.02, and the file name V_1.0 -> V_1.1.
4. Keep the old history rows. Add a new row: today, the new version, the author, and "Updated based on the revised user manual: <what changed>".
5. Build the new file. Keep the old file unless the user says to remove it.

## Step 1 - Images (UI Design)
1. The pages and images are already in `work/brs/<manual>/<fn>/pages/` (from `brs_plan.py export`). Each .md says whether it is `shared` or `function`.
2. Skip the small inline button/icon crops (anything under about 300 px wide). Only full screenshots go into the BRS.
3. Sort the screenshots first: `python tools/brs_judge.py scan work/brs/<manual>/<fn>/pages/img`.
   - **unmarked:** `python tools/brs_img.py unmark SRC img/NN.png --blue` with NO donors (under a second).
   - **twin:** `unmark SRC img/NN.png --donors <the twin> --blue`, then run the gate.
   - **NO TWIN:** do not rely on `unmark`. Build it part by part as in `references/donor-rules.md`
     (`brs_judge.py judge` per damaged part, `brs_img.py copy` for each swap), run
     `python tools/brs_judge.py gate MARKED REPAIRED`, then strip the frame with `unmark REPAIRED img/NN.png`.
   - Never pass `--donor-dir` for the whole folder: it costs about 45 seconds per image and picks wrong donors.
   The older single command, still valid for a twin or a simple mark:
   `python tools/brs_img.py unmark SRC work/brs/<manual>/<fn>/img/NN.png --donors <1-3 named donors> --blue`
   - This removes only what the manual added: the blue frame around the screenshot, the red boxes, the numbered circles, the stubs and leftover mark segments.
   - **The app's own elements must NEVER be removed:** blue panels and lines, blue buttons, red asterisks and red icons, grid lines and highlights. The tool guards this. Any pixel changed outside the marks' footprint is put back, and the report shows `guard_restored_px`.
   - **Blue boxes:** `--blue` only LISTS possible drawn blue boxes (`blue_box_candidates`); it removes nothing, because the app has its own blue rectangles. Show the user each candidate. Remove one only after the user confirms it is a drawn mark and not part of the app: rerun with `--blue-box x0,y0,x1,y1` for each confirmed box.
   - Never use `erase`, `fill` or `copy` to take away something that belongs to the app, unless the user asked for that exact edit.
   - It then repairs everything the marks covered, in this order:
     1. A similar element replaces a damaged one: the same button, box or check box, taken from the same screen, a neighbouring screenshot, or an inline crop. It is used only when it matches every pixel the mark left visible.
     2. Otherwise the element is redrawn in the style of the most similar element on the same screen.
     3. The manual's own inline step crops (buttons, check boxes, icons in `--donor-dir`) are used, but only where a crop matches every surrounding pixel exactly.
     4. Other screenshots of the same screen are used next, then matching areas elsewhere on the same screen.
     5. Last comes row/column continuation, and only where the area is provably plain.
   - If the user's original unmarked screenshots exist in `screenshots/<function>/`, add them with `--donors`. They are the best source.
   - Never invent text or icons. If a mark covered part of a label, value or icon, only a real source can fill it: a clean copy of the same element, or real letters from the letter library (`ilis.py learn / write`, see donor-rules section 6). Visible letter pixels are always kept.
4. The images must be 100% seamless. An image is used only when its report says `"seamless": true` AND `brs_judge.py gate` passes (0 pixels changed outside the marked area, no mark lines left) AND an enlarged crop of every repaired spot looks right. `"seamless": true` alone has been wrong.
   - If not, fix each `unresolved` box with the tools in `references/image-logic.md`.
   - If none of them can do it exactly, show the user the `_check.png` and ask for an unmarked screenshot of that screen, naming the screen and the spot.
   - Never put a smudged or guessed image in the BRS.
5. Drop duplicates, meaning the same screen in the same state. Order the images in the screen's flow and caption them Image I, II, III...
6. Run `python tools/brs_img.py sheet <images> --out output/previews/brs_<manual>_<fn>/sheet.png --labels "Image I,Image II,..."`. Show it.
7. Wait for the user's OK on the images. Then fill `images` in brs.json.

## Step 2 - Cover, history, approval
- **Cover:**
  - company line as in the sample;
  - module;
  - function name;
  - version 01.01;
  - date = today, DD/MM/YYYY.
- **History of Modifications:** one row: today (DD.MM.YYYY), V01.01, author, and "Initial version created based on the confirmed screen designs".
  - **Author = Appsara**, always. She is the only author of every BRS. Do not read it from the manual and do not ask.
- **Record of Approval:** left blank. The tool keeps only the Author/Auditor/Approver/Signature/Date labels.
- **Contents:** the TOC field stays. Word refreshes it on open (updateFields is set). Tell the user to accept the "update fields" prompt, or press F9.

## Step 3 - Introduction
- **1.1 Purpose:** always exactly one sentence, nothing added: "This document explains the purpose of <Module>'s <Screen> <Function> details." Only the function name changes from BRS to BRS. Example: "This document explains the purpose of EMS's Depot Activity Accept Release details." The manual's overview/definition of the function does NOT go here; it goes in 2.1.
- **1.2 UI Design:** the approved images.

## Step 4 - Business Process
- **2.1 Features & Functionalities:** first the manual's definition of the function (its overview page sentence, worded as in the manual, for example Empty Return Pre Advise: "This feature allows the user to generate Pre Advice FCL file for Empty Return PR/Containers."), then the manual's pre-defined conditions, one item per condition, worded as in the manual (for example Generate Release Advise: "Port release should be generated…", "Both booking and PR information should be available."). BLANK only if the manual has neither. Never put pre-conditions in Remarks or Triggered When. Nested sub-conditions: the parent condition is one line, then each sub-condition is its own line labelled a), b), c)..., which the builder indents one step further (Generate Truck Order). Replace the export's stray "&D" marks with double quotes.
- **2.2 Event Triggering's (if any):** see Step 6.
- **2.3 Menu Items:** BLANK.
- **2.4 Business Process Flow:** BLANK.

## Step 5 - Column Definitions & Business Rules (table by table)
Use the rules in `references/column-rules.md`. They include the sample's own rows as examples.

**UI Design sub-sections:** when the manual splits a function into flows (for example Freeze / Unfreeze), give each image a `"section"` ("Freeze", "Unfreeze"); `brs_docx.py build` adds a 1.2.1, 1.2.2 ... heading when the section changes, and the images keep the manual's order (settled on Freeze / Unfreeze). Ask first: the user can choose plain Image I, II ... with no sub-sections even when the manual has flows (settled on Door Address Link). Keep the app's own loading indicator (for example "▶▶▶▶") in an image; it is part of the original screenshot, not a mark (settled on Door Address Link).

Do 3.1 Search first, then 3.2 Display Area. **More than two tables:** put 3.3, 3.4 ... in `extra_tables` (`[{"title": ..., "rows": [display-style rows]}]`); `brs_docx.py build` clones the 3.2 heading + table for each, after 3.2. A single function that opens a form below the grid (Accept Release, EMS Depot Activity): 3.1 "<Function> - Data Grid" (the grid as shown on the form screen; boxes greyed out while the form is open are Display Item), 3.2 "<Function> - Basic Information", 3.3 "<Function> - Container Tab" (or the open tab's name). **An empty table is left out with its heading:** `brs_docx.py build` drops 3.1 / 3.2 when it has no filled rows; the "3 Column Definitions & Business Rules" heading always stays (settled on Empty Return Pre Advise). If the Display Area has a tab or panel with many fields, split it into one round per tab or panel. For each round:
1. Show the image(s) the table is read from. If it helps, add a crop of just that panel: use `ilis.py crop` on the unmarked image, or the sheet.
2. Show the rows as plain text, one row per line: `UI Item Name | Item Type | UI Validation | DB Validation | Possible Values | Remarks`. Under each row add one line starting with "Why:". It says where each column came from:
   - the image, the label and the icon seen (calendar + clock = Date and Time Picker, blue arrow = Single Select Drop Down, placeholder + corner mark = Auto Populate, empty + corner mark = Multiselect Drop Down, asterisk = mandatory);
   - the manual sentence used;
   - or "blank - not shown in the screen or the manual".
3. List QUESTIONS for that table:
   - unreadable labels;
   - unclear control types;
   - DB rules the manual does not state;
   - drop-down values not visible;
   - fields in the manual but not on the screen, or the reverse;
   - read-only versus editable.
4. Wait for the answers. Update the rows in brs.json, then move on.

**Action-only functions** (a Group/Single function that just runs on the selected records and shows a success message, for example Generate Release Advise):
- UI Design = only the screen with the function menu open (records selected) and the success-message screen. No Query or Data Grid images.
- Fill only 2.2 Event Triggering's: one row for the menu click after selecting records, with the success message in Remarks, and 2.1 as usual (definition + pre-defined conditions). Leave `search` and `display` empty: the 3.1 and 3.2 headings are then left out.

**Always show the edited sheets.** After any image is unmarked, patched or rebuilt, show the review/selection sheet and a before/after crop of each repaired spot before asking anything about the images.

**Ask one question at a time, each with the image or crop it is about.** Commit the crop to the previews folder and show it before asking. Put the proposed text or rows (with their Why: lines) INSIDE the ask_user question itself: text written before the question is not shown to the user (Generate Truck Order 2.2).

**Grow the house rules as documents are made.** When the user settles a new Item Type, Event Type, naming or row-split rule that is not in these files, add it straight away to `references/column-rules.md` or to this file, with the example it came from.

## Step 6 - Event Triggering's
- One row for each button, link, checkbox or toggle in the images that makes something happen. Examples: Submit, Cancel, Process, Generate, Query/Search, Clear, Apply, Overwrite, Next/Previous, a tab click that loads data, a checkbox that enables fields.
- Columns:
  - **Event Type:** "Button Click", "Check Box Click", "Radio Button Click", "Menu Click" (an item in a ☰ Group/Single function menu, for example Generate Release Advise), "Tab Click", "Link Click" or "On Change".
  - **Description:** what happens. Take it from the manual's "How to" steps and from the alert or success-bar text in the images.
  - **Triggered When?:** the user action plus the precondition, for example "User clicks Submit after entering all mandatory fields".
  - **Remarks:** the message shown, quoted from the image. Otherwise blank.
- One button used by several flows (for example Submit for Link, Delink and Edit) can be ONE row: start each part of Description and Remarks with the flow name ("Link: ... Delink: ... Edit: ...") and quote each flow's message (settled on Door Address Link).
- **Events split like the UI Design:** when the images have sections, the user may want 2.2 split the same way. Give each event a `"section"` (same names as the image sections); `brs_docx.py build` then writes a 2.2.1, 2.2.2 ... heading and its own events table per section (settled on Container Redelivery).
- Same Why: lines and questions as Step 5. Wait for the answers.

## Step 7 - Build and check
1. Run `python tools/brs_docx.py build work/brs/<manual>/<fn>/brs.json --out "output/<Module>/BRS - <Module> - <Function> V_1.0.docx"`.
2. Run `python tools/brs_docx.py check <out>`. Compare it with brs.json: cover, history row, blank approval, captions, row counts.
3. References and Assumptions stay as blank headings.
   **Page layout (done by the build; check it in the render):**
   - Real page breaks, no blank-line padding. History of Modifications, Record of Approval and Contents each start a new page.
   - "1. Introduction" starts a new page. Image I is scaled down so that 1, 1.1 Purpose, 1.2 UI Design, the "Image I" caption and the image fit on that one page.
   - Every other image fits one page together with its caption (scaled down if needed).
   - "3. Column Definitions & Business Rules" always starts a new page; 4 References and 5 Assumptions just follow 3.
   - 2.1 text is indented to line up with the 2.2 Event table's edges.
   - Empty headings are removed.
   - Table rows in 2.2, 3.1 and 3.2 never split over two pages, and the header row repeats on every continuation page (Empty Container Admission).
   - Check: render with `soffice --headless --convert-to pdf` and look at every page before handing it over.
4. Tell the user where the file is, in one or two lines. On github.com, commit it in the pull request.
