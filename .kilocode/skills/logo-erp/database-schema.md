# LOGO ERP Database Schema

## Core Tables

### 1. LG_XXX_ITEMS (Materials)
**Naming:** `LG_[FIRMA]_ITEMS` (no period)

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| CODE | ZString | 25 | Kod | Code | **UK, Required** |
| NAME | ZString | 51 | Açıklama | Description | **Required** |
| CARDTYPE | Integer | 2 | Tür | Type | 1=TM, 10=HM, 12=MM, 20=MS |
| ACTIVE | Integer | 2 | Durum | Status | 0=Active, 1=Passive |
| UNITSETREF | Longint | 4 | Birim Seti | Unit Set | **FK→LGUNITSETF** |
| VAT | Double | 8 | KDV | VAT | |
| TRACKTYPE | Byte | 1 | İzleme | Tracking | 0=None, 1=Lot, 2=Serial |

**Indexes:** LOGICALREF(UK), CODE(UK), NAME(D)

---

### 2. LG_XXX_CLCARD (Customers/Suppliers)
**Naming:** `LG_[FIRMA]_CLCARD` (no period)

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| CODE | ZString | 17 | Kod | Code | **UK, Required** |
| DEFINITION | ZString | 51 | Ünvan | Title | **Required** |
| CARDTYPE | Integer | 2 | Tür | Type | 0=Customer, 1=Supplier, 2=Both |
| ACTIVE | Integer | 2 | Durum | Status | 0=Active, 1=Passive |
| TAXNR | ZString | 16 | Vergi No | Tax Number | |
| TAXOFFICE | ZString | 16 | Vergi Dairesi | Tax Office | |
| PAYMENTREF | Longint | 4 | Ödeme Planı | Payment Plan | **FK→LGPAYPLANS** |

**Indexes:** LOGICALREF(UK), CODE(UK), DEFINITION(D)

---

### 3. LG_XXX_YY_INVOICE (Invoices)
**Naming:** `LG_[FIRMA]_[PERIOD]_INVOICE`

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| GRPCODE | Integer | 2 | Grup | Group | 1=Purchase, 2=Sales |
| TRCODE | Integer | 2 | Hareket | Transaction | 31-44, 56 |
| FICHENO | ZString | 17 | Fiş No | Voucher Number | **Required** |
| DATE | Longint | 4 | Tarih | Date | **YYYYMMDD** |
| CLIENTREF | Longint | 4 | Cari | AR/AP | **FK→LGCLCARD** |
| SOURCEINDEX | Integer | 2 | Ambar | Warehouse | |
| NETTOTAL | Double | 8 | Net | Net Total | |
| TOTALVAT | Double | 8 | KDV | VAT Total | |

**Indexes:** LOGICALREF(UK), GRPCODE+TRCODE+FICHENO(UK), DATE+TRCODE(D)

---

### 4. LG_XXX_YY_STLINE (Material Transactions)
**Naming:** `LG_[FIRMA]_[PERIOD]_STLINE`

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| STOCKREF | Longint | 4 | Malzeme | Material | **FK→LGITEMS** |
| CLIENTREF | Longint | 4 | Cari | AR/AP | **FK→LGCLCARD** |
| INVOICEREF | Longint | 4 | Fatura | Invoice | **FK→LGINVOICE** |
| IOCODE | Integer | 2 | Giriş/Çıkış | I/O Type | 1=In, 2=Out, 3=Transfer |
| TRCODE | Integer | 2 | Hareket | Transaction | |
| DATE | Longint | 4 | Tarih | Date | **YYYYMMDD** |
| SOURCEINDEX | Integer | 2 | Ambar | Warehouse | |
| AMOUNT | Double | 8 | Miktar | Quantity | |
| PRICE | Double | 8 | Fiyat | Price | |
| TOTAL | Double | 8 | Toplam | Total | |
| VAT | Double | 8 | KDV | VAT Rate | |
| LINENO | Integer | 2 | Satır | Line Number | |

**Indexes:** LOGICALREF(UK), TRCODE+DATE+INVOICEREF(D), STOCKREF+DATE+IOCODE(D)

---

### 5. LG_XXX_YY_CLFLINE (AR/AP Transactions)
**Naming:** `LG_[FIRMA]_[PERIOD]_CLFLINE`

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| CLIENTREF | Longint | 4 | Cari | AR/AP | **FK→LGCLCARD** |
| SOURCEFREF | Longint | 4 | Kaynak Fiş | Source Voucher | **FK→multi** |
| DATE | Longint | 4 | Tarih | Date | **YYYYMMDD** |
| TRCODE | Integer | 2 | Hareket | Transaction | |
| MODULENR | Integer | 2 | Modül | Module | 4=Invoice, 5=Voucher, 7=Bank |
| SIGN | Integer | 2 | İşaret | Sign | 0=Debit, 1=Credit |
| AMOUNT | Double | 8 | Tutar | Amount | |

**Indexes:** LOGICALREF(UK), CLIENTREF+DATE+MODULENR+TRCODE(D)

---

