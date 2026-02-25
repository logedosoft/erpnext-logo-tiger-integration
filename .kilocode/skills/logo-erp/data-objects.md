# LOGO WCF Data Objects

## Object Mappings

| Index | DataObjectType | Database Table(s) | XML Root | Primary Use |
|-------|----------------|-------------------|----------|-------------|
| 0 | doMaterial | LG_XXX_ITEMS | ITEMS | Material master |
| 1 | doMaterialSlip | LG_XXX_YY_STFICHE + STLINE | MATERIAL_SLIP | Stock movements |
| 18 | doPurchInvoice | LG_XXX_YY_INVOICE + STLINE | INVOICE | Purchase invoices |
| 19 | doSalesInvoice | LG_XXX_YY_INVOICE + STLINE | INVOICE | Sales invoices |
| 30 | doAccountsRP | LG_XXX_CLCARD | CLCARD | Customers/Suppliers |
| 31 | doARAPVoucher | LG_XXX_YY_CLFICHE + CLFLINE | ARP_VOUCHER | AR/AP vouchers |
| 22 | doBank | LG_XXX_BNCARD | BNCARD | Bank master |
| 23 | doBankAccount | LG_XXX_BANKACC | BANKACC | Bank accounts |
| 24 | doBankVoucher | LG_XXX_YY_BNFICHE + BNFLINE | BANK_VOUCHER | Bank transactions |
| 25 | doGLAccount | LG_XXX_EMUHACC | EMUHACC | GL accounts |
| 26 | doGLVoucher | LG_XXX_YY_EMFICHE + EMLINE | GL_VOUCHER | Journal entries |
| 33 | doUnitSet | LG_XXX_UNITSETF + UNITSETL | UNIT_SET | Unit sets |
| 81 | doSalesOrderSlip | LG_XXX_YY_ORFICHE + ORFLINE | ORDER_SLIP | Sales orders |
| 82 | doPurchOrderSlip | LG_XXX_YY_ORFICHE + ORFLINE | ORDER_SLIP | Purchase orders |

---

## Object Details

### 1. doMaterial (0) - ITEMS

**Database:** `LG_XXX_ITEMS`

**Key Fields:**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| CODE | ZString(25) | R | Unique material code |
| NAME | ZString(51) | R | Description |
| CARDTYPE | Integer | R | 1=TM, 10=HM, 12=MM, 20=MS |
| ACTIVE | Integer | R | 0=Active, 1=Passive |
| UNITSETREF | Longint | R | FK to UNITSETF |
| STGRPCODE | ZString(17) | O | Material group |
| PRODUCERCODE | ZString(25) | O | Producer code |
| VAT | Double | O | Default VAT rate |
| TRACKTYPE | Byte | O | 0=None, 1=Lot, 2=Serial |
| SHELFLIFE | Double | O | Shelf life days |

**Related Objects:**
- Parent: doUnitSet (UNITSETREF)
- Child: doMaterialSlip, Invoice lines

**Example XML:**
```xml
<ITEMS>
    <LOGICALREF>0</LOGICALREF>
    <CODE>MAT001</CODE>
    <NAME>Material Item 1</NAME>
    <CARDTYPE>1</CARDTYPE>
    <ACTIVE>0</ACTIVE>
    <UNITSETREF>1234</UNITSETREF>
    <STGRPCODE>A001</STGRPCODE>
    <VAT>18.00</VAT>
</ITEMS>
```

**Validation:**
- CODE: Max 25 chars, alphanumeric, unique
- NAME: Max 51 chars, required
- CARDTYPE: 1, 10, 12, or 20
- UNITSETREF: Must exist in UNITSETF

---

### 2. doAccountsRP (30) - CLCARD

**Database:** `LG_XXX_CLCARD`

**Key Fields:**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| CODE | ZString(17) | R | Unique customer code |
| DEFINITION | ZString(51) | R | Customer name |
| CARDTYPE | Integer | R | 0=Customer, 1=Supplier, 2=Both |
| ACTIVE | Integer | R | 0=Active, 1=Passive |
| ADDR1 | ZString(51) | O | Address line 1 |
| ADDR2 | ZString(51) | O | Address line 2 |
| CITY | ZString(21) | O | City |
| COUNTRY | ZString(21) | O | Country |
| TAXNR | ZString(16) | O | Tax number |
| TAXOFFICE | ZString(16) | O | Tax office |
| EMAILADDR | ZString(31) | O | Email |
| PAYMENTREF | Longint | O | FK to payment plan |

