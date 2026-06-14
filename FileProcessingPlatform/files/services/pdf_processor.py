from celery import shared_task
from pypdf import PdfReader


def process_pdf(file_instance):

    file_obj = file_instance.file.open("rb")

    reader = PdfReader(file_obj)

    extracted_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text += text

    file_instance.extracted_text = extracted_text
    file_instance.processing_status = "completed"

    file_instance.save(
        update_fields=[
            "extracted_text",
            "processing_status",
        ]
    )

    return extracted_text

