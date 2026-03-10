# -*- coding: utf-8 -*-
# LOGEDOSOFT

import frappe, json
from frappe import msgprint, _

from frappe.model.document import Document
from frappe.utils import cint, flt


import requests
from bs4 import BeautifulSoup
import html
import pymssql

def get_logo_xml(doctype, docLObjectServiceSettings):
	#Gets info from LOGO Object Service Settings -> Mappings table
	dctResult = frappe._dict({
		"op_result": False,
		"op_message": "",
		"xml_template": "",
		"parameter_xml": ""
	})

	for xml_template in docLObjectServiceSettings.logo_xml_templates:
		if xml_template.document_type == doctype:
			dctResult.op_result = True
			dctResult.xml_template = xml_template.logo_xml_template
			if xml_template.parameter_xml:
				dctResult.parameter_xml = xml_template.parameter_xml
			elif docLObjectServiceSettings.default_parameter_xml:
				dctResult.parameter_xml = xml_template.parameter_xml
			else:
				dctResult.parameter_xml = """
<Parameters>
  <ReplicMode>0</ReplicMode>
  <CheckParams>1</CheckParams>
  <CheckRight>1</CheckRight>
  <ApplyCampaign>1</ApplyCampaign>
  <ApplyCondition>1</ApplyCondition>
  <FillAccCodes>1</FillAccCodes>
  <FormSeriLotLines>0</FormSeriLotLines>
  <GetStockLinePrice>0</GetStockLinePrice>
  <ExportAllData>1</ExportAllData>
  <Validation>0</Validation>
  <CheckApproveDate>0</CheckApproveDate>
  <Period>01</Period>
</Parameters>
"""
	if dctResult.op_result == False and doctype == "Item":
		dctResult.op_result = True
		dctResult.xml_template = """<soapenv:Envelope 
	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
	xmlns:tem="http://tempuri.org/">
   <soapenv:Header/>
   <soapenv:Body>
	  <tem:AppendDataObject>
		 <tem:dataType>{{ doc.logo_dataType }}</tem:dataType>
		 <tem:dataReference>0</tem:dataReference>
		 <tem:dataXML>
			<![CDATA[<ITEMS>
  {% set dctUnitSet = get_logo_mapping_for("UOM", doc.stock_uom, throw_exception = True) %}
  <ITEM DBOP="INS">
	<CARD_TYPE>1</CARD_TYPE>
	<CODE>{{ doc.name }}</CODE>
	<NAME>{{ doc.item_name }}</NAME>
	<GROUP_CODE>{{ doc.item_group }}</GROUP_CODE>
	<PRODUCER_CODE></PRODUCER_CODE>
	<AUXIL_CODE></AUXIL_CODE>
	<AUTH_CODE></AUTH_CODE>
	<USEF_PURCHASING>1</USEF_PURCHASING>
	<USEF_SALES>1</USEF_SALES>
	<USEF_MM>1</USEF_MM>
	<VAT>{{ doc.logo_tax_rate }}</VAT>
	<AUTOINCSL>1</AUTOINCSL>
	<LOTS_DIVISIBLE>1</LOTS_DIVISIBLE>
	<UNITSET_CODE>{{ dctUnitSet.logo_code }}</UNITSET_CODE>
	<DIST_LOT_UNITS>1</DIST_LOT_UNITS>
	<COMB_LOT_UNITS>1</COMB_LOT_UNITS>
	<UNITS>
	  {% set logo_units = get_logo_units_for_unit_set(dctUnitSet.logo_code) %}
	  {% for unit in logo_units %}
	  <UNIT>
		<UNIT_CODE>{{ unit.CODE }}</UNIT_CODE>
		<USEF_MTRLCLASS>1</USEF_MTRLCLASS>
		<USEF_PURCHCLAS>1</USEF_PURCHCLAS>
		<USEF_SALESCLAS>1</USEF_SALESCLAS>
		<CONV_FACT1>{{ unit.CONVFACT1 }}</CONV_FACT1>
		<CONV_FACT2>{{ unit.CONVFACT2 }}</CONV_FACT2>
	  </UNIT>
	  {% endfor %}
	</UNITS>
	<MULTI_ADD_TAX>0</MULTI_ADD_TAX>
	<PACKET>0</PACKET>
	<SELVAT>{{ doc.logo_tax_rate }}</SELVAT>
	<RETURNVAT>{{ doc.logo_tax_rate }}</RETURNVAT>
	<SELPRVAT>{{ doc.logo_tax_rate }}</SELPRVAT>
	<RETURNPRVAT>{{ doc.logo_tax_rate }}</RETURNPRVAT>
	<MARKCODE></MARKCODE>
	<AUXIL_CODE2></AUXIL_CODE2>
	<AUXIL_CODE3></AUXIL_CODE3>
	<AUXIL_CODE4>{{ doc.brand or '' }}</AUXIL_CODE4>
	<AUXIL_CODE5>{{ doc.custom_manufacturer or '' }}</AUXIL_CODE5>
	<UPDATECHILDS>1</UPDATECHILDS>
  </ITEM>
</ITEMS>]]>
		 </tem:dataXML>

		 <tem:paramXML>
		 <![CDATA[{{ parameterXML }}]]>
		 </tem:paramXML>
		 <tem:FirmNr>{{ docLObjectServiceSettings.logo_company_no or '1' }}</tem:FirmNr>
		 <tem:securityCode>{{ docLObjectServiceSettings.lobject_service_client_secret }}</tem:securityCode>
		 </tem:AppendDataObject>
		 </soapenv:Body>
</soapenv:Envelope>"""
		dctResult.parameter_xml = """
<Parameters>
  <ReplicMode>0</ReplicMode>
  <CheckParams>1</CheckParams>
  <CheckRight>1</CheckRight>
  <ApplyCampaign>1</ApplyCampaign>
  <ApplyCondition>1</ApplyCondition>
  <FillAccCodes>1</FillAccCodes>
  <FormSeriLotLines>0</FormSeriLotLines>
  <GetStockLinePrice>0</GetStockLinePrice>
  <ExportAllData>1</ExportAllData>
  <Validation>0</Validation>
  <CheckApproveDate>0</CheckApproveDate>
  <Period>01</Period>
</Parameters>"""
	if dctResult.op_result == False and doctype == "Customer":
		dctResult.op_result = True
		dctResult.xml_template = """<soapenv:Envelope
	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
	xmlns:tem="http://tempuri.org/">
   <soapenv:Header/>
   <soapenv:Body>
	  <tem:AppendDataObject>
		 <tem:dataType>{{ doc.logo_dataType }}</tem:dataType>
		 <tem:dataReference>0</tem:dataReference>
		 <tem:dataXML>
			<![CDATA[<?xml version="1.0" encoding="ISO-8859-9"?>
<AR_APS>
  <AR_AP DBOP="INS" >
	<ACCOUNT_TYPE>1</ACCOUNT_TYPE>
	<CODE>{{ doc.name }}</CODE>
	<TITLE>{{ doc.customer_name }}</TITLE>
	<CORRESP_LANG>1</CORRESP_LANG>
	<NOTES>
	  <NOTE>
		<INTERNAL_REFERENCE>0</INTERNAL_REFERENCE>
	  </NOTE>
	</NOTES>
	<CL_ORD_FREQ>1</CL_ORD_FREQ>
	<INVOICE_PRNT_CNT>1</INVOICE_PRNT_CNT>
	<PARENTCLCODE>{{ doc.logo_parent_code }}</PARENTCLCODE>
	<PERSCOMPANY>{{ doc.personal_company }}</PERSCOMPANY>
	<ORGLOGOID></ORGLOGOID>
	<ADDRESS1>{{ docBillingAddress.address_line1 }}</ADDRESS1>
	<ADDRESS2>{{ docBillingAddress.address_line2 or '' }}</ADDRESS2>
	<DISTRICT_CODE></DISTRICT_CODE>
	<DISTRICT></DISTRICT>
	<TOWN_CODE></TOWN_CODE>
	<TOWN>{{ docBillingAddress.county or '' }}</TOWN>
	<CITY_CODE></CITY_CODE>
	<CITY>{{ docBillingAddress.city or '' }}</CITY>
	<COUNTRY_CODE></COUNTRY_CODE>
	<COUNTRY>{{ docBillingAddress.country or '' }}</COUNTRY>
	<TELEPHONE1></TELEPHONE1>
	<TELEPHONE1_CODE></TELEPHONE1_CODE>
	<TELEPHONE2></TELEPHONE2>
	<TELEPHONE2_CODE></TELEPHONE2_CODE>
	<TAX_ID>{{ doc.tax_id or '' }}</TAX_ID>
	<TAX_OFFICE>{{ doc.custom_tax_office or '' }}</TAX_OFFICE>
	<CONTACT></CONTACT>
	<PAYMENT_CODE>{{ doc.logo_payment_term }}</PAYMENT_CODE>
	<E_MAIL></E_MAIL>
	<AUXIL_CODE>{{ doc.customer_group }}</AUXIL_CODE>
	<AUXIL_CODE5>{{ doc.territory }}</AUXIL_CODE5>
	<CONTACT2></CONTACT2>
	<E_MAIL2></E_MAIL2>
	<PURCHBRWS>1</PURCHBRWS>
	<SALESBRWS>1</SALESBRWS>
	<IMPBRWS>1</IMPBRWS>
	<EXPBRWS>1</EXPBRWS>
	<FINBRWS>1</FINBRWS>
	<COLLATRLRISK_TYPE>1</COLLATRLRISK_TYPE>
	<EBANKCODE>-7</EBANKCODE>
	<RISK_TYPE1>1</RISK_TYPE1>
	<RISK_TYPE2>1</RISK_TYPE2>
	<RISK_TYPE3>1</RISK_TYPE3>
	<PROFILE_ID>2</PROFILE_ID>
	<PROFILEID_DESP>1</PROFILEID_DESP>
	<DISP_PRINT_CNT>1</DISP_PRINT_CNT>
	<ORD_PRINT_CNT>1</ORD_PRINT_CNT>
  </AR_AP>
</AR_APS>]]>
		 </tem:dataXML>

		 <tem:paramXML>
		 <![CDATA[{{ parameterXML }}]]>
		 </tem:paramXML>
		 <tem:FirmNr>{{ docLObjectServiceSettings.logo_company_no or '1' }}</tem:FirmNr>
		 <tem:securityCode>{{ docLObjectServiceSettings.lobject_service_client_secret }}</tem:securityCode>
		 </tem:AppendDataObject>
		 </soapenv:Body>
</soapenv:Envelope>"""
		dctResult.parameter_xml = """
<Parameters>
  <ReplicMode>0</ReplicMode>
  <CheckParams>1</CheckParams>
  <CheckRight>1</CheckRight>
  <ApplyCampaign>1</ApplyCampaign>
  <ApplyCondition>1</ApplyCondition>
  <FillAccCodes>1</FillAccCodes>
  <FormSeriLotLines>0</FormSeriLotLines>
  <GetStockLinePrice>0</GetStockLinePrice>
  <ExportAllData>1</ExportAllData>
  <Validation>0</Validation>
  <CheckApproveDate>0</CheckApproveDate>
  <Period>01</Period>
</Parameters>"""

	if dctResult.op_result == False:
		link = frappe.utils.get_link_to_form("LOGO Object Service Settings", _("LOGO Object Service Settings"))
		frappe.throw(_("{0} tipi {1} sayfasında XML şablonu bulunamadı!").format(_(doctype), link))

	return dctResult