**Related Objects:**
- Parent: doPayPlan (PAYMENTREF)
- Child: Invoice, Order, ARAP transactions

**Example XML:**
```xml
<CLCARD>
    <LOGICALREF>0</LOGICALREF>
    <CODE>CUS001</CODE>
    <DEFINITION>Acme Corporation</DEFINITION>
    <CARDTYPE>0</CARDTYPE>
    <ACTIVE>0</ACTIVE>
    <ADDR1>123 Main Street</ADDR1>
    <CITY>Istanbul</CITY>
    <TAXNR>1234567890</TAXNR>
    <TAXOFFICE>Istanbul VD</TAXOFFICE>
</CLCARD>
```

**Validation:**
- CODE: Max 17 chars, unique
- DEFINITION: Max 51 chars, required
- CARDTYPE: 0, 1, or 2
- TAXNR: 10 digits (Turkey)

---

### 3. doSalesInvoice (19) - INVOICE

**Database:** `LG_XXX_YY_INVOICE` + `LG_XXX_YY_STLINE`

**Key Fields (Header):**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| GRPCODE | Integer | R | 2 for sales |
| TRCODE | Integer | R | 37=Wholesale, 38=Retail, etc. |
| FICHENO | ZString(17) | R | Invoice number |
| DATE | Longint | R | YYYYMMDD format |
| TIME | Longint | O | HHMMss format |
| CLIENTREF | Longint | R | FK to CLCARD |
| SOURCEINDEX | Integer | R | Warehouse number |
| GENEXP1-6 | ZString(51) | O | Description lines |

**Key Fields (Lines):**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| STOCKREF | Longint | R | FK to ITEMS |
| AMOUNT | Double | R | Quantity |
| PRICE | Double | R | Unit price |
| TOTAL | Double | O | Auto-calculated |
| VAT | Double | R | VAT rate |
| VATAMOUNT | Double | O | Auto-calculated |
| LINENO | Integer | O | Auto-assigned |
| LINETYPE | Integer | R | 0=Material, 4=Discount, 5=Surcharge |

**Related Objects:**
- Parent: doAccountsRP (CLIENTREF)
- Parent: doMaterial (STOCKREF)
- Child: doCLFLINE (AR transactions)

**Example XML:**
```xml
<INVOICE>
    <LOGICALREF>0</LOGICALREF>
    <GRPCODE>2</GRPCODE>
    <TRCODE>37</TRCODE>
    <FICHENO>SAT2026-001</FICHENO>
    <DATE>20260216</DATE>
    <TIME>143000</TIME>
    <CLIENTREF>5678</CLIENTREF>
    <SOURCEINDEX>1</SOURCEINDEX>
    <TRANSACTIONS>
        <TRANSACTION>
            <STOCKREF>12345</STOCKREF>
            <AMOUNT>10</AMOUNT>
            <PRICE>100.00</PRICE>
            <VAT>18</VAT>
            <LINETYPE>0</LINETYPE>
        </TRANSACTION>
    </TRANSACTIONS>
</INVOICE>
```

**Validation:**
- GRPCODE: 2 for sales
- TRCODE: Valid sales codes (37, 38, 39, 40, 56)
- DATE: Integer YYYYMMDD (20000101-21001231)
- CLIENTREF: Must exist in CLCARD
- STOCKREF: Must exist in ITEMS
- AMOUNT: > 0
- PRICE: >= 0

---

### 4. doPurchInvoice (18) - INVOICE

**Database:** `LG_XXX_YY_INVOICE` + `LG_XXX_YY_STLINE`

**Key Differences from Sales:**
- GRPCODE: 1 (purchase)
- TRCODE: 31=Purchase, 41=Return, etc.
- IOCODE in STLINE: 1 (input to warehouse)

**Example XML:**
```xml
<INVOICE>
    <LOGICALREF>0</LOGICALREF>
    <GRPCODE>1</GRPCODE>
    <TRCODE>31</TRCODE>
    <FICHENO>ALM2026-001</FICHENO>
    <DATE>20260216</DATE>
    <CLIENTREF>9012</CLIENTREF>
    <SOURCEINDEX>1</SOURCEINDEX>
    <TRANSACTIONS>
        <TRANSACTION>
            <STOCKREF>12345</STOCKREF>
            <AMOUNT>50</AMOUNT>
            <PRICE>80.00</PRICE>
            <VAT>18</VAT>
        </TRANSACTION>
    </TRANSACTIONS>
</INVOICE>
```