### 6. LG_XXX_YY_ORFICHE (Orders)
**Naming:** `LG_[FIRMA]_[PERIOD]_ORFICHE`

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| FICHENO | ZString | 9 | Fiş No | Voucher Number | **Required** |
| DATE | Longint | 4 | Tarih | Date | **YYYYMMDD** |
| TRCODE | Integer | 2 | Hareket | Transaction | 81=Received, 82=Placed |
| CLIENTREF | Longint | 4 | Cari | AR/AP | **FK→LGCLCARD** |
| STATUS | Integer | 2 | Durum | Status | 0=Open, 1=Closed |

---

### 7. LG_XXX_YY_ORFLINE (Order Lines)
**Naming:** `LG_[FIRMA]_[PERIOD]_ORFLINE`

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| ORDFICHEREF | Longint | 4 | Sipariş Fişi | Order Voucher | **FK→LGORFICHE** |
| STOCKREF | Longint | 4 | Malzeme | Material | **FK→LGITEMS** |
| AMOUNT | Double | 8 | Miktar | Quantity | |
| PRICE | Double | 8 | Fiyat | Price | |
| CLOSED | Integer | 2 | Kapalı | Closed | 0=Open, 1=Closed |

---

### 8. LG_XXX_YY_INVDEF (Warehouse Stock)
**Naming:** `LG_[FIRMA]_[PERIOD]_INVDEF`

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| ITEMREF | Longint | 4 | Malzeme | Material | **FK→LGITEMS** |
| INVENNO | Integer | 2 | Ambar | Warehouse | |
| ONHAND | Double | 8 | Eldeki | On Hand | Current stock |
| RESERVED | Double | 8 | Rezerve | Reserved | |
| AVAILABLE | Double | 8 | Kullanılabilir | Available | ONHAND - RESERVED |

---

### 9. LG_XXX_YY_STFICHE (Material Vouchers)
**Naming:** `LG_[FIRMA]_[PERIOD]_STFICHE`

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| FICHENO | ZString | 9 | Fiş No | Voucher Number | **Required** |
| DATE | Longint | 4 | Tarih | Date | **YYYYMMDD** |
| TRCODE | Integer | 2 | Hareket | Transaction | |
| IOCODE | Integer | 2 | Giriş/Çıkış | I/O Type | 1=In, 2=Out |
| CLIENTREF | Longint | 4 | Cari | AR/AP | **FK→LGCLCARD** |

---

### 10. LG_XXX_UNITSETF (Unit Sets)
**Naming:** `LG_[FIRMA]_UNITSETF` (no period)

| Field | Type | Size | TR | EN | Notes |
|-------|------|------|----|----|-------|
| **LOGICALREF** | Longint | 4 | Log. Ref. | Logical Reference | **PK** |
| CODE | ZString | 25 | Kod | Code | **UK, Required** |
| NAME | ZString | 51 | Açıklama | Description | **Required** |
| MAINUNIT | Integer | 2 | Ana Birim | Main Unit | |

---

## Common Joins

### 1. Material + Stock
```sql
SELECT i.CODE, i.NAME, inv.INVENNO, inv.ONHAND, inv.AVAILABLE
FROM LG_001_ITEMS i
LEFT JOIN LG_001_01_INVDEF inv ON i.LOGICALREF = inv.ITEMREF
WHERE i.ACTIVE = 0 AND inv.INVENNO = 1;
```

### 2. Invoice + Customer + Lines
```sql
SELECT inv.FICHENO, cl.CODE, stl.LINENO, i.CODE, stl.AMOUNT, stl.TOTAL
FROM LG_001_01_INVOICE inv
INNER JOIN LG_001_CLCARD cl ON inv.CLIENTREF = cl.LOGICALREF
INNER JOIN LG_001_01_STLINE stl ON inv.LOGICALREF = stl.INVOICEREF
INNER JOIN LG_001_ITEMS i ON stl.STOCKREF = i.LOGICALREF
WHERE inv.FICHENO = 'INV2026-001';
```

### 3. Customer Balance
```sql
SELECT cl.CODE, clf.DATE, clf.AMOUNT,
    SUM(CASE WHEN clf.SIGN = 0 THEN clf.AMOUNT ELSE -clf.AMOUNT END) 
        OVER (PARTITION BY cl.LOGICALREF ORDER BY clf.DATE) AS Balance
FROM LG_001_CLCARD cl
INNER JOIN LG_001_01_CLFLINE clf ON cl.LOGICALREF = clf.CLIENTREF
WHERE cl.CODE = 'CUS001' AND clf.DATE >= 20260101;
```

### 4. Material Movement
```sql
SELECT stl.DATE, i.CODE, stl.IOCODE, stl.SOURCEINDEX, stl.AMOUNT, cl.CODE
FROM LG_001_01_STLINE stl
INNER JOIN LG_001_ITEMS i ON stl.STOCKREF = i.LOGICALREF
LEFT JOIN LG_001_CLCARD cl ON stl.CLIENTREF = cl.LOGICALREF
WHERE i.CODE = 'MAT001' AND stl.DATE >= 20260101;
```

