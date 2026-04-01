# TRCODE Validation for eLogo PDF Downloads

## What & Why
Incorrect `custom_ld_logo_ref_no` can cause downloading wrong document PDFs (e.g., purchase invoices with TRCODE=1) instead of sales invoices/delivery notes (TRCODE=8) from eLogo.

## Change
- **File:** `tiger_integration/api/logo_sync.py`
- **Where:** `download_elogo_document` function, lines 783-787
- **Before:**
```python
if doctype == "Sales Invoice":
    query = "SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(logo_ref_no)s"
elif doctype == "Delivery Note":
    query = "SELECT GUID FROM {STFICHE} WHERE LOGICALREF = %(logo_ref_no)s"
```
- **After:**
```python
if doctype == "Sales Invoice":
    query = "SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(logo_ref_no)s AND TRCODE = 8"
elif doctype == "Delivery Note":
    query = "SELECT GUID FROM {STFICHE} WHERE LOGICALREF = %(logo_ref_no)s AND TRCODE = 8"
```

## Validation
- [ ] Test with valid Sales Invoice (TRCODE=8) - should download successfully
- [ ] Test with invalid Sales Invoice (TRCODE=1) - should return "No record found" error
- [ ] Test with valid Delivery Note (TRCODE=8) - should download successfully
- [ ] Test with invalid Delivery Note (TRCODE!=8) - should return "No record found" error