---

### 5. doMaterialSlip (1) - STFICHE

**Database:** `LG_XXX_YY_STFICHE` + `LG_XXX_YY_STLINE`

**Key Fields:**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| FICHENO | ZString(9) | R | Voucher number |
| DATE | Longint | R | YYYYMMDD |
| TRCODE | Integer | R | Transaction type |
| IOCODE | Integer | R | 1=In, 2=Out, 3=Transfer |
| SOURCEINDEX | Integer | R | Source warehouse |
| DESTINDEX | Integer | O | Dest warehouse (for transfer) |

**Related Objects:**
- Parent: doMaterial (STOCKREF in lines)

**Example XML:**
```xml
<MATERIAL_SLIP>
    <LOGICALREF>0</LOGICALREF>
    <FICHENO>ST001</FICHENO>
    <DATE>20260216</DATE>
    <TRCODE>1</TRCODE>
    <IOCODE>1</IOCODE>
    <SOURCEINDEX>1</SOURCEINDEX>
    <TRANSACTIONS>
        <TRANSACTION>
            <STOCKREF>12345</STOCKREF>
            <AMOUNT>100</AMOUNT>
            <PRICE>50.00</PRICE>
        </TRANSACTION>
    </TRANSACTIONS>
</MATERIAL_SLIP>
```

---

### 6. doARAPVoucher (31) - CLFICHE

**Database:** `LG_XXX_YY_CLFICHE` + `LG_XXX_YY_CLFLINE`

**Key Fields:**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| FICHENO | ZString(9) | R | Voucher number |
| DATE | Longint | R | YYYYMMDD |
| TRCODE | Integer | R | 1=Collection, 2=Payment, etc. |
| CLIENTREF | Longint | R | FK to CLCARD |
| AMOUNT | Double | R | Transaction amount |
| SIGN | Integer | R | 0=Debit, 1=Credit |

**Example XML:**
```xml
<ARP_VOUCHER>
    <LOGICALREF>0</LOGICALREF>
    <FICHENO>TAH001</FICHENO>
    <DATE>20260216</DATE>
    <TRCODE>1</TRCODE>
    <CLIENTREF>5678</CLIENTREF>
    <TRANSACTIONS>
        <TRANSACTION>
            <AMOUNT>1000.00</AMOUNT>
            <SIGN>1</SIGN>
        </TRANSACTION>
    </TRANSACTIONS>
</ARP_VOUCHER>
```

---

### 7. doUnitSet (33) - UNITSETF

**Database:** `LG_XXX_UNITSETF` + `LG_XXX_UNITSETL`

**Key Fields:**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| CODE | ZString(25) | R | Unit set code |
| NAME | ZString(51) | R | Description |
| MAINUNIT | Integer | R | Main unit index |

**Example XML:**
```xml
<UNIT_SET>
    <LOGICALREF>0</LOGICALREF>
    <CODE>UNIT001</CODE>
    <NAME>Piece/Box/Pallet</NAME>
    <MAINUNIT>0</MAINUNIT>
    <UNITS>
        <UNIT>
            <CODE>PC</CODE>
            <NAME>Piece</NAME>
            <MAINUNIT>1</MAINUNIT>
        </UNIT>
        <UNIT>
            <CODE>BOX</CODE>
            <NAME>Box</NAME>
            <CONVFACT1>12</CONVFACT1>
        </UNIT>
    </UNITS>
</UNIT_SET>
```

---

### 8. doSalesOrderSlip (81) - ORFICHE

**Database:** `LG_XXX_YY_ORFICHE` + `LG_XXX_YY_ORFLINE`

**Key Fields:**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| FICHENO | ZString(9) | R | Order number |
| DATE | Longint | R | YYYYMMDD |
| TRCODE | Integer | R | 81=Received order |
| CLIENTREF | Longint | R | FK to CLCARD |
| STATUS | Integer | O | 0=Open, 1=Closed |

**Example XML:**
```xml
<ORDER_SLIP>
    <LOGICALREF>0</LOGICALREF>
    <FICHENO>SIP001</FICHENO>
    <DATE>20260216</DATE>
    <TRCODE>81</TRCODE>
    <CLIENTREF>5678</CLIENTREF>
    <TRANSACTIONS>
        <TRANSACTION>
            <STOCKREF>12345</STOCKREF>
            <AMOUNT>50</AMOUNT>
            <PRICE>100.00</PRICE>
        </TRANSACTION>
    </TRANSACTIONS>
</ORDER_SLIP>
```

