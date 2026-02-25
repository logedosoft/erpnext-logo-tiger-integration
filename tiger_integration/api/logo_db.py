# -*- coding: utf-8 -*-
# Copyright (c) 2023, LOGEDO
# License: GNU General Public License v3. See license.txt

"""
LOGO Database Query Module

This module provides a clean interface for querying LOGO SQL Server database.
It handles connection management, query execution, and returns results in a
consistent format.

Table Name Patterns:
    LOGO uses different table name patterns:
    
    1. Period-specific tables (company + period):
       Pattern: LG_{COMPANY}_{PERIOD}_{TABLENAME}
       Example: LG_001_01_INVOICE, LG_001_01_STLINE
       
    2. Company-specific tables (company only, no period):
       Pattern: LG_{COMPANY}_{TABLENAME}
       Example: LG_001_CLCARD, LG_001_ITEMS
       
    3. General tables (no company or period):
       Pattern: L_{TABLENAME}
       Example: L_CAPIFIRM, L_CAPIPERIOD

Placeholder Usage:
    You can use placeholders in your queries:
    - {INVOICE} -> LG_{COMPANY}_{PERIOD}_INVOICE (period-specific)
    - {CLCARD} -> LG_{COMPANY}_CLCARD (company-specific)
    - {CAPIFIRM} -> L_CAPIFIRM (general)
    
    The module automatically replaces placeholders based on LOGO_TABLE_MAP patterns.

Example usage:

    # Period-specific table query
    query = "SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(ref)s"
    result = execute_query(query, company="001", period="01", params={"ref": 123})
    
    # Company-specific table query
    query = "SELECT DEFINITION_ FROM {CLCARD} WHERE LOGICALREF = %(ref)s"
    result = execute_query(query, company="001", params={"ref": 123})
    
    # General table query
    query = "SELECT * FROM {CAPIFIRM} WHERE NR = %(nr)s"
    result = execute_query(query, params={"nr": 1})

Connection Reuse (Performance Optimization):
    For multiple queries in sequence, use the context manager to avoid
    connection overhead:
    
    # Using context manager for multiple queries
    with get_logo_connection() as conn:
        result1 = execute_query_with_conn(conn, "SELECT ...", company="001")
        result2 = execute_query_with_conn(conn, "SELECT ...", company="001")
        # Connection stays open for both queries
    
    # Using batch query function
    queries = [
        ("SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(ref)s", {"ref": 123}),
        ("SELECT DEFINITION_ FROM {CLCARD} WHERE LOGICALREF = %(ref)s", {"ref": 456}),
    ]
    results = execute_queries(queries, company="001", period="01")
"""

import frappe
import pymssql
from contextlib import contextmanager
from frappe import _


# LOGO Table Map: Maps placeholder names to (table_name, table_pattern)
# table_pattern contains placeholders:
#   - {COMPANY}: Will be replaced with normalized company number (3-digit)
#   - {PERIOD}: Will be replaced with normalized period number (2-digit)
#   - If no placeholders, the pattern is used as-is
LOGO_TABLE_MAP = {
    # Period-specific tables (transaction data that varies by period)
    # Pattern: LG_{COMPANY}_{PERIOD}_{TABLE}
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
    
    # Company-specific tables (master data, no period)
    # Pattern: LG_{COMPANY}_{TABLE}
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
    
    # General tables (system-wide, no company or period)
    # Pattern: L_{TABLE}
    "CAPIFIRM": ("CAPIFIRM", "L_CAPIFIRM"),
    "CAPIPERIOD": ("CAPIPERIOD", "L_CAPIPERIOD"),
    "CITY": ("CITY", "L_CITY"),
    "COUNTRY": ("COUNTRY", "L_COUNTRY"),
    "POSTCODE": ("POSTCODE", "L_POSTCODE"),
}


