// Copyright (c) 2025, Logedosoft Business Solutions and contributors
// For license information, please see license.txt
// Updated: 2026-08-14

frappe.query_reports["LOGO Fatura Kontrol"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": "2026-01-01",
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": "2026-08-14",
			"reqd": 1,
		},
		{
			"fieldname": "period",
			"label": "LOGO Period",
			"fieldtype": "Select",
			"options": "01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12\n0",
			"default": "01",
			"reqd": 1,
		},
		{
			"fieldname": "issue_type",
			"label": "Issue Type",
			"fieldtype": "Select",
			"options": "Mismatched\nMissing in LOGO\nDuplicate Refs\nSummary",
			"default": "Mismatched",
			"reqd": 1,
		},
	],
};
