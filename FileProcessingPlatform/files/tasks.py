from celery import shared_task, chain, chord
from config.celery import app
from pydantic import ValidationError
from files.services.s3_service import download_from_localstack_s3
from files.services.file_content_hash import calculate_sha256
from pypdf import PdfReader
from PIL import Image
from io import BytesIO
import pandas as pd

from files.models import File
from files.services.file_processor import process_file


"""
Work with the Chord here.

download
process
upload
metadata update in DB
"""


def start_file_processing(file_id: int):

    file = File.objects.get(id=file_id)
    chain_tasks = []
    total_chunks = get_chunks(file.file_size)

    part_size = file.file_size // total_chunks
    # 50 by 2 = 25

    for chunk_number in range(total_chunks):

        start  = chunk_number * part_size

        if chunk_number == total_chunks - 1:
            end = file.file_size
        else:
            end = start + part_size

        chain_tasks.append(chain(
            download_file_chunk.s(file_id, start, end),
            # process_file_task.s(file_id),
            # upload_file_chunk.s(file_id),
        ))

    chord(
        chain_tasks
    )(call_back.s(file_id))

def get_chunks(file_size):
    # if file_size > (1e+8)-1:
    #     return 10
    return 2


@app.task
def call_back(file_id):

    file_instance = File.objects.get(id=file_id)
    file_instance.processing_status = "completed"
    file_instance.save(
        update_fields=["processing_status"]
    )
    return True


@app.task
def download_file_chunk(file_id: int, start: int, end: int):

    print("------INSIDE DONWLOAD CHUNK METHOD----------")

    file_instance = File.objects.get(id=file_id)

    # response = cli.get_object(
    #     Bucket="my-bucket",
    #     Key="my-file",
    #     Range=f"bytes={start}-{end}",
    # )

    download_from_localstack_s3(
        bucket_name="my-bucket",
        object_key=file_instance.file_name,
        Range=f"bytes={start}-{end}",
        # destination_path=f"/tmp/{file_instance.storage_path}"
    )

@app.task
def upload_file_chunk(file_id: int):

    # check if the initate API is called. Ned to store something in DB.

    file_instance = File.objects.get(id=file_id)



def process_file_task(file_id: int):

    file_instance = File.objects.get(id=file_id)

    # file_instance.processing_status = "processing"
    # file_instance.save(update_fields=["processing_status"])

    # process_file(file_instance)

    content_type = file_instance.file_type

    if content_type.startswith("image/"):
        return process_image.delay(str(file_instance.id))

    elif content_type == "application/pdf":
        return process_pdf.delay(str(file_instance.id))

    elif content_type in [
        "txt",
        "application/csv",
        "application/vnd.ms-excel",
    ]:
        print("-------INSIDE TXT ELIF-----------")
        print("-------INSIDE TXT ELIF-----------")
        print("-------INSIDE TXT ELIF-----------")
        return process_csv.delay(str(file_instance.id))

    else:
        raise ValueError(f"Unsupported file type: {content_type}")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_pdf(self, file_instance_id):

    file_instance = File.objects.get(id=file_instance_id)

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



@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_csv(self, file_instance_id):

    print("-------INSIDE PROCESS CSV-----------")

    # file_obj = file_instance.file.open("rb")
    file_instance = File.objects.get(id=file_instance_id)
    # file_obj = file_instance.id
    # Donwload the file from S3.

    downloaded_file = download_from_localstack_s3(
        bucket_name="my-bucket",
        object_key=file_instance.file_name,
        destination_path=f"/tmp/{file_instance.storage_path}"
    )

    df = pd.read_csv(downloaded_file)

    # hashed_content = calculate_sha256(f"/tmp/{file_instance.storage_path}")
    # print(f"Hashed Content: {hashed_content}")
    # if file_instance.content_hash == hashed_content:
    #     print("File already processed..!")
    #     return ValidationError("File already processed..!")

    total_rows = len(df)
    total_columns = len(df.columns)

    metadata = {
        "rows": total_rows,
        "columns": total_columns,
        "column_names": list(df.columns),
    }

    # Example:
    # store parsed rows into DB here

    file_instance.metadata = metadata
    file_instance.processing_status = "completed"
    # file_instance.content_hash = hashed_content

    file_instance.save(
        update_fields=["metadata", "processing_status"]
        # update_fields=["metadata", "processing_status", "content_hash"]
    )

    return metadata



@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_image(self, file_instance_id):

    file_instance = File.objects.get(id=file_instance_id)
    file_obj = file_instance.file.open("rb")

    image = Image.open(file_obj)

    width, height = image.size
    image_format = image.format

    thumbnail_size = (200, 200)

    image.thumbnail(thumbnail_size)

    thumb_io = BytesIO()

    image.save(thumb_io, format=image_format)

    thumb_io.seek(0)

    # TODO:
    # upload thumbnail to S3

    metadata = {
        "width": width,
        "height": height,
        "format": image_format,
    }

    file_instance.metadata = metadata
    file_instance.processing_status = File.FileStatus.COMPLETED

    file_instance.save(update_fields=["metadata", "processing_status"])

    return metadata