def get_logo_db_settings():
    """
    Get LOGO SQL Settings from DocType.
    
    Returns:
        frappe._dict: Settings dict with server, user, password, database
    """
    docSettings = frappe.get_doc("LOGO SQL Settings")
    docSettings.check_permission("read")
    
    return frappe._dict({
        "server": docSettings.sql_server_address,
        "user": docSettings.sql_user_name,
        "password": docSettings.get_password("sql_user_password") if docSettings.sql_user_password else "",
        "database": docSettings.sql_database_name,
        "login_timeout": 10,
        "timeout": 30
    })


def _normalize_company(company):
    """
    Normalize company number to 3-digit format.
    
    Args:
        company (str|int): Company number (e.g., 1, "1", "01", "001")
    
    Returns:
        str: 3-digit company number (e.g., "001")
    """
    if isinstance(company, int):
        company = str(company)
    
    company = str(company).strip()
    
    if len(company) == 1:
        return f"00{company}"
    elif len(company) == 2:
        return f"0{company}"
    
    return company


def _normalize_period(period):
    """
    Normalize period number to 2-digit format.
    
    Args:
        period (str|int): Period number (e.g., 1, "1", "01")
    
    Returns:
        str: 2-digit period number (e.g., "01")
    """
    if isinstance(period, int):
        period = str(period)
    
    period = str(period).strip()
    
    if len(period) == 1:
        return f"0{period}"
    
    return period


def build_table_name(table_key, company=None, period=None):
    """
    Build LOGO table name based on table pattern.
    
    Args:
        table_key (str): Table key like "INVOICE", "ITEMS", "CLCARD", "CAPIFIRM"
        company (str|int, optional): LOGO company number (e.g., "001", "01", 1)
        period (str, optional): Period number (e.g., "01"). Default None.
    
    Returns:
        str: Full table name
    
    Example:
        # Period-specific table
        build_table_name("INVOICE", "001", "01")  # Returns "LG_001_01_INVOICE"
        
        # Company-specific table
        build_table_name("CLCARD", "001")  # Returns "LG_001_CLCARD"
        
        # General table
        build_table_name("CAPIFIRM")  # Returns "L_CAPIFIRM"
    """
    # Get table info from mapping
    table_key_upper = table_key.upper()
    
    if table_key_upper not in LOGO_TABLE_MAP:
        # Unknown table - default to period-specific pattern
        if company:
            normalized_company = _normalize_company(company)
            if period:
                normalized_period = _normalize_period(period)
                return f"LG_{normalized_company}_{normalized_period}_{table_key_upper}"
            else:
                return f"LG_{normalized_company}_{table_key_upper}"
        else:
            return f"L_{table_key_upper}"
    
    table_name, table_pattern = LOGO_TABLE_MAP[table_key_upper]
    
    # Replace placeholders in pattern
    result = table_pattern
    
    # Replace {COMPANY} placeholder
    if "{COMPANY}" in result:
        if not company:
            frappe.throw(_("Company is required for table: {0}").format(table_key))
        normalized_company = _normalize_company(company)
        result = result.replace("{COMPANY}", normalized_company)
    
    # Replace {PERIOD} placeholder
    if "{PERIOD}" in result:
        normalized_period = _normalize_period(period or "01")
        result = result.replace("{PERIOD}", normalized_period)
    
    return result


def replace_table_placeholders(query, company=None, period=None):
    """
    Replace table placeholders in query with actual table names.
    
    Args:
        query (str): SQL query with placeholders like {INVOICE}, {CLCARD}
        company (str|int, optional): LOGO company number
        period (str, optional): Period number. Default "01" for period-specific tables.
    
    Returns:
        str: Query with replaced table names
    
    Example:
        # Period-specific table
        query = "SELECT * FROM {INVOICE} WHERE LOGICALREF = 1"
        result = replace_table_placeholders(query, "001", "01")
        # Result: "SELECT * FROM LG_001_01_INVOICE WHERE LOGICALREF = 1"
        
        # Company-specific table
        query = "SELECT * FROM {CLCARD} WHERE LOGICALREF = 1"
        result = replace_table_placeholders(query, "001")
        # Result: "SELECT * FROM LG_001_CLCARD WHERE LOGICALREF = 1"
        
        # General table
        query = "SELECT * FROM {CAPIFIRM} WHERE NR = 1"
        result = replace_table_placeholders(query)
        # Result: "SELECT * FROM L_CAPIFIRM WHERE NR = 1"
    """
    import re
    
    # Find all placeholders like {TABLENAME}
    placeholder_pattern = r'\{([A-Za-z_][A-Za-z0-9_]*)\}'
    
    def replace_match(match):
        table_key = match.group(1)
        return build_table_name(table_key, company, period)
    
    return re.sub(placeholder_pattern, replace_match, query)


