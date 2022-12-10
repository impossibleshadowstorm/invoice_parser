from django.contrib import admin
from invoice.models import Invoice, InvoiceFile
from import_export.admin import ImportExportModelAdmin


class CustomInvoiceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = (
        "company_name",
        "company_state",
        "company_state_cd",
        "vendor_name",
        "vendor_state",
        "vendor_state_code",
        "invoice_date",
        "invoice_no",
        "po_no",
        "company_gst",
        "vendor_gst",
        "igst_amount",
        "cgst_amount",
        "sgst_amount",
        "basic_amount",
        "total_amount",
    )

    search_fields = (
        "company_name",
        "company_state",
    )
    
    ordering = ("company_name",)


admin.site.register(Invoice, CustomInvoiceAdmin,)
admin.site.register(InvoiceFile)
