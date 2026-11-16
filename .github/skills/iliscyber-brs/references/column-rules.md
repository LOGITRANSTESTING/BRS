# Column rules (from the house sample BRS - Agency Booking - Accept Release V1.0)

## Search table (3.1)
Columns: UI Item Name | Item Type | UI Validation | DB Validation | Possible Values

## Display Area table (3.2)
Columns: UI Item Name | Item Type | UI Validation | DB Validation | Possible Values | Remarks

## Rows
- **Which items get a row:** every field, grid column, checkbox, toggle and button on the unmarked screen.
- **Order:** screen order, left to right and then top to bottom, panel by panel. Buttons go last.
- **Search:** the read-only header or query part of the screen (for example PR Number, Status, Size Type).
- **Display Area:** the editable detail or grid part (for example Container, the weights, the seals, VGM, then Submit and Cancel).

## UI Item Name
- Use the label exactly as printed, including units in brackets: "Tare Weight(kg)", "Volume(CBM)".
- A panel label in front of field labels becomes a prefix when the sample does that: "VGM UOM", "VGM Status".

## Item Type (decide from the control's look)
These are the house item types, settled by the user on Voyage Update (depot cross booking). Use them unless a screen has something different; ask then.
- Auto Populate: a box with a small corner mark at the bottom right and placeholder text, either "Key in three char" (for example Customer, Allocation Voyage) or "Select ..." (for example Load Terminal, Destination Terminal).
- Single Select Drop Down: a box with a solid blue down-arrow at the right (for example Status = All).
- Alphanumeric / Numeric: a plain empty box with no icon (for example Container No.). Alphanumeric for codes and text, Numeric for numbers only.
- Check Box: a small square, one row for each (for example COPARN Sent, Freeze, Valid ETA, Depot Blank).
- Date and Time Picker: a box with a calendar icon and a clock icon (dd/MM/yyyy HH:mm). A From / To pair joined by "~" under one label (for example "Empty Pickup From / To Date") is ONE row named as the label.
- Multiselect Drop Down: an empty box with only the small corner mark at the bottom right and no placeholder text (for example Status).
- Radio Button: a group of round options where only one can be selected (for example None / Gate Out / Gate In). One row for the group; list the options in Possible Values.
- Toggle: a pill switch (for example Update Related BLs).
- Display Item: a greyed-out box (read-only, for example PR Number, Status, Freeze in Accept Release Basic Information), and grid column values that cannot be edited.
- Swap voyage field (⇆ + two boxes, for example Voyage, Load Voyage): ONE row, Item Type "Auto Populate / Alphanumeric + Single Select Drop Down". The ⇆ switches only the second box between Auto Populate ("Key in three char") and Alphanumeric (plain box). The third box ("Select ... Voyage Port") is always a Single Select Drop Down. Describe this in UI Validation.
- Also, when seen: Button (Submit, Cancel, Apply, Process, Validate); LOV (a box with a magnifier or list icon that opens a lookup); Text Area (a large multi-line box with a note icon, for example Remarks).

## UI Validation (short and imperative, as in the sample)
- Editable text: "Input <what> of the container". Example: "Input Tare Weight of the container".
- Drop down: "Select <what> manually from drop down list".
- Date: "Input <what> date".
- Read-only or derived: "<What> of the selected PR". Examples: "Status of the selected PR", "Container Type Size of the PR".
- Auto-filled: "Based on selected <X>, <Y> will auto populate".
- Check box: "If <condition> please select the check box".
- Button: what it does. Examples: "Cancelled all the input values and requery existing data"; "After input all the mandatory column values, it should be inserted into <tables> for the selected PR".
- Mandatory: when the label has a red asterisk, start with "Mandatory. ".

## DB Validation
- Fill it only from what the manual or the user says about what is saved or checked: table names, duplicates, status changes.
- Otherwise leave it blank and add a question.

## Possible Values
- Fill it only with values you can see: drop-down entries, statuses, Y/N, toggle on/off. Example: Status = Prepared / Supplied / Full Return / Cancelled / Empty Return / Freeze.
- If the drop-down is closed on every screenshot, leave it blank and ask the user.

## Remarks (Display Area only)
- Use it for notes from the manual that fit no other column. Examples: "Disabled until Container is entered", "Greyed out (dd/MM/yyyy placeholder)".

## Sample rows (house style)
| UI Item Name | Item Type | UI Validation |
|---|---|---|
| PR Number | Text Item | Selected PR Number Details |
| Empty Pickup Date | Date Picker | Empty Pickup Date for the PR |
| Actual Container Type | Text Item | Based on selected Container number Type size will auto populate |
| Container Status | Drop Down | Select Container Status manually from drop down list |
| Over Weight | Check Box | If container is over weight Pl select the check box |
| Submit | Button | After input all the mandatory columns value's, it should be inserted into Cargo containers & PR Details for the selected PR |
| Cancel | Button | Cancelled all the input values and requery existing data |

## brs.json keys
- `search_title` / `display_title` (optional): rename the 3.1 / 3.2 headings. Use it when the 3.1 part is the screen's edit header rather than query fields, for example Accept Release: "Cross Booking Depot Activity Edit Fields".
- `drop_display: true`: remove the whole 3.2 section. Use it when only the editing area is documented: put its rows in 3.1 (named with `search_title`) and leave out the read-only header. Example: Accept Release keeps only the Containers fields, under "Cross Booking Depot Activity Edit Fields".
- `search` rows: name, type, ui, db, values
- `display` rows: name, type, ui, db, values, remarks
- `events` rows: event_type, description, triggered_when, remarks
