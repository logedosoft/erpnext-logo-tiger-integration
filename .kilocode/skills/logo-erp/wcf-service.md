# LOGO Object WCF Service

## Base Configuration

### Endpoints
- Format: `http://<SERVER>:<PORT>/Logo/<PRODUCT>/LogoObjectService.svc`
- HTTP: 8010 (Tiger), 8020 (Netsis), 8030 (J4)
- HTTPS: 8011, 8021, 8031
- Example: `http://192.168.1.10:8010/Logo/Tiger/LogoObjectService.svc`

### Authentication

**Windows (Recommended):**
```csharp
var binding = new BasicHttpBinding();
binding.Security.Mode = BasicHttpSecurityMode.TransportCredentialOnly;
binding.Security.Transport.ClientCredentialType = HttpClientCredentialType.Windows;
binding.MaxReceivedMessageSize = 2147483647;

var client = new LogoObjectServiceClient(binding, endpoint);
client.ClientCredentials.Windows.ClientCredential = new NetworkCredential("user", "pass", "DOMAIN");
```

**Basic:**
```csharp
binding.Security.Transport.ClientCredentialType = HttpClientCredentialType.Basic;
client.ClientCredentials.UserName.UserName = "logouser";
client.ClientCredentials.UserName.Password = "logopass";
```

---

## Methods

### 1. InsertDataObject
```csharp
string InsertDataObject(int dataObjectType, string dataXML, string paramXML, int firma, int period);
```

**Example:**
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
```

**Output:**
```xml
<RESULT>
    <LOGICALREF>12345</LOGICALREF>
    <STATUS>SUCCESS</STATUS>
</RESULT>
```

---

### 2. UpdateDataObject
```csharp
string UpdateDataObject(int dataObjectType, string dataXML, string paramXML, int firma, int period);
```

**Example:**
```csharp
string dataXML = @"<ITEMS>
    <LOGICALREF>12345</LOGICALREF>
    <CODE>MAT001</CODE>
    <NAME>Updated Name</NAME>
    <VAT>20.00</VAT>
</ITEMS>";

string result = client.UpdateDataObject(0, dataXML, paramXML, 1, 0);
```

---

### 3. DeleteDataObject
```csharp
string DeleteDataObject(int dataObjectType, int logicalRef, int firma, int period);
```

**Example:**
```csharp
string result = client.DeleteDataObject(0, 12345, 1, 0);
```

---

### 4. ReadDataObject
```csharp
string ReadDataObject(int dataObjectType, int logicalRef, string paramXML, int firma, int period);
```

**Example:**
```csharp
string paramXML = @"<?xml version=""1.0"" encoding=""utf-16""?>
<Parameters><ExportAllData>1</ExportAllData><Period>0</Period></Parameters>";

string result = client.ReadDataObject(0, 12345, paramXML, 1, 0);
```

---

### 5. ReadDataObjects
```csharp
string ReadDataObjects(int dataObjectType, string filterXML, string paramXML, int firma, int period);
```

**Example:**
```csharp
string filterXML = @"<FILTER>
    <ACTIVE>0</ACTIVE>
    <STGRPCODE>A001</STGRPCODE>
</FILTER>";

string result = client.ReadDataObjects(0, filterXML, paramXML, 1, 0);
```

**Output:**
```xml
<DATA_OBJECTS>
    <ITEMS><LOGICALREF>12345</LOGICALREF><CODE>MAT001</CODE></ITEMS>
    <ITEMS><LOGICALREF>12346</LOGICALREF><CODE>MAT002</CODE></ITEMS>
</DATA_OBJECTS>
```

---

### 6. CalculateDataObject
```csharp
string CalculateDataObject(int dataObjectType, string dataXML, string paramXML, int firma, int period);
```

**Example:**
```csharp
string dataXML = @"<INVOICE>
    <GRPCODE>2</GRPCODE>
    <TRCODE>37</TRCODE>
    <CLIENTREF>5678</CLIENTREF>
    <TRANSACTIONS>
        <TRANSACTION>
            <STOCKREF>12345</STOCKREF>
            <AMOUNT>10</AMOUNT>
            <PRICE>100.00</PRICE>
            <VAT>18</VAT>
        </TRANSACTION>
    </TRANSACTIONS>
</INVOICE>";

string paramXML = @"<Parameters>
    <ApplyCampaign>1</ApplyCampaign>
    <GetStockLinePrice>8</GetStockLinePrice>
    <Validation>0</Validation>
</Parameters>";

