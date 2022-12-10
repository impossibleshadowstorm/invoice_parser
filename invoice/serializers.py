from rest_framework import serializers
from invoice.models import Invoice
from invoice.utils import DataExtraction, DataParser


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Custom User serializer
    """

    class Meta:
        model = Invoice
        fields = "__all__"

    def create(self, validated_data):
        file_content = validated_data.get("file_path")
        data_extractor = DataExtraction(file_path=None, file_content=file_content.read())
        response = data_extractor.pdf_to_text_using_fitz()
        data = {}
        if len(response) > 0:
            parser = DataParser(response, parser="fitz-annotation-parser")
            data = parser.parse()
        else:
            response = data_extractor.pdf_to_img_to_text()
            # parser = DataParser(response, parser="simple-text-parser")
            # data = parser.parse()
        print(data, "data--")
        return validated_data