def execute_query(query, company=None, period=None, params=None, as_dict=True):
    """
    Execute a SQL query on LOGO database and return results.
    
    This function replaces table placeholders like {INVOICE} with actual
    table names based on the table pattern in LOGO_TABLE_MAP.
    
    Args:
        query (str): SQL query with table placeholders (e.g., {INVOICE}, {CLCARD})
        company (str|int, optional): LOGO company number (e.g., "001", "01", 1)
        period (str, optional): Period number. Default "01" for period-specific tables.
        params (dict, optional): Parameters for parameterized query
        as_dict (bool, optional): Return results as dict. Default True.
    
    Returns:
        frappe._dict: Result object with:
            - op_result (bool): True if successful, False otherwise
            - op_message (str): Success/error message
            - data (list): List of rows (as dict or tuple based on as_dict)
            - row_count (int): Number of rows returned
            - columns (list): List of column names
            - query (str): The executed query (with replaced table names)
    
    Example:
        # Period-specific table query
        result = execute_query(
            "SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(ref)s",
            company="001",
            period="01",
            params={"ref": 123}
        )
        if result.op_result:
            guid = result.data[0].get("GUID") if result.data else None
        
        # Company-specific table query
        result = execute_query(
            "SELECT DEFINITION_ FROM {CLCARD} WHERE LOGICALREF = %(ref)s",
            company="001",
            params={"ref": 123}
        )
        
        # General table query
        result = execute_query(
            "SELECT * FROM {CAPIFIRM} WHERE NR = %(nr)s",
            params={"nr": 1}
        )
    """
    dctResult = frappe._dict({
        "op_result": False,
        "op_message": "",
        "data": [],
        "row_count": 0,
        "columns": [],
        "query": ""
    })
    
    conn = None
    
    try:
        # Replace table placeholders
        actual_query = replace_table_placeholders(query, company, period)
        dctResult.query = actual_query
        
        # Get settings
        settings = get_logo_db_settings()
        
        # Connect to LOGO SQL Server
        conn = pymssql.connect(
            server=settings.server,
            user=settings.user,
            password=settings.password,
            database=settings.database,
            login_timeout=settings.login_timeout,
            timeout=settings.timeout,
        )
        
        cursor = conn.cursor()
        
        # Execute query
        if params:
            cursor.execute(actual_query, params)
        else:
            cursor.execute(actual_query)
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Get column names from cursor description
        columns = []
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            dctResult.columns = columns
        
        # Convert to dict if requested
        if as_dict and rows and columns:
            dctResult.data = [
                dict(zip(columns, row))
                for row in rows
            ]
        else:
            dctResult.data = rows
        
        dctResult.row_count = len(rows)
        dctResult.op_result = True
        dctResult.op_message = f"Query executed successfully. {dctResult.row_count} row(s) returned."
        
    except pymssql.Error as e:
        dctResult.op_message = f"Database error: {str(e)}"
        frappe.log_error(frappe.get_traceback(), f"LOGO DB Query Error: {query[:100]}")
    
    except Exception as e:
        dctResult.op_message = f"Unexpected error: {str(e)}"
        frappe.log_error(frappe.get_traceback(), f"LOGO DB Query Error: {query[:100]}")
    
    finally:
        if conn:
            conn.close()
    
    return dctResult


