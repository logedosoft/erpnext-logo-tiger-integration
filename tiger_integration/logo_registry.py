# -*- coding: utf-8 -*-
# LOGEDOSOFT
# Central registry for LOGO entity types, table names, and DataType constants.

import frappe
from enum import IntEnum


class LogoDataType(IntEnum):
	"""LOGO Object Service DataType numbers for each entity."""
	ITEM = 0
	CUSTOMER = 30
	SUPPLIER = 30


# Mapping of ERPNext doctype -> LOGO metadata
LOGO_ENTITY_REGISTRY = {
	"Item": {
		"data_type": LogoDataType.ITEM,
		"table_template": "LG_{firm_no:03d}_ITEMS",
	},
	"Customer": {
		"data_type": LogoDataType.CUSTOMER,
		"table_template": "LG_{firm_no:03d}_CLCARD",
	},
	"Supplier": {
		"data_type": LogoDataType.SUPPLIER,
		"table_template": "LG_{firm_no:03d}_CLCARD",
	},
}


def _get_settings():
	"""Return the cached LOGO Object Service Settings singleton."""
	return frappe.get_doc("LOGO Object Service Settings")


def get_firm_no(settings=None):
	"""Return the LOGO company/firm number as an integer.

	Reads from the ``logo_company_no`` field of *LOGO Object Service Settings*.
	"""
	if settings is None:
		settings = _get_settings()
	return int(settings.logo_company_no or 1)


def get_security_code(settings=None):
	"""Return the LOGO Object Service security GUID from settings."""
	if settings is None:
		settings = _get_settings()
	return settings.lobject_service_client_secret


def get_data_type(entity_type):
	"""Return the LOGO DataType number for a given ERPNext doctype.

	Args:
		entity_type: ERPNext doctype name (e.g. ``"Item"``, ``"Customer"``).

	Returns:
		int – the DataType constant.

	Raises:
		ValueError: if *entity_type* is not in the registry.
	"""
	entry = LOGO_ENTITY_REGISTRY.get(entity_type)
	if entry is None:
		raise ValueError(f"Unknown LOGO entity type: {entity_type}")
	return int(entry["data_type"])


def get_table_name(entity_type, firm_no=None, settings=None):
	"""Return the formatted LOGO SQL table name for a given entity type.

	Args:
		entity_type: ERPNext doctype name.
		firm_no: Optional firm number override; defaults to settings value.
		settings: Optional pre-fetched settings document.

	Returns:
		str – e.g. ``"LG_001_ITEMS"``.
	"""
	entry = LOGO_ENTITY_REGISTRY.get(entity_type)
	if entry is None:
		raise ValueError(f"Unknown LOGO entity type: {entity_type}")
	if firm_no is None:
		firm_no = get_firm_no(settings)
	return entry["table_template"].format(firm_no=firm_no)
