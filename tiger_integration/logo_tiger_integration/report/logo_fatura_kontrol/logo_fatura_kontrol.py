# -*- coding: utf-8 -*-
"""
LOGO Fatura Kontrol Report

Reconciles ERPNext Sales Invoices with LOGO Tiger to find:
- Mismatched totals
- Missing records in LOGO
- Duplicate LOGO references
"""

import frappe
from frappe import _
from tiger_integration.api.invoice_reconciliation import reconcile_sales_invoices_with_logo


def execute(filters=None):
	"""
	Report execution entry point.

	:param filters: dict with from_date, to_date, period, issue_type
	:returns: tuple of (columns, data, message)
	"""
	if not filters:
		filters = frappe._dict()

	# Apply default date range: first day of current year to today
	if not filters.get("from_date"):
		filters.from_date = frappe.utils.get_first_day_of_this_year()
	if not filters.get("to_date"):
		filters.to_date = frappe.utils.get_today()

	# Default LOGO period
	period = filters.get("period") or "01"

	# Run reconciliation
	result = reconcile_sales_invoices_with_logo(
		period=period,
		from_date=filters.from_date,
		to_date=filters.to_date,
	)

	if not result.op_result:
		frappe.log_error(
			title="LOGO Fatura Kontrol Error",
			message=result.op_message,
		)
		return [], [], result.op_message

	# Build report data based on selected issue type
	issue_type = filters.get("issue_type") or "Mismatched"

	if issue_type == "Mismatched":
		columns = get_mismatched_columns()
		data = []
		for row in result.mismatched:
			data.append(frappe._dict({
				"erpnext_invoice": row.get("erpnext_invoice"),
				"customer": row.get("customer"),
				"posting_date": row.get("posting_date"),
				"logo_ref": row.get("logo_ref"),
				"logo_fiche": row.get("logo_fiche"),
				"erp_grand_total": row.get("erp_grand_total"),
				"erp_net_total": row.get("erp_net_total"),
				"erp_vat_total": row.get("erp_vat_total"),
				"logo_net_total": row.get("logo_net_total"),
				"logo_gross_total": row.get("logo_gross_total"),
				"logo_vat_total": row.get("logo_vat_total"),
				"grand_difference": row.get("grand_difference"),
				"net_difference": row.get("net_difference"),
				"vat_difference": row.get("vat_difference"),
				"currency": row.get("currency"),
				"logo_currency": row.get("logo_currency"),
			}))
		message = result.op_message

	elif issue_type == "Missing in LOGO":
		columns = get_missing_columns()
		data = []
		for row in result.missing_in_logo:
			data.append(frappe._dict({
				"erpnext_invoice": row.get("erpnext_invoice"),
				"customer": row.get("customer"),
				"posting_date": row.get("posting_date"),
				"logo_ref": row.get("logo_ref"),
				"erp_grand_total": row.get("erp_grand_total"),
				"currency": row.get("currency"),
			}))
		message = result.op_message

	elif issue_type == "Duplicate Refs":
		columns = get_duplicate_columns()
		data = []
		for row in result.duplicate_refs:
			data.append(frappe._dict({
				"logo_ref": row.get("logo_ref"),
				"invoices": row.get("invoices"),
				"count": row.get("count"),
				"logo_fiche": row.get("logo_fiche"),
			}))
		message = result.op_message

	else:
		columns = get_summary_columns()
		data = []
		data.append(frappe._dict({
			"metric": _("Total Checked"),
			"count": result.total_checked,
		}))
		data.append(frappe._dict({
			"metric": _("Matched"),
			"count": len(result.matched),
		}))
		data.append(frappe._dict({
			"metric": _("Mismatched"),
			"count": len(result.mismatched),
		}))
		data.append(frappe._dict({
			"metric": _("Missing in LOGO"),
			"count": len(result.missing_in_logo),
		}))
		data.append(frappe._dict({
			"metric": _("Duplicate Refs"),
			"count": len(result.duplicate_refs),
		}))
		message = result.op_message

	return columns, data, message


def get_mismatched_columns():
	return [
		{
			"fieldname": "erpnext_invoice",
			"label": _("ERPNext Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150,
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 120,
		},
		{
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "logo_ref",
			"label": _("LOGO Ref"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "logo_fiche",
			"label": _("LOGO Fiche"),
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"fieldname": "erp_grand_total",
			"label": _("ERP Base Grand Total"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 140,
		},
		{
			"fieldname": "erp_net_total",
			"label": _("ERP Base Net Total"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 140,
		},
		{
			"fieldname": "erp_vat_total",
			"label": _("ERP Base VAT"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 120,
		},
		{
			"fieldname": "logo_net_total",
			"label": _("LOGO Net Total"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 120,
		},
		{
			"fieldname": "logo_gross_total",
			"label": _("LOGO Gross Total"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 120,
		},
		{
			"fieldname": "logo_vat_total",
			"label": _("LOGO VAT"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 120,
		},
		{
			"fieldname": "grand_difference",
			"label": _("Grand Difference"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 120,
		},
		{
			"fieldname": "net_difference",
			"label": _("Net Difference"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 120,
		},
		{
			"fieldname": "vat_difference",
			"label": _("VAT Difference"),
			"fieldtype": "Currency",
			"options": "logo_currency",
			"width": 120,
		},
	]


def get_missing_columns():
	return [
		{
			"fieldname": "erpnext_invoice",
			"label": _("ERPNext Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150,
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 120,
		},
		{
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "logo_ref",
			"label": _("LOGO Ref"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "erp_grand_total",
			"label": _("ERP Grand Total"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
	]


def get_duplicate_columns():
	return [
		{
			"fieldname": "logo_ref",
			"label": _("LOGO Ref"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "invoices",
			"label": _("Invoices"),
			"fieldtype": "Data",
			"width": 300,
		},
		{
			"fieldname": "count",
			"label": _("Count"),
			"fieldtype": "Int",
			"width": 70,
		},
		{
			"fieldname": "logo_fiche",
			"label": _("LOGO Fiche"),
			"fieldtype": "Data",
			"width": 140,
		},
	]


def get_summary_columns():
	return [
		{
			"fieldname": "metric",
			"label": _("Metric"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "count",
			"label": _("Count"),
			"fieldtype": "Int",
			"width": 100,
		},
	]
