"""Malicious payloads built at test time (S6-T57). No binary fixtures are committed."""

# Split so on-disk scanners do not quarantine this source file; joined at runtime.
EICAR = ("X5O!P%@AP[4\\PZX54(P^)7CC)7}$" + "EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*").encode()

PDF_JS = (
    b"%PDF-1.7\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R/OpenAction 4 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 0/Kids[]>>endobj\n"
    b"4 0 obj<</S/JavaScript/JS(app.alert\\(1\\))>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)

# JPEG magic + a ZIP local-file header / end-of-central-directory appended.
JPEG_ZIP = (
    b"\xff\xd8\xff\xe0"
    + b"\x00" * 12
    + b"\xff\xd9"
    + b"PK\x03\x04"
    + b"\x00" * 26
    + b"payload.txt"
    + b"PK\x05\x06"
    + b"\x00" * 18
)

PDF_HTML = b"%PDF-1.7\n<html><script>alert(document.cookie)</script></html>\n"
