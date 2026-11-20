# DCSA eBK BRS progress
Source: SDS - DCSA eBK V03.01.docx. One BRS per SDS UC sub-topic; files = the 19 "BRS - DCSA eBK - <name> V 1.0.docx" in repo root. Go UC-wise; user says what to do when something is missing.
- 20.11.2026 | UC1 View Request | Step 1 images: doc has 5 unmarked screenshots (scan: unmarked); SDS has 6 older ones (not used). Sheet at output/previews/brs_DCSA_eBK_view_request/sheet.png | Next: user OK on images, then 2.1/2.2/3.x tables.
- 20.11.2026 | Decision | One BRS per UC (9 docs), sub-topics = sub-sections. Name: "BRS - DCSA eBK - UC<n> - <UC name> V 1.0.docx". Base = user's DCSA doc (Reject Request) via brs.json "template"; new brs_docx.py option "module_line" = "DCSA – eBK Process".
- 20.11.2026 | UC1 | Step 1 images: 22 screenshots from the 8 sub-topic docs (all unmarked by scan; black highlight boxes present). Meta Query has none. Sheets: output/previews/brs_DCSA_eBK_uc1/src_*.png | Next: user OK on image list.
- 20.11.2026 UC1 images: black boxes on buttons 3_2, 6_2, 6_3 repaired (0 black left, 0 px changed outside outline) - preview output/previews/brs_DCSA_eBK_uc1/fix_buttons.png. Pending: 1_1, 5_3.
- 20.11.2026 User rule: when a BRS has many functions, each function gets its own sub-title (1.2.x images, 2.1.x features, 2.2.x events, 3.x tables). CONFIRMED by user: apply in all sections; 3.x = one numbered sub-title per function.
- 20.11.2026 UC1 images: 1_1 rebuilt (menu edge from 3_1/4_1 at matched offsets; ~40 icon-under-shadow pixels computed from a shadow model fitted on visible pixels, max err 2) - preview fix_1_1.png. 5_3 rebuilt (popup edge + shadow from a rounded-shadow model fitted on 380 visible pixels, max err 3; corner pixels mirrored from the visible opposite corners) - preview fix_5_3.png. All 22 UC1 images now in uc1/img, 0 black boxes left. Sheet: output/previews/brs_DCSA_eBK_uc1/sheet.png - waiting for user OK. Button repairs redone (right edge had been filled from the neighbouring button; now from the toolbar gap).
- 20.11.2026 USER DECISION: use all screenshots as given, WITH their black markings - no image changes. UC1 BRS uses work/brs/DCSA eBK/uc1/src/*.png. (img/ repairs kept only for reference.)

- Builder: 2.1.x feature sub-titles + heading-only 1.2.x entries (Meta Query) added and tested. DCSA template has no captions -> images placed without captions (same as user's DCSA docs).
- uc1/brs.json created: 22 marked src images under 1.2.1–1.2.8, 2.1.1–2.1.8 verbatim. Next: 2.2 events per function.
- 2.2.1 View Request events approved (6 rows).
- 2.2.2 Meta Query: 1 row (Menu Click) approved.
- 2.2.3 Edit Request events approved (5 rows).
- 2.2.4 Validate QC events approved (5 rows).
- 2.2.5 Create Booking events approved (4 rows).
- 2.2.6 Edit Booking events approved (6 rows).
- 2.2.7 Communication History events approved (4 rows).
- 2.2.8 Timeline events approved (3 rows). 2.2 complete. Next: 3.x tables per function.
- 3.x structure: Option A approved (3.x per function, 3.x.y per tab/pop-up; Meta Query heading + 'No screen design available'). Builder: new 'tables' key (tested).
- 3.1.1 View Request – Basic Information approved (33 rows, grouped rows split).
- 3.1.2 Sailing approved (22 rows).
- 3.1.3 Containers & Cargo approved (39 rows).
- 3.1.4 Parties & Addresses approved (12 rows).
- 3.1.5 Communication History approved (11 rows, DB = DOC HEADER).
- 3.1.6 Notes approved (8 rows). 3.2 Meta Query = heading + 'No screen design available.'
