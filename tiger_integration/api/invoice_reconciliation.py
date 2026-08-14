# -*- coding: utf-8 -*-
"""
Invoice Reconciliation: ERPNext Sales Invoice vs LOGO Tiger

Finds Sales Invoices that have a corresponding LOGO record
and identifies those with mismatched totals.
"""

import csv
import io
import re

import frappe
from frappe import _
from tiger_integration.api.logo_db import execute_query


@frappe.whitelist()
def reconcile_sales_invoices_with_logo(period="01", from_date=None, to_date=None):
	"""
	Reconcile ERPNext Sales Invoices with LOGO Tiger invoice totals.

	Scans all submitted Sales Invoices that carry a LOGO reference
	(``custom_ld_logo_ref_no``) and compares ``grand_total`` against
	the ``NETTOTAL`` stored in LOGO.

	Field mapping:
	  ERPNext ``grand_total``    ↔ LOGO ``NETTOTAL``
	  ERPNext ``total``          ↔ LOGO ``GROSSTOTAL``
	  ERPNext ``total_taxes``    ↔ LOGO ``TOTALVAT``

	:param period: LOGO fiscal period, zero-padded to 2 digits (default ``01``)
	:param from_date: Filter invoices from this date (YYYY-MM-DD)
	:param to_date: Filter invoices to this date (YYYY-MM-DD)
	:returns: ``frappe._dict`` with matched / mismatched / missing / duplicate_refs lists
	"""
	if not re.match(r"^\d{1,2}$", str(period)):
		frappe.throw(_("Invalid LOGO period: {0}").format(period))

	dctResult = frappe._dict({
		"op_result": True,
		"op_message": "",
		"matched": [],
		"mismatched": [],
		"missing_in_logo": [],
		"duplicate_refs": [],
		"errors": [],
		"total_checked": 0,
	})

	try:
		settings = frappe.get_doc("LOGO Object Service Settings")
		company = settings.logo_company_no

		# 1. Collect ERPNext invoices that have a LOGO reference
		query = """
			SELECT
				name,
				grand_total,
				base_grand_total,
				total AS erp_net_total,
				base_total AS erp_base_net_total,
				total_taxes_and_charges AS erp_vat_total,
				base_total_taxes_and_charges AS erp_base_vat_total,
				custom_ld_logo_ref_no,
				posting_date,
				customer,
				currency
			FROM `tabSales Invoice`
			WHERE docstatus = 1
			  AND custom_ld_logo_ref_no IS NOT NULL
			  AND custom_ld_logo_ref_no != ''
		"""
		params = {}

		if from_date:
			query += " AND posting_date >= %(from_date)s"
			params["from_date"] = from_date

		if to_date:
			query += " AND posting_date <= %(to_date)s"
			params["to_date"] = to_date

		query += " ORDER BY posting_date DESC"

		invoices = frappe.db.sql(query, params, as_dict=True)

		dctResult.total_checked = len(invoices)

		if not invoices:
			dctResult.op_message = _("No submitted Sales Invoices with LOGO reference found in the selected date range.")
			return dctResult

		# 2. Bulk-fetch LOGO invoice totals in a single query
		logo_refs = [inv.custom_ld_logo_ref_no for inv in invoices]
		placeholders = ",".join(["%s"] * len(logo_refs))

		logo_sql = (
			"SELECT LOGICALREF, GROSSTOTAL, NETTOTAL, TOTALVAT, FICHENO "
			"FROM {INVOICE} WHERE LOGICALREF IN (" + placeholders + ")"
		)

		logo_result = execute_query(
			logo_sql,
			company=company,
			period=period,
			params=tuple(logo_refs),
		)

		logo_lookup = {}
		if logo_result.op_result and logo_result.data:
			for row in logo_result.data:
				logo_lookup[str(row["LOGICALREF"])] = row

		# 3. Detect duplicate LOGO refs before classification
		ref_counter = {}
		for inv in invoices:
			ref = str(inv.custom_ld_logo_ref_no)
			ref_counter.setdefault(ref, []).append(inv.name)

		for ref, inv_names in ref_counter.items():
			if len(inv_names) > 1:
				dctResult.duplicate_refs.append({
					"logo_ref": ref,
					"invoices": ", ".join(inv_names),
					"count": len(inv_names),
					"logo_fiche": logo_lookup.get(ref, {}).get("FICHENO", "") if ref in logo_lookup else "",
				})

		# 4. Classify each invoice
		for inv in invoices:
			logo_ref = str(inv.custom_ld_logo_ref_no)

			if logo_ref not in logo_lookup:
				dctResult.missing_in_logo.append({
					"erpnext_invoice": inv.name,
					"customer": inv.customer,
					"posting_date": str(inv.posting_date),
					"logo_ref": logo_ref,
					"erp_grand_total": flt_str(inv.grand_total),
					"currency": inv.currency or "",
				})
				continue

			logo_row = logo_lookup[logo_ref]
			logo_net = flt(logo_row.get("NETTOTAL", 0) or 0)
			logo_gross = flt(logo_row.get("GROSSTOTAL", 0) or 0)
			logo_vat = flt(logo_row.get("TOTALVAT", 0) or 0)
			erp_grand = flt(inv.base_grand_total or 0)
			erp_net = flt(inv.erp_base_net_total or 0)
			erp_vat = flt(inv.erp_base_vat_total or 0)
			logo_fiche = logo_row.get("FICHENO", "")

			# Compare in base currency (company currency = TRY)
			# ERPNext base_* fields are already in company currency.
			# LOGO NETTOTAL/GROSSTOTAL/TOTALVAT are also in company currency.
			grand_mismatch = abs(logo_net - erp_grand) > 0.01
			net_mismatch = abs(logo_gross - erp_net) > 0.01
			vat_mismatch = abs(logo_vat - erp_vat) > 0.01

			if grand_mismatch or net_mismatch or vat_mismatch:
				dctResult.mismatched.append({
					"erpnext_invoice": inv.name,
					"customer": inv.customer,
					"posting_date": str(inv.posting_date),
					"logo_ref": logo_ref,
					"logo_fiche": logo_fiche,
					"erp_grand_total": round(erp_grand, 2),
					"erp_net_total": round(erp_net, 2),
					"erp_vat_total": round(erp_vat, 2),
					"logo_net_total": round(logo_net, 2),
					"logo_gross_total": round(logo_gross, 2),
					"logo_vat_total": round(logo_vat, 2),
					"grand_difference": round(erp_grand - logo_net, 2),
					"net_difference": round(erp_net - logo_gross, 2),
					"vat_difference": round(erp_vat - logo_vat, 2),
					"currency": inv.currency or "",
					"logo_currency": "TRY",
				})
			else:
				dctResult.matched.append({
					"erpnext_invoice": inv.name,
					"customer": inv.customer,
					"posting_date": str(inv.posting_date),
					"logo_ref": logo_ref,
					"logo_fiche": logo_fiche,
					"erp_grand_total": round(erp_grand, 2),
					"logo_net_total": round(logo_net, 2),
					"currency": inv.currency or "",
					"logo_currency": "TRY",
				})

		dctResult.op_message = (
			_("Checked {0} invoices. Matched: {1}, Mismatched: {2}, Missing in LOGO: {3}, Duplicate Refs: {4}")
			.format(
				dctResult.total_checked,
				len(dctResult.matched),
				len(dctResult.mismatched),
				len(dctResult.missing_in_logo),
				len(dctResult.duplicate_refs),
			)
		)

	except Exception as e:
		dctResult.op_result = False
		dctResult.op_message = _("Reconciliation failed: {0}").format(str(e))
		frappe.log_error(
			title="LOGO Invoice Reconciliation Error",
			message=frappe.get_traceback(),
		)

	return dctResult


