# BRS progress - EMS - Help Manual depot

Manual: manuals/EMS_-_Help_Manual_depot.gui (copy of the user's upload)
Plan: work/brs/EMS_Help_Manual_depot/plan.json (21 functions, all new)
Branch: brs-skill-update (PR #4)
Author: Appsara

## Log
- 17.11.2026 - Skill updated from brs_skill_update-1.zip; author fixed to Appsara; progress log rule added.
- 17.11.2026 - Ran brs_plan.py plan on the manual: 6 Group + 15 Single functions, all new.
- 17.11.2026 - Cover module line: "ILISCyber - EMS - Depot Activity". Starting function 1 (Group) Empty Return Pre Advise; exported to group_empty_return_pre_advise/pages.
- 17.11.2026 - Fn 1 images built: img/01.png = menu step (How_to_..._91e2_01): menu area from page image ab64_01 (twin), record strips from ../group_generate_truck_order Generate_Truck_Order_d619_01 at dy+1 (rows 361-363, 391-393, circle x21-52, x1504), scrollbar x1505-1508 at dy0; gate 0 outside, only app ☰ icon red left. img/02.png = success screen (91e2_02), frame only. Sheet + before/after in output/previews/brs_EMS_Help_Manual_depot_group_empty_return_pre_advise/. Functions 2-6 also exported (used as donors).
- 17.11.2026 - Donor rules: added the scrolling-grid recipe and the copy-whole-rectangle warning.
- 17.11.2026 - Images I/II approved. Settled: Purpose is always "This document explains the purpose of EMS's Depot Activity <Function> details." only; the manual's definition goes first in 2.1; empty 3.1/3.2 are left out with their headings, heading 3 stays (brs_docx.py extended, skill updated). Module set to "EMS – Depot Activity" (cover: ILISCyber – EMS – Depot Activity).
- 17.11.2026 - Fn 1 built: output/EMS/BRS - EMS - Depot Activity - Empty Return Pre Advise V_1.0.docx (2.1 two items, 2.2 one Menu Click row approved).
- 17.11.2026 - Fn 1 approved by user; brs_plan.py done recorded (01.01).
- 17.11.2026 - Layout fixes (user): page breaks for History/Approval/Contents/1/3, Image I fits page with 1/1.1/1.2, images kept with captions, 2.1 indented to the 2.2 table, empty headings removed (brs_docx.py layout(), skill Step 7). Fn 1 rebuilt (8 pages) - approved by user.
- 17.11.2026 - Fn 2 Generate Release Advise: Image I = menu step repaired from its twin (page image), gate passed; Image II = success screen, frame only. Images approved.
- 17.11.2026 - Fn 2: 2.1 (definition + 2 conditions) and 2.2 (1 Menu Click row) approved; built output/EMS/BRS - EMS - Depot Activity - Generate Release Advise V_1.0.docx (8 pages). Approved; brs_plan done recorded (01.01).
- 17.11.2026 - Fn 3 TOPS XML: user chose the page image (6-item menu) for Image I; no twin, rebuilt by part swaps from the Generate Release Advise page image (menu at +3,-35 cut around letters; Generate Truck Order item at +3,-3; left shadow +3,-5; check box column +3,-3) and same-screen shadow/margin; gate passed. Image II = success screen, frame only.
- 17.11.2026 - Fn 3: 2.1 (definition + 1 condition) and 2.2 (1 Menu Click row) approved; built output/EMS/BRS - EMS - Depot Activity - TOPS XML V_1.0.docx (8 pages). Approved; brs_plan done recorded (01.01).
- 17.11.2026 - Fn 4 Generate Truck Order: Image I = menu step repaired from its twin (page image), gate passed with 0 px differing from the twin; Image II = success screen, frame only. Awaiting image OK.
- 17.11.2026 - Fn 4: images approved; 2.1 approved (definition + 7 conditions, item 7 sub-conditions as a) to i) lines); 2.2 Menu Click row approved. Built output/EMS/BRS - EMS - Depot Activity - Generate Truck Order V_1.0.docx (9 pages); a)-i) lines indented one step (brs_docx layout). Awaiting document OK.
- 17.11.2026 - Fn 4 approved; brs_plan done recorded.
- 17.11.2026 - Fn 5 Empty Container Admission (opens own screen, needs 3.1/3.2). User chose images: I = menu (clean page image), II = empty screen S2 with S3 query values pasted in (dates + Activity Place), III = S5 selected+Process repaired from S4 (gate passed), IV = S6 success. Awaiting image OK.
- 17.11.2026 - Fn 5: images approved; 1.1 + 2.1 (overview + 2 conditions) approved; 2.2 six rows approved (Menu Click, Search, Process, Excel, Refresh, Expand/Collapse). brs.json saved.
- 17.11.2026 - Fn 5: 3.1 approved (7 rows, DB/values blank); headings: "Empty Container Admission - Query Screen" (3.1) and "Empty Container Admission - Data Grid" (3.2).
- 17.11.2026 - Fn 5: 3.2 Data Grid approved (11 rows). Built output/EMS/BRS - EMS - Depot Activity - Empty Container Admission V_1.0.docx (14 pages). brs_docx layout now: table rows cantSplit + header repeat. Awaiting document OK.
- 17.11.2026 - Fn 5 approved; brs_plan done recorded.
- 17.11.2026 - Fn 6 Confirmation: Image I = menu step repaired from twin page image (gate passed, 0 px from twin); Image II = success screen, frame only. Awaiting image OK.
- 17.11.2026 - Fn 6: images, 2.1 (overview only, no conditions), 2.2 Menu Click approved. Built output/EMS/BRS - EMS - Depot Activity - Confirmation V_1.0.docx. Awaiting document OK.
- 17.11.2026 - Fn 6 approved; brs_plan done recorded. Fn 7 Booking Query (Single) exported to single_booking_query/.
- 17.11.2026 - Fn 7 Booking Query: Image I = menu step repaired from twin page image (gate passed); Image II = Booking Query screen (unmarked, frame only). Awaiting image OK.
- 17.11.2026 - Fn 7: images approved; 2.1 overview only; 2.2 seven rows (Menu Click, section Tab Click, Expand All, Collapse All, Refresh, Show Less, Show More); 3.x left empty (read-only screen, user choice). Built output/EMS/BRS - EMS - Depot Activity - Booking Query V_1.0.docx. Awaiting document OK.
- 17.11.2026 - Fn 7 approved; brs_plan done recorded. Fn 8 Accept Release (Single) exported to single_accept_release/.
- NEXT: fn 8 Accept Release - read pages, images.