@frappe.whitelist()
def get_default_address(doc):
	#Returns default address of a given doctype (Supplier, Customer)
	from frappe.contacts.doctype.address.address import get_default_address

	docResult = None

	address_name = get_default_address(doc.doctype, doc.name)
	if address_name:
		docResult = frappe.get_doc("Address", address_name)

	return docResult

@frappe.whitelist()
def get_logo_mapping_for(data_type, erp_code, throw_exception = False, docLObjectServiceSettings = None):
	#Gets info from LOGO Object Service Settings -> Mappings table
	dctResult = frappe._dict({
		"op_result": False,
		"op_message": "",
		"logo_code": "",
		"logo_code_2": ""
	})

	if not docLObjectServiceSettings:
		docLObjectServiceSettings = frappe.get_doc("LOGO Object Service Settings")

	for mapping in docLObjectServiceSettings.mappings:
		if mapping.data_type == data_type:
			if mapping.erp_code == erp_code:
				dctResult.logo_code = mapping.logo_code
				dctResult.logo_code_2 = mapping.logo_code_2
				dctResult.op_result = True

	if dctResult.op_result == False and throw_exception == True:
		link = frappe.utils.get_link_to_form("LOGO Object Service Settings", _("LOGO Object Service Settings"))
		frappe.throw(_("{0} tipinde {1} için eşleştirme bulunamadı! {2} sayfasında kontrol ediniz").format(data_type, erp_code, link))

	return dctResult

