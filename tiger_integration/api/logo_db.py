# -*- coding: utf-8 -*-
# Copyright (c) 2023, LOGEDO
# License: GNU General Public License v3. See license.txt

"""
LOGO Database Query Module

Provides a thin interface for running parameterised SQL queries against a
LOGO ERP SQL Server instance.

Public surface
--------------
get_logo_db_settings()
    Return connection settings from the LOGO SQL Settings DocType.

build_table_name(table_key, company, period)
    Resolve a table key to a fully-qualified LOGO table name.

replace_table_placeholders(query, company, period)
    Replace all ``{TABLE_KEY}`` placeholders in a query string.

get_logo_connection()
    Context-manager that yields an open pymssql connection.

execute_query(query, company, period, params, as_dict, conn)
    Run a single query.  If *conn* is provided the caller owns the connection
    and it will NOT be closed here — use this for connection reuse across
    multiple queries.  If *conn* is None a new connection is opened and closed
    automatically.

test_connection()
    Verify that the configured LOGO SQL Server is reachable.
"""

import json
import re
from contextlib import contextmanager

import frappe
import pymssql
from frappe import _


# ---------------------------------------------------------------------------
# Table name map
# ---------------------------------------------------------------------------

LOGO_TABLE_MAP = {
	"INVOICE": ("INVOICE", "LG_{COMPANY}_{PERIOD}_INVOICE"),
	"STLINE": ("STLINE", "LG_{COMPANY}_{PERIOD}_STLINE"),
	"STFICHE": ("STFICHE", "LG_{COMPANY}_{PERIOD}_STFICHE"),
	"PAYTRANS": ("PAYTRANS", "LG_{COMPANY}_{PERIOD}_PAYTRANS"),
	"PAYPLANS": ("PAYPLANS", "LG_{COMPANY}_{PERIOD}_PAYPLANS"),
	"KSLINES": ("KSLINES", "LG_{COMPANY}_{PERIOD}_KSLINES"),
	"KSCURR": ("KSCURR", "LG_{COMPANY}_{PERIOD}_KSCURR"),
	"BANKLINES": ("BANKLINES", "LG_{COMPANY}_{PERIOD}_BANKLINES"),
	"EMUHTOTAL": ("EMUHTOTAL", "LG_{COMPANY}_{PERIOD}_EMUHTOTAL"),
	"EMFLINE": ("EMFLINE", "LG_{COMPANY}_{PERIOD}_EMFLINE"),
	"EMFICHE": ("EMFICHE", "LG_{COMPANY}_{PERIOD}_EMFICHE"),
	"CSHTRANS": ("CSHTRANS", "LG_{COMPANY}_{PERIOD}_CSHTRANS"),
	"ACCOUNTRP": ("ACCOUNTRP", "LG_{COMPANY}_{PERIOD}_ACCOUNTRP"),
	"PROJECTTOT": ("PROJECTTOT", "LG_{COMPANY}_{PERIOD}_PROJECTTOT"),
	"ITEMUNIT": ("ITEMUNIT", "LG_{COMPANY}_{PERIOD}_ITEMUNIT"),
	"PRCLIST": ("PRCLIST", "LG_{COMPANY}_{PERIOD}_PRCLIST"),
	"PRCPLAN": ("PRCPLAN", "LG_{COMPANY}_{PERIOD}_PRCPLAN"),
	"DISCLIST": ("DISCLIST", "LG_{COMPANY}_{PERIOD}_DISCLIST"),
	"DISCPLAN": ("DISCPLAN", "LG_{COMPANY}_{PERIOD}_DISCPLAN"),
	"CAMPALINE": ("CAMPALINE", "LG_{COMPANY}_{PERIOD}_CAMPALINE"),
	"ITMCHARVAL": ("ITMCHARVAL", "LG_{COMPANY}_{PERIOD}_ITMCHARVAL"),
	"ITMWSDEF": ("ITMWSDEF", "LG_{COMPANY}_{PERIOD}_ITMWSDEF"),
	"ITMWSTOT": ("ITMWSTOT", "LG_{COMPANY}_{PERIOD}_ITMWSTOT"),
	"ITEMS": ("ITEMS", "LG_{COMPANY}_ITEMS"),
	"CLCARD": ("CLCARD", "LG_{COMPANY}_CLCARD"),
	"BANKACC": ("BANKACC", "LG_{COMPANY}_BANKACC"),
	"ACCOUNTS": ("ACCOUNTS", "LG_{COMPANY}_ACCOUNTS"),
	"PROJECT": ("PROJECT", "LG_{COMPANY}_PROJECT"),
	"UNITSETL": ("UNITSETL", "LG_{COMPANY}_UNITSETL"),
	"UNITSETF": ("UNITSETF", "LG_{COMPANY}_UNITSETF"),
	"CAMPAIN": ("CAMPAIN", "LG_{COMPANY}_CAMPAIN"),
	"CHARVAL": ("CHARVAL", "LG_{COMPANY}_CHARVAL"),
	"CHARIS": ("CHARIS", "LG_{COMPANY}_CHARIS"),
	"ITMCLASSA": ("ITMCLASSA", "LG_{COMPANY}_ITMCLASSA"),
	"ITMCLASSB": ("ITMCLASSB", "LG_{COMPANY}_ITMCLASSB"),
	"ITMUNITA": ("ITMUNITA", "LG_{COMPANY}_ITMUNITA"),
	"ITMUNITB": ("ITMUNITB", "LG_{COMPANY}_ITMUNITB"),
	"ITMWSCARD": ("ITMWSCARD", "LG_{COMPANY}_ITMWSCARD"),
	"SPECODES": ("SPECODES", "LG_{COMPANY}_SPECODES"),
	"LGMAIN": ("LGMAIN", "LG_{COMPANY}_LGMAIN"),
	"LOGREP": ("LOGREP", "LG_{COMPANY}_LOGREP"),
	"CAPIFIRM": ("CAPIFIRM", "L_CAPIFIRM"),
	"CAPIPERIOD": ("CAPIPERIOD", "L_CAPIPERIOD"),
	"CITY": ("CITY", "L_CITY"),
	"COUNTRY": ("COUNTRY", "L_COUNTRY"),
	"POSTCODE": ("POSTCODE", "L_POSTCODE"),
}


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def get_logo_db_settings():
	doc = frappe.get_doc("LOGO SQL Settings")
	doc.check_permission("read")

	if not doc.get("enable_logo_sql_connection"):
		frappe.throw(
			_("LOGO SQL Connection is not enabled. Please enable it in LOGO SQL Settings."),
			frappe.ValidationError
		)

	return frappe._dict({
		"server": doc.sql_server_address,
		"user": doc.sql_user_name,
		"password": doc.get_password("sql_user_password") if doc.sql_user_password else "",
		"database": doc.sql_database_name,
		"login_timeout": 10,
		"timeout": 30,
		"charset": doc.get("sql_server_charset", "cp1254"),
		"enable_logging_for_queries": doc.get("enable_logging_for_queries", 0),
	})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize_company(company):
	return str(company).strip().zfill(3)


