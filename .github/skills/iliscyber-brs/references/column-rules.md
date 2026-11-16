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
- Text Item: a plain input box, or a grey read-only box showing a value.
- Date Picker: a calendar icon. A date and time pair with a clock icon is still one "Date Picker" row, unless the time has its own label.
- Drop Down: a down-arrow at the right of the box.
- Check Box: a small square.
- Toggle: a pill switch. Ask the user whether to call it Toggle or Check Box.
- Button: a clickable button (Submit, Cancel, Apply, Process).
- LOV: a box with a magnifier or list icon that opens a lookup.
- Text Area: a large multi-line box with a note icon (Remarks).
- Display Item: grid column values that cannot be edited. Ask if unsure.

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
- `search` rows: name, type, ui, db, values
- `display` rows: name, type, ui, db, values, remarks
- `events` rows: event_type, description, triggered_when, remarks
