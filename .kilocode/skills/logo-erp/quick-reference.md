# LOGO ERP Integration Cheat Sheet

## WCF Methods (Top 5)

```csharp
// 1. Insert
client.InsertDataObject(dataObjectType, dataXML, paramXML, firma, period);

// 2. Update
client.UpdateDataObject(dataObjectType, dataXML, paramXML, firma, period);

// 3. Read Single
client.ReadDataObject(dataObjectType, logicalRef, paramXML, firma, period);

// 4. Read Multiple
client.ReadDataObjects(dataObjectType, filterXML, paramXML, firma, period);

// 5. Calculate (no save)
client.CalculateDataObject(dataObjectType, dataXML, paramXML, firma, period);
```

---

## Critical Tables

| Table | PK | Naming | Example |
|-------|----|----|---------|
| **LGITEMS** | LOGICALREF | `LG_XXX_ITEMS` | `LG_001_ITEMS` (no period) |
| **LGCLCARD** | LOGICALREF | `LG_XXX_CLCARD` | `LG_001_CLCARD` (no period) |
| **LGINVOICE** | LOGICALREF | `LG_XXX_YY_INVOICE` | `LG_001_01_INVOICE` |
| **LGSTLINE** | LOGICALREF | `LG_XXX_YY_STLINE` | `LG_001_01_STLINE` |
| **LGCLFLINE** | LOGICALREF | `LG_XXX_YY_CLFLINE` | `LG_001_01_CLFLINE` |

**Pattern:** XXX=Firma(001-999), YY=Period(00-99)

---

## Authentication Setup

```csharp
// Windows Auth (RECOMMENDED)
var binding = new BasicHttpBinding();
binding.Security.Mode = BasicHttpSecurityMode.TransportCredentialOnly;
binding.Security.Transport.ClientCredentialType = HttpClientCredentialType.Windows;
binding.MaxReceivedMessageSize = 2147483647;
var client = new LogoObjectServiceClient(binding, 
    new EndpointAddress("http://192.168.1.10:8010/Logo/Tiger/LogoObjectService.svc"));
client.ClientCredentials.Windows.ClientCredential = 
    new NetworkCredential("user", "pass", "DOMAIN");
```

---

## DataObjectTypes (Top 5)

| Index | Type | Use |
|-------|------|-----|
| **0** | doMaterial | Material cards |
| **19** | doSalesInvoice | Sales invoices |
| **30** | doAccountsRP | Customers/Suppliers |
| **18** | doPurchInvoice | Purchase invoices |
| **81** | doSalesOrderSlip | Sales orders |

---

## paramXML Template

```xml
<?xml version="1.0" encoding="utf-16"?>
<Parameters>
    <ReplicMode>0</ReplicMode>
    <CheckParams>1</CheckParams>
    <CheckRight>1</CheckRight>
    <ApplyCampaign>0</ApplyCampaign>
    <Validation>1</Validation>
    <Period>0</Period>
</Parameters>
```

---

## Common SQL Patterns

```sql
-- Material stock
SELECT i.CODE, inv.ONHAND FROM LG_001_ITEMS i
LEFT JOIN LG_001_01_INVDEF inv ON i.LOGICALREF = inv.ITEMREF
WHERE i.CODE = 'MAT001' AND i.ACTIVE = 0;

-- Customer balance
SELECT cl.CODE, SUM(CASE WHEN clf.SIGN=0 THEN clf.AMOUNT ELSE -clf.AMOUNT END) AS Balance
FROM LG_001_CLCARD cl
INNER JOIN LG_001_01_CLFLINE clf ON cl.LOGICALREF = clf.CLIENTREF
WHERE cl.CODE = 'CUS001' GROUP BY cl.CODE;

-- Invoice lines
SELECT inv.FICHENO, stl.LINENO, i.CODE, stl.AMOUNT, stl.PRICE
FROM LG_001_01_INVOICE inv
INNER JOIN LG_001_01_STLINE stl ON inv.LOGICALREF = stl.INVOICEREF
INNER JOIN LG_001_ITEMS i ON stl.STOCKREF = i.LOGICALREF
WHERE inv.FICHENO = 'INV001';
```

---

## 5 AUTHENTICATION GOTCHAS

| # | Issue | Solution |
|---|-------|----------|
| 1 | **401 Unauthorized** | Verify domain in `NetworkCredential("user", "pass", "DOMAIN")` |
| 2 | **Endpoint not found** | Check port 8010 (HTTP) or 8011 (HTTPS), firewall rules |
| 3 | **Request timeout** | Increase `binding.SendTimeout = TimeSpan.FromMinutes(10)` |
| 4 | **Message too large** | Set `binding.MaxReceivedMessageSize = 2147483647` |
| 5 | **SSL/TLS errors** | Use HTTP (8010) not HTTPS or install cert |

---

## 5 INTEGRATION GOTCHAS

| # | Issue | Solution |
|---|-------|----------|
| 1 | **"Duplicate CODE"** | Query existing before insert; generate unique codes |
| 2 | **"LOGICALREF not found"** | Always query foreign keys first (`CLIENTREF`, `STOCKREF`) |
| 3 | **paramXML parse error** | Remove `<?xml version...?>` from dataXML; keep in paramXML |
| 4 | **"CheckParams failed"** | Set `<CheckParams>1</CheckParams>` to bypass warehouse validation |
| 5 | **"Invalid TRCODE"** | Verify TRCODE/GRPCODE combo (31→GRPCODE=1, 37→GRPCODE=2) |

---

## 5 DATABASE GOTCHAS