def _normalize_period(period):
	return str(period).strip().zfill(2)


def _log_query(original_query, generated_query, params, result_data, row_count, columns, error_message=None):
	log_data = {
		"Original Query": original_query,
		"Generated Query": generated_query,
		"Parameters": json.dumps(params) if params else "None",
		"Columns": ", ".join(columns) if columns else "None",
		"Row Count": row_count,
		"Result Data": json.dumps(result_data) if result_data else "None",
	}

	if error_message:
		log_data["Error"] = error_message
		title = "LOGO Query Failed"
		message = "LOGO Query Failed: {0}\n".format(original_query)
	else:
		title = "LOGO Query Executed"
		message = "LOGO Query Executed: {0}\n".format(original_query)
	
	message += "\n".join(["{0}: {1}".format(k, v) for k, v in log_data.items()])
	frappe.log_error(title=title, message=message)


# ---------------------------------------------------------------------------
# Table-name resolution
# ---------------------------------------------------------------------------

def build_table_name(table_key, company=None, period=None):
	table_key_upper = table_key.upper()

	if table_key_upper not in LOGO_TABLE_MAP:
		if company:
			normalized_company = _normalize_company(company)
			if period:
				normalized_period = _normalize_period(period)
				return "LG_{0}_{1}_{2}".format(normalized_company, normalized_period, table_key_upper)
			else:
				return "LG_{0}_{1}".format(normalized_company, table_key_upper)
		else:
			return "L_{0}".format(table_key_upper)

	_table_name, table_pattern = LOGO_TABLE_MAP[table_key_upper]
	result = table_pattern

	if "{COMPANY}" in result:
		if not company:
			frappe.throw(_("Company is required for table: {0}").format(table_key))
		result = result.replace("{COMPANY}", _normalize_company(company))

	if "{PERIOD}" in result:
		result = result.replace("{PERIOD}", _normalize_period(period or "01"))

	return result


def replace_table_placeholders(query, company=None, period=None):
	placeholder_pattern = r'\{([A-Za-z_][A-Za-z0-9_]*)\}'

	def replace_match(match):
		return build_table_name(match.group(1), company, period)

	return re.sub(placeholder_pattern, replace_match, query)


