# -*- coding: utf-8 -*-
# LOGEDOSOFT
# eLogo PostBox Service API Integration

import frappe
import requests
from bs4 import BeautifulSoup


def elogo_login(service_address, username, password):
	"""
	Call eLogo PostBox Login method to get sessionID.
	
	Args:
		service_address (str): eLogo PostBox service URL (e.g., https://pb.elogo.com.tr/PostBoxService.svc)
		username (str): eLogo username
		password (str): eLogo password
	
	Returns:
		frappe._dict: Result with op_result, session_id, op_message
	"""
	dctResult = frappe._dict({
		"op_result": False,
		"session_id": "",
		"op_message": ""
	})
	
	# Build SOAP envelope for Login
	soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:efat="http://schemas.datacontract.org/2004/07/eFaturaWebService">
   <soapenv:Header/>
   <soapenv:Body>
      <tem:Login>
         <tem:login>
            <efat:appStr>erpnext</efat:appStr>
            <efat:passWord>{password}</efat:passWord>
            <efat:source>1</efat:source>
            <efat:userName>{username}</efat:userName>
            <efat:version>1</efat:version>
         </tem:login>
      </tem:Login>
   </soapenv:Body>
</soapenv:Envelope>"""
	
	headers = {
		"Content-Type": "text/xml; charset=utf-8",
		"SOAPAction": "http://tempuri.org/IPostBoxService/Login",
		"Connection": "keep-alive",
		"Accept-Encoding": "gzip, deflate, br"
	}
	
	try:
		response = requests.post(
			url=service_address,
			data=soap_body,
			headers=headers,
			timeout=30
		)
		
		if response.status_code != 200:
			dctResult.op_message = f"HTTP Error {response.status_code}: {response.reason}"
			return dctResult
		
		# Parse XML response
		soup = BeautifulSoup(response.content, 'xml')
		
		# Find LoginResult and sessionID
		login_result = soup.find('LoginResult')
		session_id = soup.find('sessionID')
		
		if login_result and login_result.text.lower() == 'true' and session_id:
			dctResult.op_result = True
			dctResult.session_id = session_id.text
			dctResult.op_message = "Login successful"
		else:
			dctResult.op_message = f"Login failed. Response: {response.text}"
	
	except Exception as e:
		dctResult.op_message = f"Login error: {str(e)}"
		frappe.log_error(
			message=frappe.get_traceback(),
			title="eLogo Login Error"
		)
	
	return dctResult


def elogo_get_document_data(service_address, session_id, uuid, doc_type="EINVOICE", data_type="PDF"):
	"""
	Call eLogo PostBox getDocumentData method to download e-invoice PDF.
	
	Args:
		service_address (str): eLogo PostBox service URL
		session_id (str): Session ID from login
		uuid (str): Invoice GUID from LOGO database
		doc_type (str): Document type (default: EINVOICE)
		data_type (str): Data type (default: PDF)
	
	Returns:
		frappe._dict: Result with op_result, base64_data, file_name, op_message
	"""
	dctResult = frappe._dict({
		"op_result": False,
		"base64_data": "",
		"file_name": "",
		"hash": "",
		"op_message": ""
	})
	
	# Build SOAP envelope for getDocumentData
	soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
   <soapenv:Header/>
   <soapenv:Body>
      <tem:getDocumentData>
         <tem:sessionID>{session_id}</tem:sessionID>
         <tem:uuid>{uuid}</tem:uuid>
         <tem:docType>{doc_type}</tem:docType>
         <tem:dataType>{data_type}</tem:dataType>
      </tem:getDocumentData>
   </soapenv:Body>
</soapenv:Envelope>"""
	
	headers = {
		"Content-Type": "text/xml; charset=utf-8",
		"SOAPAction": "http://tempuri.org/IPostBoxService/getDocumentData",
		"Connection": "keep-alive",
		"Accept-Encoding": "gzip, deflate, br"
	}
	
	try:
		response = requests.post(
			url=service_address,
			data=soap_body,
			headers=headers,
			timeout=60
		)
		
		if response.status_code != 200:
			dctResult.op_message = f"HTTP Error {response.status_code}: {response.reason}"
			return dctResult
		
		# Parse XML response
		soup = BeautifulSoup(response.content, 'xml')
		
		# Find binaryData Value
		value = soup.find('Value')
		content_type = soup.find('contentType')
		file_name = soup.find('fileName')
		hash_value = soup.find('hash')
		
		if value and value.text:
			dctResult.op_result = True
			dctResult.base64_data = value.text
			dctResult.file_name = file_name.text if file_name else f"{uuid}.zip"
			dctResult.hash = hash_value.text if hash_value else ""
			dctResult.op_message = "Document data retrieved successfully"
		else:
			dctResult.op_message = f"No document data found. Response: {response.text}"
	
	except Exception as e:
		dctResult.op_message = f"getDocumentData error: {str(e)}"
		frappe.log_error(
			message=frappe.get_traceback(),
			title="eLogo getDocumentData Error"
		)
	
	return dctResult


def unzip_base64_to_pdf(base64_data):
	"""
	Decode base64 and unzip to extract PDF content.
	
	Args:
		base64_data (str): Base64 encoded ZIP file content
	
	Returns:
		frappe._dict: Result with op_result, pdf_content, op_message
	"""
	import base64
	import zipfile
	import io
	
	dctResult = frappe._dict({
		"op_result": False,
		"pdf_content": b"",
		"pdf_file_name": "",
		"op_message": ""
	})
	
	try:
		# Decode base64
		zip_data = base64.b64decode(base64_data)
		
		# Create in-memory zip file
		zip_buffer = io.BytesIO(zip_data)
		
		# Extract PDF from ZIP
		with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
			# List all files in the zip
			file_list = zip_ref.namelist()
			
			# Find PDF file
			pdf_files = [f for f in file_list if f.lower().endswith('.pdf')]
			
			if pdf_files:
				# Get the first PDF file
				pdf_file_name = pdf_files[0]
				pdf_content = zip_ref.read(pdf_file_name)
				
				dctResult.op_result = True
				dctResult.pdf_content = pdf_content
				dctResult.pdf_file_name = pdf_file_name
				dctResult.op_message = f"PDF extracted: {pdf_file_name}"
			else:
				dctResult.op_message = f"No PDF file found in ZIP. Files: {file_list}"
	
	except Exception as e:
		dctResult.op_message = f"Unzip error: {str(e)}"
		frappe.log_error(
			message=frappe.get_traceback(),
			title="eLogo Unzip PDF Error"
		)
	
	return dctResult