@contextmanager
def get_logo_connection():
    """
    Context manager for LOGO database connection.
    
    Use this when you need to execute multiple queries in sequence
    to avoid the overhead of creating a new connection for each query.
    
    Yields:
        pymssql.Connection: Database connection object
    
    Example:
        with get_logo_connection() as conn:
            result1 = execute_query_with_conn(conn, "SELECT ...", company="001")
            result2 = execute_query_with_conn(conn, "SELECT ...", company="001")
        # Connection is automatically closed when exiting the context
    
    Raises:
        pymssql.Error: If connection fails
    """
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
        )
        yield conn
    finally:
        if conn:
            conn.close()


def execute_query_with_conn(conn, query, company=None, period=None, params=None, as_dict=True):
    """
    Execute a SQL query using an existing LOGO database connection.
    
    Use this with get_logo_connection() context manager for multiple queries.
    
    Args:
        conn (pymssql.Connection): Existing database connection
        query (str): SQL query with table placeholders (e.g., {INVOICE}, {CLCARD})
        company (str|int, optional): LOGO company number (e.g., "001", "01", 1)
        period (str, optional): Period number. Default "01" for period-specific tables.
        params (dict, optional): Parameters for parameterized query
        as_dict (bool, optional): Return results as dict. Default True.
    
    Returns:
        frappe._dict: Result object with:
            - op_result (bool): True if successful, False otherwise
            - op_message (str): Success/error message
            - data (list): List of rows (as dict or tuple based on as_dict)
            - row_count (int): Number of rows returned
            - columns (list): List of column names
            - query (str): The executed query (with replaced table names)
    
    Example:
        with get_logo_connection() as conn:
            # First query
            result1 = execute_query_with_conn(
                conn,
                "SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(ref)s",
                company="001",
                period="01",
                params={"ref": 123}
            )
            
            # Second query using same connection
            if result1.op_result and result1.data:
                guid = result1.data[0].get("GUID")
                result2 = execute_query_with_conn(
                    conn,
                    "SELECT * FROM {STLINE} WHERE INVOICEREF = %(ref)s",
                    company="001",
                    period="01",
                    params={"ref": 123}
                )
    """
    dctResult = frappe._dict({
        "op_result": False,
        "op_message": "",
        "data": [],
        "row_count": 0,
        "columns": [],
        "query": ""
    })
    
    try:
        # Replace table placeholders
        actual_query = replace_table_placeholders(query, company, period)
        dctResult.query = actual_query
        
        cursor = conn.cursor()
        
        # Execute query
        if params:
            cursor.execute(actual_query, params)
        else:
            cursor.execute(actual_query)
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Get column names from cursor description
        columns = []
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            dctResult.columns = columns
        
        # Convert to dict if requested
        if as_dict and rows and columns:
            dctResult.data = [
                dict(zip(columns, row))
                for row in rows
            ]
        else:
            dctResult.data = rows
        
        dctResult.row_count = len(rows)
        dctResult.op_result = True
        dctResult.op_message = f"Query executed successfully. {dctResult.row_count} row(s) returned."
        
    except pymssql.Error as e:
        dctResult.op_message = f"Database error: {str(e)}"
        frappe.log_error(frappe.get_traceback(), f"LOGO DB Query Error: {query[:100]}")
    
    except Exception as e:
        dctResult.op_message = f"Unexpected error: {str(e)}"
        frappe.log_error(frappe.get_traceback(), f"LOGO DB Query Error: {query[:100]}")
    
    return dctResult


