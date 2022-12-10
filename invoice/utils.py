import os
import fitz
import re
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdf2image import convert_from_bytes
from pytesseract import pytesseract
from invoice.formats import SIMPLE_INVOICE_TEMPLATES, FITZ_INVOICE_TEMPLATE
from common.consts import STATUE_CODE_MAPPING

NO_INPUT_ERROR = "You must provide a file path or file content"


class DataExtraction:

    """
    Helper function to extract data from the Invoice
    """

    def __init__(self, file_path=None, file_content=None):

        if file_path is None and file_content is None:
            raise IOError(NO_INPUT_ERROR)

        if file_content is not None:
            self.file_content = file_content

        if file_path is not None and file_content is None:
            with open(file_path, "rb") as fh:
                self.file_content = fh.read()

    def _pdf_to_img(self):
        images = []
        pages = convert_from_bytes(self.file_content)
        for page in enumerate(pages):
            images.append(page)
        return images

    def pdf_to_text_using_pdfminer(self):
        output_string = StringIO()
        parser = PDFParser(self.file_content)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
        return output_string.getvalue()

    def pdf_to_text_using_fitz(self):
        doc = fitz.open(stream=self.file_content, filetype="pdf")
        page1 = doc[0]
        words = page1.get_text("words")
        return words

    def pdf_to_img_to_text(self):
        pages = convert_from_bytes(self.file_content)
        data = ""
        for page in pages:
            text = pytesseract.image_to_string(page)
            data += text
        return data

    def pdf_to_text(self):
        text = self.pdf_to_text_using_fitz(self.file_content)
        if len(text) == 0:
            text = self.pdf_to_img_to_text(self.file_content)
        return text