@frappe.whitelist()
def export_reconciliation_to_csv(period="01", filter_type="mismatched", from_date=None, to_date=None):
	"""
	Export reconciliation results to CSV format.
	
	:param period: LOGO fiscal period, zero-padded to 2 digits (default ``01``)
	:param filter_type: ``all``, ``matched``, ``mismatched``, or ``missing``
	:param from_date: Filter invoices from this date (YYYY-MM-DD)
	:param to_date: Filter invoices to this date (YYYY-MM-DD)
	:returns: ``frappe._dict`` with csv_data string
	"""
	dctResult = frappe._dict({"op_result": True, "op_message": "", "csv_data": ""})
	try:
		if not re.match(r"^\d{1,2}$", str(period)):
			frappe.throw(_("Invalid LOGO period: {0}").format(period))
		dctRecon = reconcile_sales_invoices_with_logo(period=period, from_date=from_date, to_date=to_date)
		if not dctRecon.op_result:
			dctResult.op_result = False
			dctResult.op_message = dctRecon.op_message
			return dctResult
		dctResult.csv_data = _render_reconciliation_csv(dctRecon, filter_type)
	except frappe.exceptions.ValidationError:
		raise
	except Exception as e:
		dctResult.op_result = False
		dctResult.op_message = _("CSV export failed: {0}").format(str(e))
		frappe.log_error(title="LOGO Reconciliation CSV Export Error", message=frappe.get_traceback())
	return dctResult