@frappe.whitelist()
def get_item_tax_rate(strItemCode, docLObjectServiceSettings = None):
	flResult = 0

	if not docLObjectServiceSettings:
		docLObjectServiceSettings = frappe.get_doc("LOGO Object Service Settings")

	docItem = frappe.get_doc("Item", strItemCode)

	for tax in docItem.taxes:
		tax_company = frappe.db.get_value("Item Tax Template", tax.item_tax_template, "company")
		if tax_company == docLObjectServiceSettings.default_company:
			docItemTaxTemplate = frappe.get_doc("Item Tax Template", tax.item_tax_template)
			if len(docItemTaxTemplate.taxes) == 0:
				frappe.throw("{0} için vergi oranı tanımlı olmalıdır!".format(docItemTaxTemplate.name))
			else:
				flResult = docItemTaxTemplate.taxes[0].tax_rate

	return flResult

@frappe.whitelist()
def get_logo_units_for_unit_set(unit_set_code, docLObjectServiceSettings=None):
	"""
	Fetch all UOMs for a given UNITSET_CODE from LOGO database.
	
	Args:
	    unit_set_code (str): The UNITSET code (e.g., "05")
	    docLObjectServiceSettings: LOGO Object Service Settings DocType
	
	Returns:
	    list: List of dicts with CODE, CONVFACT1, CONVFACT2
	"""
	if not unit_set_code:
		return []
	
	if not docLObjectServiceSettings:
		docLObjectServiceSettings = frappe.get_doc("LOGO Object Service Settings")
	
	try:
		from tiger_integration.api.logo_db import execute_query
		
		company = docLObjectServiceSettings.logo_company_no
		
		query = """
			SELECT UNITSETL.CODE, UNITSETL.CONVFACT1, UNITSETL.CONVFACT2
			FROM {UNITSETL} AS UNITSETL
			  INNER JOIN {UNITSETF} AS UNITSETF 
			    ON UNITSETL.UNITSETREF = UNITSETF.LOGICALREF
			WHERE UNITSETF.CODE = %(unit_set_code)s
			ORDER BY UNITSETL.LINENR
		"""
		
		result = execute_query(query, company=company, params={"unit_set_code": unit_set_code})
		
		if result.op_result and result.data:
			return result.data
		else:
			frappe.log_error(
				title="Tiger Integration: get_logo_units_for_unit_set failed",
				message=result.op_message or "No data returned from LOGO database"
			)
			return []
		
	except Exception as e:
		frappe.log_error(
			title="Tiger Integration: get_logo_units_for_unit_set error",
			message=frappe.get_traceback()
		)
		return []

