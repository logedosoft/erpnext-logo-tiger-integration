"""
Scheduled Tasks for Tiger Integration

This module contains scheduled background tasks for the Tiger Integration app.
"""

import frappe
import time
from tiger_integration.api.logo_sync import download_einvoice_pdf


def download_einvoice_pdfs():
    """
    Scheduled task to download e-invoice PDFs for submitted Sales Invoices.
    Runs hourly via scheduler_events.
    
    Process:
    1. Check if enable_elogo_pdf_attachments_for_invoices is enabled in LOGO Object Service Settings
    2. Find submitted Sales Invoices with LOGO reference but no ELOGO_INVOICE attachment
    3. Process in batches (max 20 per run)
    4. Use frappe.enqueue for each invoice to ensure non-blocking execution
    5. Include rate limiting between API calls
    """
    # Check if the feature is enabled in LOGO Object Service Settings
    if not frappe.db.get_single_value(
        "LOGO Object Service Settings", 
        "enable_elogo_pdf_attachments_for_invoices"
    ):
        # Feature is disabled, stop execution
        return
    # Get eligible invoices
    invoices = frappe.db.sql("""
        SELECT si.name
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
        AND si.custom_ld_logo_ref_no IS NOT NULL
        AND si.custom_ld_logo_ref_no != ''
        AND NOT EXISTS (
            SELECT 1 FROM `tabFile` f
            WHERE f.attached_to_doctype = 'Sales Invoice'
            AND f.attached_to_name = si.name
            AND f.file_name LIKE '%ELOGO_INVOICE%'
        )
        ORDER BY si.creation DESC
        LIMIT 20
    """, as_dict=True)
    
    if not invoices:
        return
    
    for invoice in invoices:
        # Enqueue each invoice processing as separate job
        frappe.enqueue(
            process_single_einvoice_download,
            queue="long",
            timeout=300,
            invoice_name=invoice.name,
            is_async=True,
            enqueue_after_commit=True
        )
        
        # Small delay to prevent queue flooding
        time.sleep(0.5)


def process_single_einvoice_download(invoice_name):
    """
    Process a single e-invoice PDF download.
    Called via frappe.enqueue for non-blocking execution.
    
    Args:
        invoice_name (str): Name of the Sales Invoice to process
    """
    try:
        result = download_einvoice_pdf(invoice_name)
        
        if result.get("op_result"):
            frappe.log_error(
                f"Successfully downloaded e-invoice PDF for {invoice_name}",
                "eInvoice PDF Download Success"
            )
        else:
            frappe.log_error(
                f"Failed to download e-invoice PDF for {invoice_name}: {result.get('op_message')}",
                "eInvoice PDF Download Failed"
            )
            
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            f"eInvoice PDF Download Error - {invoice_name}"
        )