def _render_reconciliation_csv(dctRecon, filter_type="mismatched"):
	"""Render reconciliation results to a properly quoted CSV string."""
	buffer = io.StringIO()
	writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
	if filter_type in ("all", "matched"):
		writer.writerow(["=== MATCHED INVOICES ==="])
		writer.writerow(["ERPNext Invoice", "Customer", "Posting Date", "LOGO Ref", "LOGO Fiche",
			"ERP Grand Total", "LOGO Net Total"])
		for row in dctRecon.matched:
			writer.writerow([row.get("erpnext_invoice"), row.get("customer"), row.get("posting_date"),
				row.get("logo_ref"), row.get("logo_fiche"),
				row.get("erp_grand_total"), row.get("logo_net_total")])
	if filter_type in ("all", "mismatched"):
		writer.writerow(["=== MISMATCHED INVOICES ==="])
		writer.writerow(["ERPNext Invoice", "Customer", "Posting Date", "LOGO Ref", "LOGO Fiche",
			"ERP Grand Total", "ERP Net Total", "ERP VAT Total",
			"LOGO Net Total", "LOGO Gross Total", "LOGO VAT Total",
			"Grand Difference", "Net Difference"])
		for row in dctRecon.mismatched:
			writer.writerow([row.get("erpnext_invoice"), row.get("customer"), row.get("posting_date"),
				row.get("logo_ref"), row.get("logo_fiche"),
				row.get("erp_grand_total"), row.get("erp_net_total"), row.get("erp_vat_total"),
				row.get("logo_net_total"), row.get("logo_gross_total"), row.get("logo_vat_total"),
				row.get("grand_difference"), row.get("net_difference")])
	if filter_type in ("all", "missing"):
		writer.writerow(["=== MISSING IN LOGO ==="])
		writer.writerow(["ERPNext Invoice", "Customer", "Posting Date", "LOGO Ref", "ERP Grand Total"])
		for row in dctRecon.missing_in_logo:
			writer.writerow([row.get("erpnext_invoice"), row.get("customer"), row.get("posting_date"),
				row.get("logo_ref"), row.get("erp_grand_total")])
	if filter_type in ("all",):
		writer.writerow(["=== DUPLICATE LOGO REFS ==="])
		writer.writerow(["LOGO Ref", "Invoice Count", "Invoices", "LOGO Fiche"])
		for row in dctRecon.duplicate_refs:
			writer.writerow([row.get("logo_ref"), row.get("count"), row.get("invoices"), row.get("logo_fiche")])
	return buffer.getvalue().rstrip("\n")


def flt(value):
	"""Safely convert to float."""
	if value is None:
		return 0.0
	try:
		return float(value)
	except (TypeError, ValueError):
		return 0.0


def flt_str(value):
	"""Format float to string with 2 decimals."""
	return f"{flt(value):.2f}"