def validate_export_to_logo(doctype, docname, docLObjectServiceSettings):
	dctResult = frappe._dict({
		"op_result": True,
		"op_message": ""
	})

	doc = frappe.get_doc(doctype, docname)
	doc.check_permission("read")

	if doctype == "Item":
		#Tax must be ok
		if len(doc.taxes) == 0:
			dctResult.op_result = False
			dctResult.op_message = _("Vergiler tanımlı olmalıdır!")

	elif doctype == "Supplier":
		#Payment Term, default billing address
		if not doc.payment_terms:
			dctResult.op_result = False
			dctResult.op_message = _("Ödeme Şekli alanı boş bırakılmamalıdır!")

		#Check billing address
		dctBillingAddress = frappe.get_all("Address",
			filters=[
				["Dynamic Link", "link_doctype", "=", "Supplier"],
				["Dynamic Link", "link_name", "=", doc.name],
				["is_primary_address", "=", 1],
				["address_type", "=", "Billing"]
			],
			fields=["name"],
			limit=1
		)
		if not dctBillingAddress:
			dctResult.op_result = False
			dctResult.op_message = _("Fatura adresi tanımlı olmalıdır!")

	elif doctype == "Customer":
		#Payment Term, default billing address
		if not doc.payment_terms:
			dctResult.op_result = False
			dctResult.op_message = _("Ödeme Şekli alanı boş bırakılmamalıdır!")

		#Check billing address
		dctBillingAddress = frappe.get_all("Address",
			filters=[
				["Dynamic Link", "link_doctype", "=", "Customer"],
				["Dynamic Link", "link_name", "=", doc.name],
				["is_primary_address", "=", 1],
				["address_type", "=", "Billing"]
			],
			fields=["name"],
			limit=1
		)
		if not dctBillingAddress:
			dctResult.op_result = False
			dctResult.op_message = _("Fatura adresi tanımlı olmalıdır!")

	elif doctype in ["Delivery Note", "Sales Invoice"]:
		# Check each item exists and is active in LOGO (ACTIVE=0 means active)
		# before exporting to prevent partial records in LOGO Tiger.
		from tiger_integration.api.logo_db import execute_query
		company = docLObjectServiceSettings.logo_company_no
		invalid_items = []

		for item in doc.items:
			result = execute_query(
				"SELECT ACTIVE FROM {ITEMS} WHERE CODE = %(code)s",
				company=company,
				params={"code": item.item_code}
			)
			if not result.op_result or not result.data or result.data[0].get("ACTIVE") != 0:
				if item.item_code not in invalid_items:
					invalid_items.append(item.item_code)

		if invalid_items:
			dctResult.op_result = False
			dctResult.op_message = _("Aşağıdaki ürünler LOGO'da bulunamadı veya aktif değil: {0}. Lütfen önce bu ürünleri LOGO'ya aktarın.").format(", ".join(invalid_items))

	return dctResult

@frappe.whitelist(allow_guest=False)
def bulk_export_to_logo(names, doctype, update_logo=False):
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	# Decode names
	names = json.loads(names)

	# Queue the process to run in background
	frappe.enqueue(
		method=process_logo_export,
		queue='long',
		timeout=3600,
		names=names,
		doctype=doctype,
		update_logo=update_logo,
		user=frappe.session.user
	)

	return {"op_result": True, "op_message": _("Export started in background...")}

def process_logo_export(names, doctype, update_logo, user):
	dctResult = frappe._dict({
		"success_count": 0,
		"failure_count": 0,
		"error_message": []
	})

	# Open a Session for speed
	session = requests.Session()
	# Fetch settings once and try to use it
	docLObjectServiceSettings = frappe.get_doc("LOGO Object Service Settings")

	total = len(names)

	for i, name in enumerate(names):
		try:
			# Pass 'session'
			dctExportResult = export_to_logo(doctype, name, update_logo, session=session, settings=docLObjectServiceSettings)
			
			if dctExportResult.op_result == True:
				dctResult.success_count += 1
			else:
				dctResult.error_message.append("<b>{0}</b>: {1}".format(name, dctExportResult.op_message))
				dctResult.failure_count += 1

		except Exception as e:
			dctResult.error_message.append("{0}: {1}".format(name, str(e)))
			dctResult.failure_count += 1

		#Update Progress Bar every 1%
		if i % 10 == 0:
			frappe.publish_realtime("logo_progress", {"current": i, "total": total}, user=user)

	#Send Final Result to User (Cannot return, must publish)
	frappe.publish_realtime("logo_done", {
		"success": dctResult.success_count,
		"failed": dctResult.failure_count,
		"errors": dctResult.error_message
	}, user=user)

def item_exists_in_logo(item_code):
	"""Check if an item already exists in Logo Tiger ERP database by querying the ITEMS table."""
	docSQLSettings = frappe.get_doc("LOGO SQL Settings")
	if not docSQLSettings.enable_logo_sql_connection:
		return False

	try:
		conn = pymssql.connect(
			server=docSQLSettings.sql_server_address,
			user=docSQLSettings.sql_user_name,
			password=docSQLSettings.get_password("sql_user_password"),
			database=docSQLSettings.sql_database_name,
			login_timeout=5,
			timeout=5,
		)
		cursor = conn.cursor()
		cursor.execute("SELECT TOP 1 LOGICALREF FROM LG_001_ITEMS WHERE CODE = %s AND ACTIVE = 0", (item_code,))
		row = cursor.fetchone()
		conn.close()
		return row is not None
	except Exception as e:
		frappe.log_error("Logo SQL Check Error", f"item_exists_in_logo({item_code}): {e}")
		return False

