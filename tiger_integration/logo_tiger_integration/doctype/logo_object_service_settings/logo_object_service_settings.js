// Copyright (c) 2025, Logedosoft Business Solutions and contributors
// For license information, please see license.txt
frappe.ui.form.on('LOGO Object Service Settings', {
	refresh(frm) {
		// your code here
	},
	sales_invoice(frm) {
		// Trigger e-invoice PDF download when sales_invoice field is set
		if (frm.doc.sales_invoice) {
			frappe.call({
				method: "tiger_integration.api.logo_sync.download_einvoice_pdf",
				args: {
					sales_invoice_name: frm.doc.sales_invoice
				},
				freeze: true,
				freeze_message: __("Logedo is running..."),
				callback: function(r) {
					if (r.exc || !r.message) return;
					
					var result = r.message;
					
					// Build step-by-step message for popup
					var step_html = "<div style='max-height: 400px; overflow-y: auto;'>";
					step_html += "<table class='table table-bordered' style='margin: 0;'>";
					step_html += "<thead><tr><th>" + __("Step") + "</th><th>" + __("Status") + "</th><th>" + __("Message") + "</th></tr></thead>";
					step_html += "<tbody>";
					
					for (var i = 0; i < result.steps.length; i++) {
						var step = result.steps[i];
						var status_icon;
						
						if (step.status === "success") {
							status_icon = "<span style='color: green;'>✓</span>";
						} else if (step.status === "error") {
							status_icon = "<span style='color: red;'>✗</span>";
						} else {
							status_icon = "<span style='color: blue;'>ℹ</span>";
						}
						
						step_html += "<tr>";
						step_html += "<td>" + step.step + "</td>";
						step_html += "<td style='text-align: center;'>" + status_icon + "</td>";
						step_html += "<td>" + step.message + "</td>";
						step_html += "</tr>";
					}
					
					step_html += "</tbody></table></div>";
					
					// Show result in dialog
					var dialog = new frappe.ui.Dialog({
						title: result.op_result 
							? __("e-Invoice PDF Download Successful") 
							: __("e-Invoice PDF Download Failed"),
						fields: [
							{
								fieldtype: "HTML",
								fieldname: "steps_html",
								options: step_html
							}
						],
						primary_action_label: __("Close"),
						primary_action: function() {
							dialog.hide();
						}
					});
					
					dialog.show();
				}
			});
		}
	}
})