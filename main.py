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

def extraction_using_tesseract(path):
    pages = convert_from_path(path, 500)
    data = ""
    for idx, page in enumerate(pages):
        text = pytesseract.image_to_string(page)
        data += text
    return data

CWD = os.getcwd()

roughly_extracted_data = ""
count = 1

for i in os.listdir("Invoices"):
    path_to_file = os.path.join("Invoices", i)
    if count == 2:
        break

    if os.path.isfile(path_to_file):
        if i.lower().endswith(".pdf"):
            output = " ".join(extraction_using_miner(path_to_file).split())
            if(len(output) == 0):
                print(f"\n\n\nExtracted using Tesseract {path_to_file}\n\n\n")
                roughly_extracted_data = extraction_using_tesseract(path_to_file)
            else:
                print(f"\n\n\nExtracted using Miner {path_to_file} \n\n\n")
                roughly_extracted_data = extraction_using_miner(path_to_file)
                print(roughly_extracted_data)
    
    count = 2