@frappe.whitelist(allow_guest=False)
def export_to_logo(doctype, docname, update_logo = False, session=None, settings=None):
	dctResult = frappe._dict({
		"op_result": False,
		"op_message": "",
		"raw_response": "",
		"data_reference": 0,
		"op_status": 0
	})

	doc = frappe.get_doc(doctype, docname)
	doc.check_permission("read")
	docLObjectServiceSettings = settings if settings else frappe.get_doc("LOGO Object Service Settings")
	docLObjectServiceSettings.check_permission("read")

	requester = session if session else requests

	try:
		if docLObjectServiceSettings.default_parameter_xml:
			parameterXML = docLObjectServiceSettings.default_parameter_xml

		dctXMLInfo = get_logo_xml(doctype, docLObjectServiceSettings)
		
		if dctXMLInfo.op_result == True:
			soap_body = dctXMLInfo.xml_template
			parameterXML = dctXMLInfo.parameter_xml if dctXMLInfo.get('parameter_xml') else parameterXML

		if docLObjectServiceSettings.enable_lobject_service == 0:
			frappe.throw(_("LOGO Object Service aktif değil!"))

		# Check if item already exists in Logo before exporting
		if doctype == "Item" and item_exists_in_logo(docname):
			dctResult.op_result = True
			dctResult.op_message = _("Item already exists in Logo, skipped.")
			return dctResult

		dctValidationResult = validate_export_to_logo(doctype, docname, docLObjectServiceSettings)
		if dctValidationResult.op_result == False:
			dctResult.op_result = False
			dctResult.op_message = dctValidationResult.op_message
		else:
			if doc.doctype == "Item":
				#Find tax rate
				doc.logo_tax_rate = get_item_tax_rate(doc.item_code, docLObjectServiceSettings)

				soap_body = frappe.render_template(soap_body, context={'doc': doc, 'docLObjectServiceSettings': docLObjectServiceSettings, 'parameterXML': parameterXML})

			elif doc.doctype in ["Supplier", "Customer"]:

				if doc.doctype == "Customer" and doc.customer_type == "Individual":
					doc.personal_company = 1
				elif doc.doctype == "Supplier" and doc.supplier_type == "Individual":
					doc.personal_company = 1
				else:
					doc.personal_company = 0

				dctBillingAddress = frappe.get_all("Address",
					filters=[
						["Dynamic Link", "link_doctype", "=", doc.doctype],
						["Dynamic Link", "link_name", "=", doc.name],
						["is_primary_address", "=", 1],
						["address_type", "=", "Billing"]
					],
					fields=["name"],
					limit=1
				)
				if dctBillingAddress:
					docBillingAddress = frappe.get_doc("Address", dctBillingAddress[0].name)
				else:
					frappe.throw(_("{0} {1} has no Billing Address").format(doc.doctype, doc.name))

				soap_body = frappe.render_template(soap_body, context={'doc': doc, 'docLObjectServiceSettings': docLObjectServiceSettings, 'docBillingAddress': docBillingAddress, 'parameterXML': parameterXML})
			elif doctype in ["Sales Order", "Delivery Note", "Sales Invoice"]:
				from frappe.utils import formatdate, format_time
				doc.posting_date_str = formatdate(doc.posting_date, "dd-mm-yyyy")
				doc.posting_time_str = 0#format_time(doc.posting_time, format_string="HH:mm:ss.SSS") + "+03:00"

				soap_body = frappe.render_template(soap_body, context={'doc': doc, 'docLObjectServiceSettings': docLObjectServiceSettings, 'parameterXML': parameterXML})

			else:
				soap_body = frappe.render_template(soap_body, context={'doc': doc, 'docLObjectServiceSettings': docLObjectServiceSettings, 'parameterXML': parameterXML})

			headers = {
				"Content-Type": "text/xml;charset=UTF-8",
				"Accept-Encoding": "gzip,deflate",
				"SOAPAction": "http://tempuri.org/ISvc/AppendDataObject"
			}

			if docLObjectServiceSettings.enable_detailed_log:
				frappe.log_error("LOGO Object Request", f"URL={docLObjectServiceSettings.lobject_service_address}\n\nSOAP Body={soap_body}\n\nSOAP Headers={headers}")

			response = requester.post(
				url=docLObjectServiceSettings.lobject_service_address,
				data=soap_body,#.encode('utf-8'),
				headers=headers,
				timeout=20
			)

			if docLObjectServiceSettings.enable_detailed_log:
				frappe.log_error("LOGO Object Response", f"Status:{response.status_code}\nBody:{response.text}")

			soup = BeautifulSoup(response.content, 'xml')

			if response.status_code != 200:
				dctResult.op_result = False
				dctResult.op_message = f"HTTP Error {response.status_code}: {response.reason}."
				fault_string = soup.find('faultstring')
				if fault_string.text:
					dctResult.op_message += fault_string.text
			else:
				dctResult.raw_response = response.text
				
				result_status = soup.find('status')

				if not result_status or not result_status.text:
					dctResult.op_message = "Connected but no status returned!"
				else:
					data_reference = soup.find('dataReference')
					error_string = soup.find('errorString')

					dctResult.data_reference = int(data_reference.text) if data_reference else 0
					dctResult.op_status = int(result_status.text) if result_status else 0
					if dctResult.op_status != 3:
						dctResult.op_result = False
						dctResult.op_message =  (error_string.text if error_string else "") + "(OpStatus=" + str(dctResult.op_status) + ")"
					else:
						dctResult.op_result = True
						dctResult.op_message = data_reference
						doc.add_comment("Comment", text=_("LOGO Export reference no {0}").format(dctResult.data_reference), comment_email=frappe.session.user, comment_by=frappe.session.user)
						
						# Set LOGO reference number if DocType has the field
						if frappe.get_meta(doc.doctype).has_field("custom_ld_logo_ref_no"):
							frappe.db.set_value(doc.doctype, doc.name, "custom_ld_logo_ref_no", dctResult.data_reference, update_modified=False)

	except Exception as e:
		dctResult.op_result = False
		dctResult.op_message = str(e) + "\n\n" + frappe.get_traceback()

	return dctResult

