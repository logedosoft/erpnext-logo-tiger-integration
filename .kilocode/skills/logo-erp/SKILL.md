# LOGO ERP Integration Skill

## When to Use
- Reading/writing LOGO Tiger database tables
- Calling Logo Object Service WCF endpoints
- Working with firma/dönem structures
- Mapping DataObjectTypes
- Handling TRCODE/MODULENR codes
- Debugging XML-based transfers

## Key Conventions

### Table Naming
| Pattern | Example | Usage |
|---------|---------|-------|
| `LG_XXX_YY_TABLE` | `LG_001_01_STLINE` | Firm 001, Period 01 |
| `LG_XXX_TABLE` | `LG_001_CLCARD` | Firm 001, no period |
| `L_TABLE` | `L_CAPIDDEF` | Global system |

- XXX = Firma (000-999)
- YY = Period (00-99)
- Case-sensitive, no spaces

### Primary Keys
- All tables use `LOGICALREF` (Longint, 4 bytes)
- New record: `LOGICALREF = 0`
- Update: `LOGICALREF = <existing value>`

### Date Format
- Type: `Longint` in YYYYMMDD format
- Example: 2026-02-16 → `20260216`

### TRCODE Mapping
| TRCODE | MODULENR | Type (TR) | Type (EN) |
|--------|----------|-----------|-----------|
| 31 | 4 | Satınalma Faturası | Purchase Invoice |
| 37 | 4 | Toptan Satış Faturası | Wholesale Sales Invoice |
| 1 | 5 | Nakit Tahsilat | Cash Collection |
| 81 | 3 | Alınan Sipariş | Received Order |
| 82 | 3 | Verilen Sipariş | Placed Order |

### DataObjectTypes
| Index | Type | Turkish | Usage |
|-------|------|---------|-------|
| 0 | doMaterial | Malzeme | Material cards |
| 18 | doPurchInvoice | Alım Faturası | Purchase invoices |
| 19 | doSalesInvoice | Satış Faturası | Sales invoices |
| 30 | doAccountsRP | Cari Kart | Customer/Supplier |
| 31 | doARAPVoucher | Cari Fiş | AR/AP vouchers |

### Authentication
```csharp
var binding = new BasicHttpBinding();
binding.Security.Mode = BasicHttpSecurityMode.TransportCredentialOnly;
binding.Security.Transport.ClientCredentialType = HttpClientCredentialType.Windows;
var client = new LogoObjectServiceClient(binding, endpoint);
client.ClientCredentials.Windows.ClientCredential = new NetworkCredential("user", "pass", "DOMAIN");
```

## Critical Rules

### Validation Safety
| Setting | Risk | When |
|---------|------|------|
| Validation=1 | 🟢 Safe | Production (default) |
| Validation=0 | 🔴 High | Development only |
| CheckParams=1 | 🟡 Moderate | Multi-warehouse |
| CheckRight=1 | 🟡 Moderate | System integration |

### Required Fields
**LGITEMS:**
- LOGICALREF (0 for new), CODE, NAME, CARDTYPE, UNITSETREF

**LGCLCARD:**
- LOGICALREF (0 for new), CODE, DEFINITION, CARDTYPE

**LGINVOICE:**
- LOGICALREF (0 for new), GRPCODE, TRCODE, FICHENO, DATE, CLIENTREF

### Forbidden Operations
❌ Never:
- Query without firma/period
- Use approximate table names
- Assume LOGICALREF without query
- Mix TRCODE/MODULENR incorrectly
- Skip paramXML tags
- Use Validation=0 in production

✅ Always:
- Verify table names exactly
- Query foreign keys before insert
- Use complete paramXML
- Validate TRCODE combinations
- Use YYYYMMDD for dates

## Example Patterns

### Pattern 1: Query Material + Stock
```sql
SELECT 
    i.CODE, i.NAME, inv.INVENNO, inv.ONHAND, inv.AVAILABLE
FROM LG_001_ITEMS i
LEFT JOIN LG_001_01_INVDEF inv ON i.LOGICALREF = inv.ITEMREF
WHERE i.CODE = 'MAT001' AND i.ACTIVE = 0;
```

### Pattern 2: Insert Customer
```csharp
string dataXML = @"<CLCARD>
    <LOGICALREF>0</LOGICALREF>
    <CODE>CUS001</CODE>
    <DEFINITION>Acme Corp</DEFINITION>
    <CARDTYPE>0</CARDTYPE>
    <ACTIVE>0</ACTIVE>
</CLCARD>";

string paramXML = @"<?xml version=""1.0"" encoding=""utf-16""?>
<Parameters>
    <ReplicMode>0</ReplicMode>
    <CheckParams>1</CheckParams>
    <CheckRight>1</CheckRight>
    <Validation>1</Validation>
    <Period>0</Period>
</Parameters>";

string result = client.InsertDataObject(30, dataXML, paramXML, 1, 0);
```

### Pattern 3: Create Invoice
```csharp
string dataXML = @"<INVOICE>
    <LOGICALREF>0</LOGICALREF>
    <GRPCODE>2</GRPCODE>
    <TRCODE>37</TRCODE>
    <FICHENO>INV2026-001</FICHENO>
    <DATE>20260216</DATE>
    <CLIENTREF>12346</CLIENTREF>
    <SOURCEINDEX>1</SOURCEINDEX>
    <TRANSACTIONS>
        <TRANSACTION>
            <STOCKREF>12345</STOCKREF>
            <AMOUNT>10</AMOUNT>
            <PRICE>100</PRICE>
            <VAT>18</VAT>
        </TRANSACTION>
    </TRANSACTIONS>
</INVOICE>";

string result = client.InsertDataObject(19, dataXML, paramXML, 1, 1);
```

## Common Pitfalls
| Pitfall | Solution |
|---------|----------|
| Table not found | Use `LG_XXX_YY_TABLE` with firma/period |
| Date format error | Use integer YYYYMMDD (20260216) |
| Foreign key fails | Query LOGICALREF of parent first |
| XML error | Remove `<?xml version...?>` from dataXML |
| ACTIVE confusion | 0=Active, 1=Passive |

## Quick Reference

### Field Types
| LOGO | C# | SQL | Example |
|------|----|----|---------|
| Longint | int | INT | LOGICALREF, DATE |
| Integer | short | SMALLINT | TRCODE |
| Byte | byte | TINYINT | ACTIVE |
| Double | double | FLOAT | AMOUNT, PRICE |
| ZString(N) | string | VARCHAR(N) | CODE, NAME |

### paramXML Values
| Parameter | 0 | 1 |
|-----------|---|---|
| ReplicMode | System sets | Override system |
| CheckParams | Validate warehouse | Skip validation |
| Validation | Skip validation | Full validation ✅ |
| ApplyCampaign | No campaign | Apply campaigns |

### Integration Checklist
- [ ] Table name: LG_XXX_YY_ format
- [ ] Foreign key LOGICALREFs queried
- [ ] TRCODE/MODULENR valid
- [ ] LOGICALREF=0 for new
- [ ] DATE in YYYYMMDD format
- [ ] Complete paramXML
- [ ] DataObjectType correct
- [ ] Field types match schema
- [ ] ACTIVE=0 for active records