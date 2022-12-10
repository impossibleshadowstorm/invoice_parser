from django.db import models
from common.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from invoice.utils import DataExtraction, DataParser


class Invoice(TimeStampedModel):
    company_name = models.CharField(max_length=255, null=True, default=None, blank=True)
    company_state = models.CharField(
        max_length=255, null=True, default=None, blank=True
    )
    company_state_cd = models.CharField(
        max_length=255, null=True, default=None, blank=True
    )
    vendor_name = models.CharField(max_length=255, null=True, default=None, blank=True)
    vendor_state = models.CharField(max_length=255, null=True, default=None, blank=True)
    vendor_state_code = models.CharField(
        max_length=255, null=True, default=None, blank=True
    )
    invoice_date = models.CharField(max_length=255, null=True, default=None, blank=True)
    invoice_no = models.CharField(max_length=255, null=True, default=None, blank=True)
    po_no = models.CharField(max_length=255, null=True, default=None, blank=True)
    sgst_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    sgst_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    cgst_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    cgst_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    igst_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    igst_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    basic_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tbl_description = models.TextField(blank=True)
    tbl_hsn_code = models.CharField(max_length=255, null=True, default=None, blank=True)
    tbl_qty = models.IntegerField(null=True, default=None, blank=True)
    tbl_unit = models.IntegerField(null=True, default=None, blank=True)
    tbl_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tble_cgst_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tble_cgst_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tble_sgst_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tble_sgst_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tble_igst_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tble_igst_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    tbl_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, default=None, blank=True
    )
    company_gst = models.CharField(max_length=255, null=True, default=None, blank=True)
    vendor_gst = models.CharField(max_length=255, null=True, default=None, blank=True)
    result = models.CharField(max_length=255, null=True, default=None, blank=True)
    file_path = models.FileField(blank=True)
    has_error = models.BooleanField(default=False, blank=True)
    error = models.TextField(blank=True)


class InvoiceFile(TimeStampedModel):
    invoice = models.ForeignKey(
        Invoice, null=True, default=None, blank=True, on_delete=models.CASCADE
    )
    file_path = models.FileField(blank=True)


@receiver(post_save, sender=InvoiceFile, dispatch_uid="parse_invoice")
def parse_invoice(sender, instance, **kwargs):
    file_content = instance.file_path
    data_extractor = DataExtraction(file_path=None, file_content=file_content.read())
    response = data_extractor.pdf_to_text_using_fitz()
    data = {}
    if len(response) > 0:
        parser = DataParser(response, parser="fitz-annotation-parser")
        data = parser.parse()
    else:
        response = data_extractor.pdf_to_img_to_text()
        print(response)
        parser = DataParser(response, parser="simple-text-parser")
        data = parser.parse()
    print(data)
    Invoice.objects.create(**data)