def gzip_zip_base64(content):
	import gzip
	import base64
	import sys
	import os
	"""
		 gzip + base64 compression
				 In this way the compressed object relatively short / small when the effect is not obvious, but since then base64 becomes large, but the compression is relatively large when the object will be effective
	:param content:
	:return:
	"""
	bytes_com = gzip.compress(str(content).encode("utf-8"))
	base64_data = base64.b64encode(bytes_com)
	back = str(base64_data.decode())
	return back, sys.getsizeof(back)
	# Gzip file for read and write operations
	# with gzip.open('./log/zip-test.gz', 'wb') as write:
	#     write.write(str(back).encode("utf-8"))

def gzip_unzip_base64(content):
	import gzip
	import base64
	import sys
	import os
	"""
		 base64 + gzip decompression
	:param content:
	:return:
	"""
	base64_data = base64.b64decode(content)
	bytes_decom = gzip.decompress(base64_data)
	str_unzip = bytes_decom.decode()
	return str_unzip, sys.getsizeof(str_unzip)


@frappe.whitelist()
def download_einvoice_pdf(sales_invoice_name):
	"""
	Download e-invoice PDF from eLogo and attach to Sales Invoice.
	
	This function:
	1. Gets Sales Invoice and checks for custom_ld_logo_ref_no
	2. Connects to LOGO SQL Server and queries GUID
	3. Calls eLogo Login API to get sessionID
	4. Calls eLogo getDocumentData API with sessionID and GUID
	5. Decodes base64 and unzips to extract PDF
	6. Attaches PDF to Sales Invoice
	
	Args:
		sales_invoice_name (str): Sales Invoice name
	
	Returns:
		frappe._dict: Result with op_result, op_message, and step-by-step details
	"""
	import pymssql
	from tiger_integration.api.elogo_api import elogo_login, elogo_get_document_data, unzip_base64_to_pdf
	
	dctResult = frappe._dict({
		"op_result": False,
		"op_message": "",
		"steps": [],
		"guid": "",
		"session_id": "",
		"pdf_file_name": ""
	})
	
	def add_step(step_name, status, message=""):
		"""Helper to track step progress"""
		dctResult.steps.append({
			"step": step_name,
			"status": status,  # "success", "error", "info"
			"message": message
		})
	
	try:
		# Step 1: Get Sales Invoice and check for LOGO reference
		add_step("Step 1: Get Sales Invoice", "info", f"Fetching Sales Invoice: {sales_invoice_name}")
		
		if not frappe.has_permission("Sales Invoice", "read", sales_invoice_name):
			frappe.throw("Insufficient Permission", frappe.PermissionError)
		
		docSalesInvoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
		logo_ref_no = docSalesInvoice.get("custom_ld_logo_ref_no")
		
		if logo_ref_no:
			add_step("Step 1: Get Sales Invoice", "success", f"LOGO Reference No: {logo_ref_no}")
			
			# Step 2: Check for existing PDF attachment
			add_step("Step 2: Check Existing Attachments", "info", "Checking if PDF already attached...")
			
			existing_files = frappe.db.get_all("File",
				filters={
					"attached_to_doctype": "Sales Invoice",
					"attached_to_name": sales_invoice_name,
					"file_name": ["like", "%ELOGO_INVOICE%"]
				},
				fields=["name", "file_name"]
			)
			
			if existing_files:
				add_step("Step 2: Check Existing Attachments", "info", 
					f"PDF already attached: {existing_files[0].file_name}")
				dctResult.op_result = True
				dctResult.op_message = f"PDF already attached: {existing_files[0].file_name}"
			else:
				add_step("Step 2: Check Existing Attachments", "success", "No existing PDF found, proceeding...")
				
				# Step 3: Get settings
				add_step("Step 3: Get Settings", "info", "Loading LOGO Object Service Settings...")
				
				docSettings = frappe.get_doc("LOGO Object Service Settings")
				docSettings.check_permission("read")
				
				# Get eLogo credentials
				elogo_username = docSettings.elogo_username
				elogo_password = docSettings.get_password("elogo_password") if docSettings.elogo_password else ""
				elogo_service_address = docSettings.elogo_service_address
				logo_company_no = docSettings.logo_company_no
				
				if elogo_username and elogo_password and elogo_service_address:
					add_step("Step 3: Get Settings", "success", 
						f"eLogo Service: {elogo_service_address}, Company No: {logo_company_no}")
					
					# Step 4: Query LOGO DB for GUID
					add_step("Step 4: Query LOGO DB", "info", "Querying LOGO database for GUID...")
					
					from tiger_integration.api.logo_db import execute_query
					
					# Use generic execute_query with table placeholder
					query = "SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(logo_ref_no)s"
					guid_result = execute_query(query, logo_company_no, period="01", params={"logo_ref_no": logo_ref_no})
					
					if guid_result.op_result:
						if guid_result.data:
							guid = guid_result.data[0].get("GUID")
							dctResult.guid = guid
							add_step("Step 4: Query LOGO DB", "success", f"Found GUID: {guid}")
							
							# Step 5: Login to eLogo
							add_step("Step 5: eLogo Login", "info", f"Logging in as {elogo_username}...")
							
							login_result = elogo_login(elogo_service_address, elogo_username, elogo_password)
							
							if login_result.op_result:
								session_id = login_result.session_id
								dctResult.session_id = session_id
								add_step("Step 5: eLogo Login", "success", f"Session ID: {session_id[:20]}...")
								
								# Step 6: Get document data from eLogo
								add_step("Step 6: Get Document Data", "info", f"Requesting PDF for UUID: {guid}...")
								
								doc_result = elogo_get_document_data(elogo_service_address, session_id, guid)
								
								if doc_result.op_result:
									add_step("Step 6: Get Document Data", "success", f"Received ZIP file: {doc_result.file_name}, Hash: {doc_result.hash}")
									
									# Step 7: Extract PDF from ZIP
									add_step("Step 7: Extract PDF", "info", "Decoding base64 and extracting PDF from ZIP...")
									
									pdf_result = unzip_base64_to_pdf(doc_result.base64_data)
									
									if pdf_result.op_result:
										add_step("Step 7: Extract PDF", "success", f"Extracted PDF: {pdf_result.pdf_file_name}, Size: {len(pdf_result.pdf_content)} bytes")
										
										# Step 8: Attach PDF to Sales Invoice
										add_step("Step 8: Attach PDF", "info", "Attaching PDF to Sales Invoice...")
										
										try:
											# Create file name
											pdf_filename = f"ELOGO_INVOICE_{sales_invoice_name}.pdf"
											
											# Save file using Frappe's File API
											file_doc = frappe.get_doc({
												"doctype": "File",
												"file_name": pdf_filename,
												"attached_to_doctype": "Sales Invoice",
												"attached_to_name": sales_invoice_name,
												"is_private": 1,
												"content": pdf_result.pdf_content
											})
											file_doc.save()
											
											dctResult.pdf_file_name = pdf_filename
											add_step("Step 8: Attach PDF", "success", 
												f"PDF attached successfully: {pdf_filename}")
											
											# Add comment to Sales Invoice with step-by-step results
											comment_text = "e-Invoice PDF Download Process Results:\n"

											# Success!
											dctResult.op_result = True
											dctResult.op_message = f"Successfully downloaded and attached e-invoice PDF: {pdf_filename}"
											
											for step in dctResult.steps:
												status_icon = "✅" if step.get("status") == "success" else ("❌" if step.get("status") == "error" else "ℹ️")
												comment_text += f"<br>{status_icon} {step.get('step', '')}: {step.get('message', '')}"
											
											comment_text += f"\n\nFinal Result: {'SUCCESS' if dctResult.op_result else 'FAILED'}\n"
											comment_text += f"Message: {dctResult.op_message}"
											
											docSalesInvoice.add_comment("Comment",
												text=comment_text,
												comment_email=frappe.session.user,
												comment_by=frappe.session.user)
										
										except Exception as e:
											add_step("Step 8: Attach PDF", "error", f"Attachment error: {str(e)}")
											dctResult.op_message = f"Failed to attach PDF: {str(e)}"
											frappe.log_error("PDF Attachment Error", frappe.get_traceback())
									else:
										add_step("Step 7: Extract PDF", "error", pdf_result.op_message)
										dctResult.op_message = f"PDF extraction failed: {pdf_result.op_message}"
								else:
									add_step("Step 6: Get Document Data", "error", doc_result.op_message)
									dctResult.op_message = f"eLogo getDocumentData failed: {doc_result.op_message}"
							else:
								add_step("Step 5: eLogo Login", "error", login_result.op_message)
								dctResult.op_message = f"eLogo login failed: {login_result.op_message}"
						else:
							add_step("Step 4: Query LOGO DB", "error", f"No record found for LOGICALREF={logo_ref_no}")
							dctResult.op_message = f"No GUID found for LOGICALREF={logo_ref_no}"
					else:
						add_step("Step 4: Query LOGO DB", "error", guid_result.op_message)
						dctResult.op_message = guid_result.op_message
				else:
					add_step("Step 3: Get Settings", "error", "eLogo credentials not configured")
					dctResult.op_message = "eLogo credentials not configured in LOGO Object Service Settings"
		else:
			add_step("Step 1: Get Sales Invoice", "error", "No LOGO reference number found (custom_ld_logo_ref_no is empty)")
			dctResult.op_message = "Sales Invoice has no LOGO reference number"
		
	except Exception as e:
		dctResult.op_message = f"Unexpected error: {str(e)}"
		add_step("Error", "error", str(e))
		frappe.log_error(
			"eInvoice PDF Download Error",
			f"Failed to download e-invoice PDF for {sales_invoice_name}: {frappe.get_traceback()}")