string result = client.CalculateDataObject(19, dataXML, paramXML, 1, 0);
```

---

### 7. GetDataObjectCount
```csharp
int GetDataObjectCount(int dataObjectType, string filterXML, int firma, int period);
```

**Example:**
```csharp
string filterXML = @"<FILTER><ACTIVE>0</ACTIVE><CARDTYPE>0</CARDTYPE></FILTER>";
int count = client.GetDataObjectCount(30, filterXML, 1, 0);
```

---

### 8. ExecuteSQL
```csharp
string ExecuteSQL(string sqlQuery, int firma, int period);
```

**Example:**
```csharp
string sql = @"SELECT i.CODE, inv.ONHAND 
    FROM LG_001_ITEMS i 
    INNER JOIN LG_001_01_INVDEF inv ON i.LOGICALREF = inv.ITEMREF 
    WHERE i.ACTIVE = 0";

string result = client.ExecuteSQL(sql, 1, 1);
```

⚠️ **Security:** Never use user input directly. Validate/sanitize all queries.

---

### 9. GetFirmaPeriodList
```csharp
string GetFirmaPeriodList();
```

**Output:**
```xml
<FIRMA_PERIODS>
    <FIRMA>
        <NR>1</NR>
        <NAME>ABC Ltd.</NAME>
        <PERIODS>
            <PERIOD><NR>1</NR><BEGDATE>20260101</BEGDATE><ACTIVE>1</ACTIVE></PERIOD>
        </PERIODS>
    </FIRMA>
</FIRMA_PERIODS>
```

---

### 10. GetDataObjectTypes
```csharp
string GetDataObjectTypes();
```

**Output:**
```xml
<DATA_OBJECT_TYPES>
    <TYPE><INDEX>0</INDEX><NAME>doMaterial</NAME><DESCRIPTION>Malzeme</DESCRIPTION></TYPE>
    <TYPE><INDEX>19</INDEX><NAME>doSalesInvoice</NAME><DESCRIPTION>Satış Faturası</DESCRIPTION></TYPE>
</DATA_OBJECT_TYPES>
```

---

### 11. ValidateDataObject
```csharp
string ValidateDataObject(int dataObjectType, string dataXML, string paramXML, int firma, int period);
```

**Output:**
```xml
<!-- Valid -->
<RESULT><STATUS>VALID</STATUS></RESULT>

<!-- Invalid -->
<RESULT>
    <STATUS>INVALID</STATUS>
    <ERRORS>
        <ERROR>TAXNR format invalid</ERROR>
    </ERRORS>
</RESULT>
```

---

### 12. GetNextCode
```csharp
string GetNextCode(int dataObjectType, string codeTemplate, int firma, int period);
```

**Example:**
```csharp
string nextCode = client.GetNextCode(0, "MAT####", 1, 0);  // Returns: MAT0001
```

**Templates:**
- `MAT####` → MAT0001
- `CUS-####` → CUS-0001
- `INV######` → INV000001

---

### 13. ImportDataObjects
```csharp
string ImportDataObjects(int dataObjectType, string dataXML, string paramXML, int firma, int period);
```

**Example:**
```csharp
string dataXML = @"<ITEMS_LIST>
    <ITEMS><LOGICALREF>0</LOGICALREF><CODE>MAT001</CODE><NAME>Item 1</NAME></ITEMS>
    <ITEMS><LOGICALREF>0</LOGICALREF><CODE>MAT002</CODE><NAME>Item 2</NAME></ITEMS>
</ITEMS_LIST>";

string result = client.ImportDataObjects(0, dataXML, paramXML, 1, 0);
```

**Output:**
```xml
<IMPORT_RESULT>
    <TOTAL>2</TOTAL>
    <SUCCESS>2</SUCCESS>
    <FAILED>0</FAILED>
</IMPORT_RESULT>
```

---

### 14. GetVersion
```csharp
string GetVersion();
```

**Output:**
```xml
<VERSION>
    <PRODUCT>LOGO Tiger</PRODUCT>
    <VERSION>5.02.15</VERSION>
</VERSION>
```

---

### 15. CheckConnection
```csharp
bool CheckConnection(int firma, int period);
```

**Example:**
```csharp
bool isConnected = client.CheckConnection(1, 0);
```

---

## Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 1001 | LOGICALREF not found | Verify exists before update/delete |
| 1002 | Duplicate CODE | Use unique value |
| 1003 | Required field missing | Check mandatory fields |
| 1004 | Invalid TRCODE/MODULENR | Verify combination |
| 1005 | Foreign key violation | Ensure referenced LOGICALREF exists |
| 1006 | CheckParams failed | Set `<CheckParams>1</CheckParams>` |
| 1007 | CheckRight denied | Set `<CheckRight>1</CheckRight>` |
| 1008 | Validation error | Review formats, types |
| 1009 | Period closed | Use open period |
| 1010 | Warehouse error | Verify SOURCEINDEX |
| 2001 | XML parse error | Check syntax |
| 2002 | paramXML missing tag | Include ALL tags |
| 2003 | Invalid DataObjectType | Use valid index 0-140 |
| 2004 | Auth failed | Verify credentials |
| 2005 | Endpoint unreachable | Check IP, port, firewall |
| 3001 | DB connection lost | Retry |
| 3002 | Timeout | Reduce batch size |
| 3003 | Deadlock | Retry after delay |
| 4001 | VAT calculation error | Verify VAT fields |
| 4003 | Campaign failed | Check campaign dates |
| 5001 | SeriLot missing | Provide or disable |
| 5002 | Stock insufficient | Check INVDEF.ONHAND |

### Error Handling
```csharp
try {
    string result = client.InsertDataObject(type, dataXML, paramXML, 1, 0);

    if (result.Contains("<STATUS>ERROR</STATUS>")) {
        string error = ExtractError(result);

        if (error.Contains("Duplicate")) {
            // Handle 1002
        } else if (error.Contains("CheckParams")) {
            // Handle 1006: Set CheckParams=1
        }
    }
}
catch (FaultException<LogoFault> ex) {
    Console.WriteLine($"Logo Error: {ex.Detail.Message}");
}
catch (TimeoutException) {
    Console.WriteLine("Timeout: Reduce batch size");
}
```

---

## Rate Limits

| Type | Value | Notes |
|------|-------|-------|
| Requests/min | 60 | Configurable |
| Concurrent connections | 10 | Per IP |
| Max message size | 2 GB | Binding config |
| Timeout | 60s | Default |
| Max array items | 65536 | Bulk operations |

### Configuration
```csharp
binding.SendTimeout = TimeSpan.FromMinutes(10);
binding.ReceiveTimeout = TimeSpan.FromMinutes(10);
binding.MaxReceivedMessageSize = 2147483647;
binding.MaxBufferSize = 2147483647;
binding.ReaderQuotas.MaxDepth = 32;
binding.ReaderQuotas.MaxStringContentLength = 2147483647;
binding.ReaderQuotas.MaxArrayLength = 2147483647;
```

### Throttling
```csharp
public async Task ImportBatch(List<MaterialData> materials) {
    int batchSize = 50;
    int delayMs = 1000;

    for (int i = 0; i < materials.Count; i += batchSize) {
        var batch = materials.Skip(i).Take(batchSize);
        string dataXML = Serialize(batch);
        client.ImportDataObjects(0, dataXML, paramXML, 1, 0);

        if (i + batchSize < materials.Count) 
            await Task.Delay(delayMs);
    }
}
```

### Retry Pattern
```csharp
public async Task<string> InsertWithRetry(string dataXML) {
    int maxRetries = 3;
    int delayMs = 1000;

    for (int attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return client.InsertDataObject(0, dataXML, paramXML, 1, 0);
        }
        catch (TimeoutException) when (attempt < maxRetries - 1) {
            await Task.Delay(delayMs * (int)Math.Pow(2, attempt));
        }
    }
    throw new Exception("Failed after retries");
}
```

---

## DataObjectType Reference

| Index | Type | TR | EN | Usage |
|-------|------|----|----|-------|
| 0 | doMaterial | Malzeme | Material | Material cards |
| 18 | doPurchInvoice | Alış Faturası | Purchase Invoice | Purchase |
| 19 | doSalesInvoice | Satış Faturası | Sales Invoice | Sales |
| 30 | doAccountsRP | Cari Kart | Customer/Supplier | AR/AP |
| 31 | doARAPVoucher | Cari Fiş | AR/AP Voucher | Payment |
| 22 | doBank | Banka | Bank | Bank master |
| 24 | doBankVoucher | Banka Fişi | Bank Voucher | Bank transactions |
| 25 | doGLAccount | Muhasebe | GL Account | Chart of accounts |
| 26 | doGLVoucher | Muhasebe Fişi | GL Voucher | Journal entries |
| 33 | doUnitSet | Birim Seti | Unit Set | UOM |

---

## Checklist
- [ ] Endpoint URL (IP, port, product)
- [ ] Credentials (user, pass, domain)
- [ ] Firewall port 8010/8011
- [ ] Logo service running
- [ ] Firma/period valid
- [ ] MaxReceivedMessageSize configured
- [ ] Timeout appropriate
- [ ] paramXML complete
- [ ] dataXML well-formed
- [ ] LOGICALREF correct