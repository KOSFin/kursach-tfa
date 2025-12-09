from pypdf import PdfReader

reader = PdfReader("Методические_указания_по_выполнению_курсовой_работы.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

print(text)