---

### 9. doPurchOrderSlip (82) - ORFICHE

**Key Differences:**
- TRCODE: 82 (placed order to supplier)
- CLIENTREF: Points to supplier (CARDTYPE=1)

---

### 10. doBankVoucher (24) - BNFICHE

**Database:** `LG_XXX_YY_BNFICHE` + `LG_XXX_YY_BNFLINE`

**Key Fields:**
| Field | Type | R/O | Notes |
|-------|------|-----|-------|
| LOGICALREF | Longint | R | PK, 0 for new |
| FICHENO | ZString(9) | R | Voucher number |
| DATE | Longint | R | YYYYMMDD |
| TRCODE | Integer | R | Transaction type |
| BNACCOUNTREF | Longint | R | FK to BANKACC |
| AMOUNT | Double | R | Amount |
| SIGN | Integer | R | 0=Debit, 1=Credit |

---

## Common Conversions

### Database → WCF Object

**Pattern:**
```csharp
// Query database
string sql = "SELECT * FROM LG_001_ITEMS WHERE LOGICALREF = 12345";
DataTable dt = ExecuteQuery(sql);

// Convert to XML
string dataXML = $@"<ITEMS>
    <LOGICALREF>{dt.Rows[0]["LOGICALREF"]}</LOGICALREF>
    <CODE>{dt.Rows[0]["CODE"]}</CODE>
    <NAME>{dt.Rows[0]["NAME"]}</NAME>
    <CARDTYPE>{dt.Rows[0]["CARDTYPE"]}</CARDTYPE>
    <ACTIVE>{dt.Rows[0]["ACTIVE"]}</ACTIVE>
</ITEMS>";
```

### WCF Object → Database Insert

**Pattern:**
```csharp
// Prepare XML
string dataXML = $@"<ITEMS>
    <LOGICALREF>0</LOGICALREF>
    <CODE>{materialCode}</CODE>
    <NAME>{materialName}</NAME>
    <CARDTYPE>1</CARDTYPE>
    <ACTIVE>0</ACTIVE>
    <UNITSETREF>{unitSetRef}</UNITSETREF>
</ITEMS>";

// Insert via WCF
string result = client.InsertDataObject(0, dataXML, paramXML, 1, 0);

// Parse LOGICALREF from result
int newLogicalRef = ExtractLogicalRef(result);
```

### Hierarchical Objects (Invoice)

**Pattern:**
```csharp
string invoiceXML = $@"<INVOICE>
    <LOGICALREF>0</LOGICALREF>
    <GRPCODE>2</GRPCODE>
    <TRCODE>37</TRCODE>
    <CLIENTREF>{clientRef}</CLIENTREF>
    <TRANSACTIONS>
        {string.Join("", lines.Select(l => $@"
        <TRANSACTION>
            <STOCKREF>{l.StockRef}</STOCKREF>
            <AMOUNT>{l.Amount}</AMOUNT>
            <PRICE>{l.Price}</PRICE>
            <VAT>{l.Vat}</VAT>
        </TRANSACTION>"))}
    </TRANSACTIONS>
</INVOICE>";
```

---

## Validation Rules

### Common Rules

| Field | Rule | Example |
|-------|------|---------|
| CODE | Max length, alphanumeric, unique | Max 17-25 chars |
| NAME | Max length, required | Max 51 chars |
| DATE | Integer YYYYMMDD | 20260216 |
| LOGICALREF | 0 for new, >0 for update | 0 or 12345 |
| ACTIVE | 0 or 1 | 0=Active |

### Object-Specific

**doMaterial:**
- CARDTYPE: 1, 10, 12, 20
- UNITSETREF: Must exist
- CODE: Unique within CARDTYPE

**doAccountsRP:**
- CARDTYPE: 0, 1, 2
- TAXNR: 10 digits (Turkey)
- CODE: Unique within firma

**doInvoice:**
- GRPCODE: 1=Purchase, 2=Sales
- TRCODE: Valid for GRPCODE
- CLIENTREF: Must exist in CLCARD
- SOURCEINDEX: Valid warehouse (1-99)
- Lines AMOUNT: > 0
- Lines PRICE: >= 0

**doARAPVoucher:**
- TRCODE: 1-73 (various payment types)
- SIGN: 0=Debit, 1=Credit
- AMOUNT: > 0

