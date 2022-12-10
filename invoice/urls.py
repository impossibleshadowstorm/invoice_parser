from django.urls import path, include
from rest_framework.routers import DefaultRouter

from invoice.views import UploadInvoiceViewSet


router = DefaultRouter()

router.register("", UploadInvoiceViewSet, basename="upload-invoice")


urlpatterns = [
    path("", include(router.urls)),
]