class DataParser:
    def __init__(self, text_data, parser=None):
        self.text_data = text_data
        self.parser = parser

    def classify_invoice(self):
        for template in SIMPLE_INVOICE_TEMPLATES:
            for keyword in template["keywords"]:
                if keyword.lower() in str(self.text_data).lower():
                    return template

        for template in FITZ_INVOICE_TEMPLATE:
            for keyword in template["keywords"]:
                if keyword.lower() in str(self.text_data).lower():
                    return template

        return None

    def normalize_fitz_data(self, data):
        for i in data:
            if data[i]["value"] == "":
                if data[i]["key"] == "company_state_cd":
                    vendor_gst = next(
                        filter(lambda x: x["key"] == "company_gst", data.values())
                    )
                    data[i].update({"value": vendor_gst["value"][:2]})
                if data[i]["key"] == "company_state":
                    vendor_gst = next(
                        filter(lambda x: x["key"] == "company_gst", data.values())
                    )
                    data[i].update(
                        {"value": STATUE_CODE_MAPPING[vendor_gst["value"][:2]]["name"]}
                    )
                if data[i]["key"] == "vendor_state_code":
                    vendor_gst = next(
                        filter(lambda x: x["key"] == "vendor_gst", data.values())
                    )
                    data[i].update({"value": vendor_gst["value"][:2]})
                if data[i]["key"] == "vendor_state":
                    vendor_gst = next(
                        filter(lambda x: x["key"] == "vendor_gst", data.values())
                    )
                    data[i].update(
                        {"value": STATUE_CODE_MAPPING[vendor_gst["value"][:2]]["name"]}
                    )

            if data[i]["key"] == "basic_amount":
                float_amout = data[i]["value"]
                float_amout = float_amout.replace(",", "")
                data[i].update({"value": float_amout})

        return {i["key"]: i["value"] for i in data.values()}

    def fitz_annot_parser(self):
        template = self.classify_invoice()
        if template is None:
            return None
        else:
            fields = template["fields"].copy()
            for i in self.text_data:
                if len(i) == 8:
                    value, box1, box2, box3 = i[4:]
                    location = f"{box1}-{box2}-{box3}"
                    if location in fields:
                        fields[location].update({"value": value})

            return self.normalize_fitz_data(fields)

    def calculate_percent_value(self, total_value, percent_rate):
        
        return (float(total_value)/100) * float(percent_rate)

    def simple_text_parser(self):
        template = self.classify_invoice()
        print(template)
        if template is None:
            return None
        else:
            if template['template_name'] == "CI INFOTECH PVT. LTD":
                response = {}
                fields = template['fields'].copy()
                response.update({"company_name": "C I Infotech Pvt. Ltd."})
                response.update({"vendor_name": "Motherson Automotive Technologies and Engineering"})
                for i in fields:
                    if fields[i]['parser'] == "regex":
                        Regex = re.compile(fields[i]['regex'])
                        m = Regex.search(self.text_data)
                        if i == "igst_rate":
                            response.update({i: m.group().split()[-2]})
                        elif i == "basic_amount":
                            response.update({i: m.group().split()[0]})
                        elif i == "vendor_gst":
                            match = re.findall(Regex, self.text_data)
                            response.update({"company_gst": match[0].split(":")[-1].replace(" ", "")})
                            response.update({"company_state_cd": response["company_gst"][0:2]})
                            response.update({"vendor_gst": match[-1].split(":")[-1].replace(" ", "")})
                            response.update({"vendor_state_code": response["vendor_gst"][0:2]})
                            response.update({"vendor_state": self.state_name_parser_by_code(response["vendor_state_code"])})
                            response.update({"company_state": self.state_name_parser_by_code(response["company_state_cd"])})
                        else:
                            if m.group() != "":
                                response.update({i: m.group().split()[-1]})
                            if i == "total_amount":
                                response.update({"igst_amount": self.calculate_percent_value(float(response["basic_amount"]), float(response["igst_rate"]))})
                                response.update({"cgst_amount": 0.00})
                                response.update({"sgst_amount": 0.00})
                                response.update({"total_amount": float(response["basic_amount"]) + float(response["igst_amount"])})
                                
                print(response)
                return response
            elif template['template_name'] == "Astrea IT Services Private Limited":
                response = {}
                fields = template['fields'].copy()
                response.update({"company_name": "Astrea IT Services Private Limited"})
                response.update({"vendor_name": "M/s Motherson Automotive Technologies and Engineering"})
                for i in fields:
                    if fields[i]['parser'] == "regex":
                        Regex = re.compile(fields[i]['regex'])
                        m = Regex.search(self.text_data)
                        if i == "vendor_state_code":
                            response.update({i: m.group().split()[-1]})
                            response.update({"vendor_state": self.state_name_parser_by_code(response["vendor_state_code"])})
                        elif i == "company_state_cd":
                            response.update({i: m.group().split()[-1]})
                            response.update({"company_state": self.state_name_parser_by_code(response["company_state_cd"])})
                        elif i == "vendor_gst":
                            response.update({i: m.group().split(":")[-1].replace(" ", "")})
                        elif i == "company_gst":
                            response.update({i: m.group().split(":")[-1].replace(" ", "")})
                        elif i == "po_no":
                            response.update({i: m.group()})
                        elif i == "invoice_date":
                            response.update({i: m.group().split(":")[-1].replace("*'", "")})
                        elif i == "invoice_no":
                            response.update({i: m.group().split(":")[-1].replace(" ", "")})
                        else:
                            if m.group() != "":
                                response.update({i: m.group().split()[-1]})
                            if i == "sgst_rate" or i == "cgst_rate":
                                response.update({i: response[i].split("%")[0]})
                            if i == "total_amount":
                                response.update({i: response[i].replace(",", "")})
                                response.update({"igst_amount": 0.00})
                                response.update({"sgst_amount": self.calculate_percent_value(response[i], response["sgst_rate"])})
                                response.update({"cgst_amount": self.calculate_percent_value(response[i], response["cgst_rate"])})
                                response.update({"basic_amount": float(response[i]) - (float(response["cgst_amount"]) + float(response["sgst_amount"]))})
                return response

    
    def state_name_parser_by_code(self, state_code):
        return STATUE_CODE_MAPPING.get(state_code).get("name")

    def parse(self):
        if self.parser == "fitz-annotation-parser":
            return self.fitz_annot_parser()

        if self.parser == "simple-text-parser":
            return self.simple_text_parser()
