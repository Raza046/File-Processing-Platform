from files.services.image_processor import process_image
from files.services.pdf_processor import process_pdf
from files.services.csv_processor import process_csv


def process_file(file_instance):
    """
    Main dispatcher method.
    Routes file processing based on content type.
    """

    content_type = file_instance.file_type

    if content_type.startswith("image/"):
        return process_image(file_instance)

    elif content_type == "application/pdf":
        return process_pdf(file_instance)

    elif content_type in [
        "txt",
        "application/csv",
        "application/vnd.ms-excel",
    ]:
        return process_csv(file_instance)

    else:
        raise ValueError(f"Unsupported file type: {content_type}")