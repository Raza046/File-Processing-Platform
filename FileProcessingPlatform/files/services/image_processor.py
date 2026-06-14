from PIL import Image
from io import BytesIO
from files.models import File, ProcessingHistory


def process_image(file_instance):

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