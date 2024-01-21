import ocrmypdf

input = "tests/assets/cardinal.pdf"
output = "tests/assets/cardinal_ocr.pdf"
ocrmypdf.ocr(input, output, language=["eng", "deu"])