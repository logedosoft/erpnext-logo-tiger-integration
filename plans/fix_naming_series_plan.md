# Fix Delivery Note Naming Series Issue

## What & Why
The delivery_note.json file contains property_setters that override the naming series on production server during migration, breaking the production naming scheme.

## Change
- **File:** `tiger_integration/logo_tiger_integration/custom/delivery_note.json`
- **Where:** Lines 942-987 (two property_setters for naming_series)
- **Before:**
```json
   {
    "_assign": null,
    "_comments": null,
    "_liked_by": null,
    "_user_tags": null,
    "creation": "2026-03-26 11:36:11.323767",
    "default_value": null,
    "doc_type": "Delivery Note",
    "docstatus": 0,
    "doctype_or_field": "DocField",
    "field_name": "naming_series",
    "idx": 0,
    "is_system_generated": 1,
    "modified": "2026-03-26 11:36:11.323767",
    "modified_by": "Administrator",
    "module": null,
    "name": "Delivery Note-naming_series-default",
    "owner": "Administrator",
    "property": "default",
    "property_type": "Text",
    "row_name": null,
    "value": "SEVK.YY..MM..DD.#########"
   },
   {
    "_assign": null,
    "_comments": null,
    "_liked_by": null,
    "_user_tags": null,
    "creation": "2026-03-26 11:36:11.040451",
    "default_value": null,
    "doc_type": "Delivery Note",
    "docstatus": 0,
    "doctype_or_field": "DocField",
    "field_name": "naming_series",
    "idx": 0,
    "is_system_generated": 1,
    "modified": "2026-03-26 11:36:11.040451",
    "modified_by": "Administrator",
    "module": null,
    "name": "Delivery Note-naming_series-options",
    "owner": "Administrator",
    "property": "options",
    "property_type": "Text",
    "row_name": null,
    "value": "SEVK.YY..MM..DD.#########"
   },
```
- **After:** (removed entirely)

## Validation
- [ ] Verify the two naming_series property_setters are removed
- [ ] Verify other property_setters remain intact
- [ ] Verify the file is still valid JSON