def execute_queries(queries, company=None, period=None, as_dict=True):
    """
    Execute multiple SQL queries using a single LOGO database connection.
    
    This is a convenience function that wraps get_logo_connection() and
    execute_query_with_conn() for batch query execution.
    
    Args:
        queries (list): List of query tuples, each containing:
            - query (str): SQL query with table placeholders
            - params (dict|None): Parameters for parameterized query (or None)
        company (str|int, optional): LOGO company number (e.g., "001", "01", 1)
        period (str, optional): Period number. Default "01" for period-specific tables.
        as_dict (bool, optional): Return results as dict. Default True.
    
    Returns:
        list: List of result objects (same order as input queries), each containing:
            - op_result (bool): True if successful, False otherwise
            - op_message (str): Success/error message
            - data (list): List of rows (as dict or tuple based on as_dict)
            - row_count (int): Number of rows returned
            - columns (list): List of column names
            - query (str): The executed query (with replaced table names)
    
    Example:
        queries = [
            ("SELECT GUID FROM {INVOICE} WHERE LOGICALREF = %(ref)s", {"ref": 123}),
            ("SELECT DEFINITION_ FROM {CLCARD} WHERE LOGICALREF = %(ref)s", {"ref": 456}),
            ("SELECT * FROM {CAPIFIRM} WHERE NR = %(nr)s", {"nr": 1}),
        ]
        
        results = execute_queries(queries, company="001", period="01")
        
        for i, result in enumerate(results):
            if result.op_result:
                print(f"Query {i+1}: {result.row_count} rows")
            else:
                print(f"Query {i+1} failed: {result.op_message}")
    """
    results = []
    
    try:
        with get_logo_connection() as conn:
            for query_item in queries:
                # Handle both tuple and single query string
                if isinstance(query_item, tuple):
                    if len(query_item) >= 2:
                        query, params = query_item[0], query_item[1]
                    else:
                        query, params = query_item[0], None
                else:
                    query = query_item
                    params = None
                
                result = execute_query_with_conn(
                    conn,
                    query,
                    company=company,
                    period=period,
                    params=params,
                    as_dict=as_dict
                )
                results.append(result)
    
    except pymssql.Error as e:
        # Connection failed - return error for all queries
        error_result = frappe._dict({
            "op_result": False,
            "op_message": f"Connection error: {str(e)}",
            "data": [],
            "row_count": 0,
            "columns": [],
            "query": ""
        })
        
        # Fill results with error for each query
        for query_item in queries:
            query = query_item[0] if isinstance(query_item, tuple) else query_item
            err_result = error_result.copy()
            err_result.query = query
            results.append(err_result)
        
        frappe.log_error(frappe.get_traceback(), "LOGO DB Batch Query Connection Error")
    
    except Exception as e:
        # Unexpected error - return error for all queries
        error_result = frappe._dict({
            "op_result": False,
            "op_message": f"Unexpected error: {str(e)}",
            "data": [],
            "row_count": 0,
            "columns": [],
            "query": ""
        })
        
        for query_item in queries:
            query = query_item[0] if isinstance(query_item, tuple) else query_item
            err_result = error_result.copy()
            err_result.query = query
            results.append(err_result)
        
        frappe.log_error(frappe.get_traceback(), "LOGO DB Batch Query Error")
    
    return results


def test_connection():
    """
    Test connection to LOGO database.
    
    Returns:
        frappe._dict: Result object with:
            - op_result (bool): True if connection successful
            - op_message (str): Success/error message
            - server_info (dict): Server information if connected
    """
    dctResult = frappe._dict({
        "op_result": False,
        "op_message": "",
        "server_info": {}
    })
    
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
        )
        
        cursor = conn.cursor()
        
        # Get SQL Server version
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        
        # Get current database
        cursor.execute("SELECT DB_NAME()")
        database = cursor.fetchone()
        
        dctResult.op_result = True
        dctResult.op_message = "Connection successful"
        dctResult.server_info = {
            "server": settings.server,
            "database": database[0] if database else settings.database,
            "version": version[0] if version else "Unknown"
        }
        
    except pymssql.Error as e:
        dctResult.op_message = f"Connection failed: {str(e)}"
        frappe.log_error(frappe.get_traceback(), "LOGO DB Connection Test Failed")
    
    except Exception as e:
        dctResult.op_message = f"Unexpected error: {str(e)}"
        frappe.log_error(frappe.get_traceback(), "LOGO DB Connection Test Failed")
    
    finally:
        if conn:
            conn.close()
    
    return dctResult