### Field Format Constraints

```csharp
// Date validation
public bool IsValidDate(int date) {
    return date >= 19000101 && date <= 21001231 && 
           DateTime.TryParseExact(date.ToString(), "yyyyMMdd", null, 
           DateTimeStyles.None, out _);
}

// Code validation
public bool IsValidCode(string code, int maxLength) {
    return !string.IsNullOrWhiteSpace(code) && 
           code.Length <= maxLength &&
           Regex.IsMatch(code, @"^[a-zA-Z0-9\-_.]+$");
}

// Amount validation
public bool IsValidAmount(double amount, bool allowZero = false) {
    return allowZero ? amount >= 0 : amount > 0;
}
```

---

## Relationship Matrix

| Object | Parent Objects | Child Objects |
|--------|---------------|---------------|
| doMaterial | doUnitSet | Invoice lines, Stock lines |
| doAccountsRP | doPayPlan | Invoice, Orders, ARAP vouchers |
| doSalesInvoice | doAccountsRP, doMaterial | CLFLINE |
| doPurchInvoice | doAccountsRP, doMaterial | CLFLINE |
| doMaterialSlip | doMaterial | - |
| doARAPVoucher | doAccountsRP | - |
| doSalesOrderSlip | doAccountsRP, doMaterial | STLINE (fulfillment) |
| doUnitSet | - | doMaterial |

---

## Quick Reference: Required Fields

| Object | Minimum Required Fields |
|--------|------------------------|
| **doMaterial** | LOGICALREF(0), CODE, NAME, CARDTYPE, ACTIVE, UNITSETREF |
| **doAccountsRP** | LOGICALREF(0), CODE, DEFINITION, CARDTYPE, ACTIVE |
| **doSalesInvoice** | LOGICALREF(0), GRPCODE(2), TRCODE, FICHENO, DATE, CLIENTREF, SOURCEINDEX, Lines[STOCKREF, AMOUNT, PRICE, VAT] |
| **doPurchInvoice** | LOGICALREF(0), GRPCODE(1), TRCODE, FICHENO, DATE, CLIENTREF, SOURCEINDEX, Lines[STOCKREF, AMOUNT, PRICE, VAT] |
| **doMaterialSlip** | LOGICALREF(0), FICHENO, DATE, TRCODE, IOCODE, SOURCEINDEX, Lines[STOCKREF, AMOUNT] |
| **doARAPVoucher** | LOGICALREF(0), FICHENO, DATE, TRCODE, CLIENTREF, Lines[AMOUNT, SIGN] |
| **doUnitSet** | LOGICALREF(0), CODE, NAME, MAINUNIT |
| **doSalesOrderSlip** | LOGICALREF(0), FICHENO, DATE, TRCODE(81), CLIENTREF, Lines[STOCKREF, AMOUNT, PRICE] |

---

## TRCODE Reference

### Invoice TRCODE
| TRCODE | GRPCODE | Type |
|--------|---------|------|
| 31 | 1 | Purchase Invoice |
| 37 | 2 | Wholesale Sales Invoice |
| 38 | 2 | Retail Sales Invoice |
| 39 | 2 | Export Sales Invoice |
| 40 | 2 | Consignment Sales Invoice |
| 41 | 1 | Purchase Return Invoice |
| 56 | 2 | Sales Return Invoice |

### ARAP TRCODE
| TRCODE | Type |
|--------|------|
| 1 | Cash Collection |
| 2 | Cash Payment |
| 3 | Customer Check Collection |
| 4 | Supplier Check Payment |
| 37 | From Sales Invoice |
| 31 | From Purchase Invoice |

### Material Slip TRCODE
| TRCODE | IOCODE | Type |
|--------|--------|------|
| 1 | 1 | Warehouse Entry |
| 2 | 2 | Warehouse Exit |
| 3 | 3 | Warehouse Transfer |

---

## Error Prevention Checklist

- [ ] LOGICALREF = 0 for new records
- [ ] All required fields present
- [ ] DATE in YYYYMMDD integer format
- [ ] Foreign keys (CLIENTREF, STOCKREF) validated
- [ ] TRCODE/GRPCODE combination valid
- [ ] ACTIVE = 0 for active records
- [ ] CODE fields unique
- [ ] AMOUNT > 0 for transactions
- [ ] Warehouse numbers valid (1-99)
- [ ] paramXML includes all required tags
- [ ] XML well-formed (no `<?xml` declaration)