def get_invoice_ref_from_stline(delivery_note_ref, company_no, period):
	"""
	Query LOGO STLINE to find invoice reference from delivery note receipt.
	
	STLINE stores line items. The relationship between receipt (Delivery Note)
	and invoice is via INVOICEREF field.
	
	Args:
		delivery_note_ref (str): LOGO reference from Delivery Note (custom_ld_logo_ref_no)
		company_no (str): LOGO company number
		period (str): Period number (01-12)
	
	Returns:
		frappe._dict: Result with op_result, invoice_ref, op_message
	"""
	from tiger_integration.api.logo_db import execute_query
	
	dctResult = frappe._dict({
		"op_result": False,
		"invoice_ref": None,
		"op_message": ""
	})
	
	try:
		# Query STLINE to find invoice reference from delivery note lines
		query = """
			SELECT DISTINCT INVOICEREF 
			FROM {STLINE} 
			WHERE STFICHEREF = %(delivery_note_ref)s
			AND INVOICEREF IS NOT NULL
			AND INVOICEREF != 0
		"""
		
		result = execute_query(query, company_no, period=period, 
						  params={"delivery_note_ref": delivery_note_ref})
		
		if result.op_result and result.data:
			invoice_ref = result.data[0].get("INVOICEREF")
			if invoice_ref:
				dctResult.op_result = True
				dctResult.invoice_ref = str(invoice_ref)
				dctResult.op_message = f"Found invoice reference: {invoice_ref}"
			else:
				dctResult.op_message = "No invoice reference found in STLINE"
		else:
			dctResult.op_message = result.op_message or "Failed to query STLINE"
	
	except Exception as e:
		dctResult.op_message = f"Error querying STLINE: {str(e)}"
		frappe.log_error(
			message=frappe.get_traceback(),
			title="Get Invoice Ref from STLINE Error"
		)
	
	return dctResult


