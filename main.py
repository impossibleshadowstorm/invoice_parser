# extraction_using_miner Function
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
# extraction_using_tesseract function
from pdf2image import convert_from_path
import pytesseract
# Extras
import os
import re

PARSER = "parser"
KEYWORDS = "keywords"
FIELDS = "fields"
REGEX = "regex"
CWD = os.getcwd()

"""
    Templates for PDF
"""
BECHRAJI_TEMPLATE = {
    "name": "Motherson Automotive Technologies & Engineering",
    "keywords": [
        "Motherson Automotive Technologies & Engineering",
        "09AAACM0405A1ZB",
        "SAMVARDHANA MOTHERSON INTERNATIONAL LIMITED",
    ],
    "fields": {
        "gst": {
            "parser": "regex",
            "regex": "GSTIN : \d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}",
            "type": "str",
        },
        "cin": {
            "parser": "regex",
            "regex": "CIN NO: ([LUu]{1})([0-9]{5})([A-Za-z]{2})([0-9]{4})([A-Za-z]{3})([0-9]{6})",
            "type": "str",
        }
    }
}


"""
    Data Extraction From PDF Using Miner
"""
def extraction_using_miner(path):
    output_string = StringIO()
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string.getvalue()


"""
    Data Extraction From PDF but
    After Converting all pages to images and
    After that extracting the data out
"""
def extraction_using_tesseract(path):
    pages = convert_from_path(path, 500)
    data = ""
    for idx, page in enumerate(pages):
        text = pytesseract.image_to_string(page)
        data += text
    return data


"""
    Return the group of matched data from given text
"""
def find_with_regex(text, regex):
    Regex = re.compile(regex)
    m = Regex.search(text)
    return m.group()


roughly_extracted_data = ""

"""
    Iterating through all the documents present in Invoices folder
"""

# for i in os.listdir("Invoices"):
#     path_to_file = os.path.join("Invoices", i)

#     if os.path.isfile(path_to_file):
#         if i.lower().endswith(".pdf"):
#             output = " ".join(extraction_using_miner(path_to_file).split())
#             if(len(output) == 0):
#                 print(f"\n\n\nExtracted using Tesseract {path_to_file}\n\n\n")
#                 roughly_extracted_data = extraction_using_tesseract(path_to_file)
#             else:
#                 print(f"\n\n\nExtracted using Miner {path_to_file} \n\n\n")
#                 roughly_extracted_data = extraction_using_miner(path_to_file)
#                 print(roughly_extracted_data)


"""
    Main Execution
"""
if __name__ == "__main__":
    roughly_extracted_data = extraction_using_miner("Invoices/Bechraji.pdf")

    found_keyword_cnt = 0
    for i in BECHRAJI_TEMPLATE.get(KEYWORDS):
        if i in roughly_extracted_data:
            found_keyword_cnt += 1

    # Check if we found keyword of some invoice template
    if found_keyword_cnt > 0:
        field = BECHRAJI_TEMPLATE.get("fields")
        list_of_field_keys = list(BECHRAJI_TEMPLATE.get("fields").keys())

        for i in list_of_field_keys:
            if field.get(i).get(PARSER) == REGEX:
                found_text = find_with_regex(
                    roughly_extracted_data, field.get(i).get(REGEX))
                print(found_text)