# ---------------------------------------------------------------------------
# Connection context manager
# ---------------------------------------------------------------------------

@contextmanager
def get_logo_connection():
	conn = None
	try:
		settings = get_logo_db_settings()
		conn = pymssql.connect(
			server=settings.server,
			user=settings.user,
			password=settings.password,
			database=settings.database,
			login_timeout=settings.login_timeout,
			timeout=settings.timeout,
			charset=settings.charset
		)
		yield conn
	finally:
		if conn:
			conn.close()


# ---------------------------------------------------------------------------
# Core query execution
# ---------------------------------------------------------------------------

def execute_query(query, company=None, period=None, params=None, as_dict=True, conn=None):
	"""Execute a single SQL query against the LOGO SQL Server.

	Parameters
	----------
	query   : str  — SQL with optional ``{TABLE_KEY}`` placeholders.
	company : str  — LOGO company number (zero-padded to 3 digits).
	period  : str  — LOGO period number (zero-padded to 2 digits).
	params  : tuple/dict — Query parameters passed to pymssql.
	as_dict : bool — When True, rows are returned as dicts.
	conn    : pymssql connection (optional).  When provided the caller owns
	          the connection; it will NOT be closed inside this function.
	          When None, a new connection is opened and closed automatically.

	Returns
	-------
	frappe._dict with keys: op_result, op_message, data, row_count, columns, query.
	"""
	dctResult = frappe._dict({
		"op_result": False,
		"op_message": "",
		"data": [],
		"row_count": 0,
		"columns": [],
		"query": "",
	})

	# When the caller supplies a connection we skip creating/closing one.
	owns_connection = conn is None
	actual_query = None
	should_log = 0

	try:
		settings = get_logo_db_settings()
		should_log = settings.get("enable_logging_for_queries", 0)

		actual_query = replace_table_placeholders(query, company, period)
		dctResult.query = actual_query

		if owns_connection:
			conn = pymssql.connect(
				server=settings.server,
				user=settings.user,
				password=settings.password,
				database=settings.database,
				login_timeout=settings.login_timeout,
				timeout=settings.timeout,
				charset=settings.charset
			)

		cursor = conn.cursor()
		if params:
			cursor.execute(actual_query, params)
		else:
			cursor.execute(actual_query)

		rows = cursor.fetchall()
		columns = [col[0] for col in cursor.description] if cursor.description else []
		dctResult.columns = columns

		if as_dict and rows and columns:
			dctResult.data = [dict(zip(columns, row)) for row in rows]
		else:
			dctResult.data = rows

		dctResult.row_count = len(rows)
		dctResult.op_result = True
		dctResult.op_message = "Query executed successfully. {0} row(s) returned.".format(dctResult.row_count)

		if should_log:
			_log_query(query, actual_query, params, dctResult.data, dctResult.row_count, columns)

	except pymssql.Error as e:
		dctResult.op_message = "Database error: {0}".format(str(e))
		frappe.log_error("LOGO DB Query Error", frappe.get_traceback())
		if should_log:
			_log_query(query, actual_query or "", params, [], 0, [], error_message=str(e))

	except Exception as e:
		dctResult.op_message = "Unexpected error: {0}".format(str(e))
		frappe.log_error("LOGO DB Query Error", frappe.get_traceback())
		if should_log:
			_log_query(query, actual_query or "", params, [], 0, [], error_message=str(e))

	finally:
		if owns_connection and conn:
			conn.close()

	return dctResult


# ---------------------------------------------------------------------------
# Connection test
# ---------------------------------------------------------------------------

def test_connection():
	"""Verify that the configured LOGO SQL Server is reachable.

	Returns
	-------
	frappe._dict with keys: op_result, op_message, server_info.
	"""
	dctResult = frappe._dict({
		"op_result": False,
		"op_message": "",
		"server_info": {},
	})

	try:
		settings = get_logo_db_settings()

		with get_logo_connection() as conn:
			cursor = conn.cursor()

			cursor.execute("SELECT @@VERSION")
			version = cursor.fetchone()

			cursor.execute("SELECT DB_NAME()")
			database = cursor.fetchone()

		dctResult.op_result = True
		dctResult.op_message = "Connection successful"
		dctResult.server_info = {
			"server": settings.server,
			"database": database[0] if database else settings.database,
			"version": version[0] if version else "Unknown",
		}

	except pymssql.Error as e:
		dctResult.op_message = "Connection failed: {0}".format(str(e))
		frappe.log_error("LOGO DB Connection Test Failed", frappe.get_traceback())

	except Exception as e:
		dctResult.op_message = "Unexpected error: {0}".format(str(e))
		frappe.log_error("LOGO DB Connection Test Failed", frappe.get_traceback())

	return dctResult