| # | Issue | Solution |
|---|-------|----------|
| 1 | **ACTIVE confusion** | `ACTIVE=0` means ACTIVE, `ACTIVE=1` means PASSIVE |
| 2 | **DATE format** | Use integer `20260216` NOT string `'2026-02-16'` |
| 3 | **Period tables** | Must include period: `LG_001_01_STLINE` not `LG_001_STLINE` |
| 4 | **LOGICALREF for new** | Always set `LOGICALREF=0` for INSERT, >0 for UPDATE |
| 5 | **Missing firma prefix** | All tables need `LG_XXX_` prefix except global (`L_CAPIDDEF`) |

---

## Insert Material (Complete Example)

```csharp
string dataXML = @"<ITEMS>
    <LOGICALREF>0</LOGICALREF>
    <CODE>MAT001</CODE>
    <NAME>Test Material</NAME>
    <CARDTYPE>1</CARDTYPE>
    <ACTIVE>0</ACTIVE>
    <UNITSETREF>1234</UNITSETREF>
</ITEMS>";

string paramXML = @"<?xml version=""1.0"" encoding=""utf-16""?>
<Parameters>
    <ReplicMode>0</ReplicMode>
    <CheckParams>1</CheckParams>
    <CheckRight>1</CheckRight>
    <Validation>1</Validation>
    <Period>0</Period>
</Parameters>";

string result = client.InsertDataObject(0, dataXML, paramXML, 1, 0);
// Extract LOGICALREF from <RESULT><LOGICALREF>12345</LOGICALREF></RESULT>
```

---

## Insert Sales Invoice (Complete Example)

```csharp
string dataXML = @"<INVOICE>
    <LOGICALREF>0</LOGICALREF>
    <GRPCODE>2</GRPCODE>
    <TRCODE>37</TRCODE>
    <FICHENO>SAT2026-001</FICHENO>
    <DATE>20260216</DATE>
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
</INVOICE>";

string result = client.InsertDataObject(19, dataXML, paramXML, 1, 1);
```

---

## TRCODE Quick Reference

| TRCODE | GRPCODE | Type | MODULENR |
|--------|---------|------|----------|
| **31** | 1 | Purchase Invoice | 4 |
| **37** | 2 | Wholesale Sales Invoice | 4 |
| **1** | - | Cash Collection | 5 |
| **2** | - | Cash Payment | 5 |
| **81** | - | Received Order | 3 |
| **82** | - | Placed Order | 3 |

---

## Error Code Quick Fix

| Code | Error | Fix |
|------|-------|-----|
| **1002** | Duplicate CODE | Generate unique code or query first |
| **1005** | Foreign key violation | Query `CLIENTREF`/`STOCKREF` exists |
| **1006** | CheckParams failed | `<CheckParams>1</CheckParams>` |
| **2001** | XML parse error | Check XML syntax, remove `<?xml` from dataXML |
| **3002** | Timeout | Reduce batch size, increase timeout |

---

## Field Types

| LOGO Type | C# Type | SQL Type | Example |
|-----------|---------|----------|---------|
| Longint | int | INT | LOGICALREF, DATE |
| Integer | short | SMALLINT | TRCODE, ACTIVE |
| Byte | byte | TINYINT | IOCODE |
| Double | double | FLOAT | AMOUNT, PRICE |
| ZString(N) | string | VARCHAR(N) | CODE, NAME |

---

## Required Fields Checklist

**Material:**
- LOGICALREF(0), CODE, NAME, CARDTYPE, ACTIVE, UNITSETREF

**Customer:**
- LOGICALREF(0), CODE, DEFINITION, CARDTYPE, ACTIVE

**Invoice:**
- LOGICALREF(0), GRPCODE, TRCODE, FICHENO, DATE, CLIENTREF, SOURCEINDEX
- Lines: STOCKREF, AMOUNT, PRICE, VAT

---

## Validation Rules

```csharp
// Date: YYYYMMDD integer
int date = 20260216;  // ✅ Correct
string date = "2026-02-16";  // ❌ Wrong

// LOGICALREF
LOGICALREF = 0;  // ✅ New record
LOGICALREF = 12345;  // ✅ Update existing

// ACTIVE
ACTIVE = 0;  // ✅ Active record
ACTIVE = 1;  // ✅ Passive record

// CODE uniqueness
// Query before insert: SELECT COUNT(*) FROM LG_001_ITEMS WHERE CODE = 'MAT001'
```

---

## Troubleshooting Checklist

- [ ] Endpoint URL correct (IP:8010/Logo/Tiger/LogoObjectService.svc)
- [ ] Credentials valid (user/pass/domain)
- [ ] Firewall allows port 8010
- [ ] Table name includes firma/period (`LG_001_01_STLINE`)
- [ ] LOGICALREF = 0 for new records
- [ ] Foreign keys exist (CLIENTREF, STOCKREF)
- [ ] DATE in integer YYYYMMDD format
- [ ] ACTIVE = 0 for active records
- [ ] TRCODE/GRPCODE valid combination
- [ ] paramXML includes all required tags
- [ ] dataXML well-formed (no `<?xml` declaration)
- [ ] MaxReceivedMessageSize = 2147483647

---

**URL:** `http://<IP>:8010/Logo/Tiger/LogoObjectService.svc`  
**Ports:** HTTP=8010, HTTPS=8011  
**Primary Key:** All tables use `LOGICALREF`  
**New Record:** `LOGICALREF = 0`  
**Date Format:** Integer `20260216`  
**Active Status:** `ACTIVE = 0`