@frappe.whitelist()
def sync_invoice_ref_from_delivery_note():
	"""
	Scheduled task to sync invoice references from Delivery Note to Sales Invoice.
	
	Finds Sales Invoices that:
	- Are submitted (docstatus = 1)
	- Have no custom_ld_logo_ref_no (or empty)
	- Have linked Delivery Note with custom_ld_logo_ref_no
	
	For each, queries LOGO STLINE to find corresponding invoice.
	If found, updates Sales Invoice custom_ld_logo_ref_no.
	
	This allows the existing download_einvoice_pdfs task to automatically
	download the e-invoice PDF once the reference is set.
	
	Returns:
		frappe._dict: Result with processed_count, updated_count, details
	"""
	dctResult = frappe._dict({
		"op_result": False,
		"processed_count": 0,
		"updated_count": 0,
		"details": []
	})
	
	try:
		# Check if the feature is enabled in LOGO Object Service Settings
		settings = frappe.get_doc("LOGO Object Service Settings")
		
		if not frappe.db.get_single_value(
			"LOGO Object Service Settings", 
			"enable_elogo_pdf_attachments_for_invoices"
		):
			dctResult.op_message = "eInvoice PDF download feature is not enabled"
			return dctResult
		
		logo_company_no = settings.logo_company_no
		
		# Find Sales Invoices that need to be synced
		# Criteria: submitted, no LOGO ref, has linked Delivery Note with LOGO ref
		invoices = frappe.db.sql("""
SELECT 
    si.name as invoice_name,
    si.custom_ld_logo_ref_no as current_logo_ref,
    sii.delivery_note as delivery_note,
    dn.custom_ld_logo_ref_no as delivery_note_logo_ref
FROM `tabSales Invoice` si
JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
LEFT JOIN `tabDelivery Note` dn ON sii.delivery_note = dn.name
WHERE si.docstatus = 1
AND (si.custom_ld_logo_ref_no IS NULL OR si.custom_ld_logo_ref_no = '')
AND sii.delivery_note IS NOT NULL
AND sii.delivery_note != ''
AND dn.custom_ld_logo_ref_no IS NOT NULL
AND dn.custom_ld_logo_ref_no != ''
ORDER BY si.creation DESC
LIMIT 50
		""", as_dict=True)
		
		dctResult.processed_count = len(invoices)
		
		for inv in invoices:
			detail = {
				"invoice": inv.invoice_name,
				"delivery_note": inv.delivery_note,
				"delivery_note_logo_ref": inv.delivery_note_logo_ref,
				"status": "pending",
				"message": ""
			}
			
			try:
				# Determine period from invoice date
				period = "01"  # Default to first period
				
				# Query LOGO STLINE for invoice reference
				stline_result = get_invoice_ref_from_stline(
					inv.delivery_note_logo_ref,
					logo_company_no,
					period
				)
				
				if stline_result.op_result and stline_result.invoice_ref:
					# Update Sales Invoice with invoice reference
					frappe.db.set_value(
						"Sales Invoice", 
						inv.invoice_name, 
						"custom_ld_logo_ref_no", 
						stline_result.invoice_ref
					)
					
					detail["status"] = "success"
					detail["invoice_logo_ref"] = stline_result.invoice_ref
					detail["message"] = f"Updated with invoice ref: {stline_result.invoice_ref}"
					dctResult.updated_count += 1
				else:
					detail["status"] = "not_found"
					detail["message"] = stline_result.op_message or "No invoice found in LOGO"
				
			except Exception as e:
				detail["status"] = "error"
				detail["message"] = str(e)
				frappe.log_error(
					message=frappe.get_traceback(),
					title=f"Sync Invoice Ref Failed for {inv.invoice_name}"
				)
			
			dctResult.details.append(detail)
		
		# Commit all changes
		frappe.db.commit()
		
		dctResult.op_result = True
		dctResult.op_message = f"Processed {dctResult.processed_count} invoices, updated {dctResult.updated_count}"
	
	except Exception as e:
		dctResult.op_message = f"Unexpected error: {str(e)}"
		frappe.log_error(
			message=frappe.get_traceback(),
			title="Sync Invoice Ref from Delivery Note Error"
		)
	
	return dctResult