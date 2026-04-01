# Fix Sales Invoice Naming Series Issue

## What & Why
The sales_invoice.json file contains property_setters that override the naming series on production server during migration, breaking the production naming scheme.

## Change
- **File:** `tiger_integration/logo_tiger_integration/custom/sales_invoice.json`
- **Where:** Lines 748-793 (two property_setters for naming_series)
- **Before:**
```json
   {
    "_assign": null,
    "_comments": null,
    "_liked_by": null,
    "_user_tags": null,
    "creation": "2026-02-03 18:37:23.706743",
    "default_value": null,
    "doc_type": "Sales Invoice",
    "docstatus": 0,
    "doctype_or_field": "DocField",
    "field_name": "naming_series",
    "idx": 0,
    "is_system_generated": 1,
    "modified": "2026-02-03 18:37:23.706743",
    "modified_by": "Administrator",
    "module": null,
    "name": "Sales Invoice-naming_series-default",
    "owner": "Administrator",
    "property": "default",
    "property_type": "Text",
    "row_name": null,
    "value": "ACC-.SINV-.YYYY-.#####"
   },
   {
    "_assign": null,
    "_comments": null,
    "_liked_by": null,
    "_user_tags": null,
    "creation": "2026-02-03 18:37:23.619464",
    "default_value": null,
    "doc_type": "Sales Invoice",
    "docstatus": 0,
    "doctype_or_field": "DocField",
    "field_name": "naming_series",
    "idx": 0,
    "is_system_generated": 1,
    "modified": "2026-02-03 18:37:23.619464",
    "modified_by": "Administrator",
    "module": null,
    "name": "Sales Invoice-naming_series-options",
    "owner": "Administrator",
    "property": "options",
    "property_type": "Text",
    "row_name": null,
    "value": "ACC-.SINV-.YYYY-.#####"
   },
```
- **After:** (removed entirely)

## Validation
- [ ] Verify the two naming_series property_setters are removed
- [ ] Verify other property_setters remain intact
- [ ] Verify the file is still valid JSON