### 5. Order Fulfillment
```sql
SELECT orf.FICHENO, cl.CODE, i.CODE, orl.AMOUNT, 
    ISNULL(SUM(stl.AMOUNT), 0) AS Delivered,
    orl.AMOUNT - ISNULL(SUM(stl.AMOUNT), 0) AS Remaining
FROM LG_001_01_ORFICHE orf
INNER JOIN LG_001_CLCARD cl ON orf.CLIENTREF = cl.LOGICALREF
INNER JOIN LG_001_01_ORFLINE orl ON orf.LOGICALREF = orl.ORDFICHEREF
INNER JOIN LG_001_ITEMS i ON orl.STOCKREF = i.LOGICALREF
LEFT JOIN LG_001_01_STLINE stl ON orl.LOGICALREF = stl.SOURCELINK
WHERE orf.TRCODE = 81 AND orl.CLOSED = 0
GROUP BY orf.FICHENO, cl.CODE, i.CODE, orl.AMOUNT;
```

### 6. Invoice-ARAP Link
```sql
SELECT inv.FICHENO, cl.CODE, inv.NETTOTAL, clf.AMOUNT
FROM LG_001_01_INVOICE inv
INNER JOIN LG_001_CLCARD cl ON inv.CLIENTREF = cl.LOGICALREF
INNER JOIN LG_001_01_CLFLINE clf ON inv.LOGICALREF = clf.SOURCEFREF AND clf.MODULENR = 4
WHERE inv.FICHENO = 'SAT2026-001';
```

### 7. Material + Units
```sql
SELECT i.CODE, us.CODE, ul.CODE, ul.MAINUNIT, iu.CONVFACT1
FROM LG_001_ITEMS i
INNER JOIN LG_001_UNITSETF us ON i.UNITSETREF = us.LOGICALREF
INNER JOIN LG_001_UNITSETL ul ON us.LOGICALREF = ul.UNITSETREF
LEFT JOIN LG_001_ITMUNITA iu ON i.LOGICALREF = iu.ITEMREF AND ul.LOGICALREF = iu.UNITLINEREF
WHERE i.CODE = 'MAT001';
```

---

## Performance Notes

### Index Usage
**✅ DO:**
- Filter by LOGICALREF (primary key)
- Use CODE for lookups (indexed)
- Filter DATE + TRCODE (compound index)
- Use ACTIVE = 0 for master data
- Query firma/period aware

**❌ AVOID:**
- Query NAME without CODE (slower)
- Full scan on STLINE, CLFLINE without DATE
- `LIKE '%value%'` on indexed fields
- Join on non-indexed fields
- No WHERE on large tables

### Optimizations

**Large Tables:**
```sql
-- ❌ BAD
SELECT * FROM LG_001_01_STLINE WHERE STOCKREF = 12345;

-- ✅ GOOD
SELECT * FROM LG_001_01_STLINE 
WHERE STOCKREF = 12345 AND DATE >= 20260101 AND DATE <= 20261231;
```

**Balance Queries:**
```sql
-- ✅ Use totals table
SELECT * FROM LG_001_01_CLTOTFIL WHERE CARDREF = 12346 AND YEAR = 2026;
```

**Stock Balance:**
```sql
-- ✅ Use INVDEF (current balance)
SELECT ONHAND, AVAILABLE FROM LG_001_01_INVDEF WHERE ITEMREF = 12345;
```

### Field Formats
| Field | Format | Example |
|-------|--------|---------|
| DATE | Integer YYYYMMDD | 20260216 |
| TIME | Integer HHMMss | 143052 |
| LOGICALREF | Longint | 12345 (0 for new) |
| CODE | ZString | 'MAT001' (trimmed) |
| ACTIVE | Integer | 0=Active, 1=Passive |

### Pitfalls
| Issue | Impact | Fix |
|-------|--------|-----|
| No period suffix | Query fails | Use `LG_XXX_YY_` for period tables |
| String DATE compare | Type mismatch | Use integer: `DATE >= 20260101` |
| SELECT * on STLINE | Heavy I/O | Select needed columns only |
| No LOGICALREF in UPDATE | Full scan | Always `WHERE LOGICALREF = value` |

### Query Patterns
**Counting:**
```sql
SELECT COUNT(*) FROM LG_001_01_STLINE WHERE DATE >= 20260101 AND SOURCEINDEX = 1;
```

**Pagination:**
```sql
SELECT * FROM LG_001_01_STLINE 
WHERE DATE = 20260216 AND LOGICALREF > @LastRef
ORDER BY LOGICALREF OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY;
```

### Relationships
```
LGITEMS → LGINVDEF, LGSTLINE, LGUNITSETF
LGCLCARD → LGINVOICE, LGCLFLINE, LGORFICHE
LGINVOICE → LGSTLINE, LGCLFLINE
```

### Table Suffixes
- No suffix: Firm-level (ITEMS, CLCARD, UNITSETF)
- `_YY` suffix: Period-specific (STLINE, INVOICE, CLFLINE)
- Global: System (L_CAPIDDEF, no firma)