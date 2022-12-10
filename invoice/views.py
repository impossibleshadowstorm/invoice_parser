from rest_framework import viewsets
from invoice.models import Invoice
from invoice.serializers import InvoiceSerializer


class UploadInvoiceViewSet(viewsets.ModelViewSet):
    """
    Django REST viewset to handle API requests
    """

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
