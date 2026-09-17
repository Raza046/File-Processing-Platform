import uuid

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.


class CommonDateTimeAbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract=True


class File(CommonDateTimeAbstractModel):

    class FileType(models.TextChoices):
        PDF = "pdf", "PDF"
        CSV = "csv", "CSV"
        XLSX = "xlsx", "XLSX"
        PNG = "png", "PNG"
        JPG = "jpg", "JPG"
        DOCX = "docx", "DOCX"
        TXT = "txt", "TXT"

    class FileStatus(models.TextChoices):
        PROCESSING = "processing", "PROCESSING"
        FAILED = "failed", "FAILED"
        PENDING = "pending", "PENDING"
        COMPLETED = "completed", "COMPLETED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="files")
    file_name = models.CharField(max_length=100)
    file_size = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    file_type = models.CharField(choices=FileType.choices, default=FileType.TXT, max_length=100)
    status = models.CharField(choices=FileStatus.choices, default=FileStatus.PENDING, max_length=100)
    storage_path = models.TextField()
    metadata = models.TextField()
    content_hash = models.CharField(max_length=64)
    # parts_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.file_name} ({self.status})"

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["uploaded_by"]),
            models.Index(fields=["created_at"]),
        ]



class ProcessingHistory(CommonDateTimeAbstractModel):

    class ProcessingStatus(models.TextChoices):
        PROCESSING = "processing", "PROCESSING"
        FAILED = "failed", "FAILED"
        PENDING = "pending", "PENDING"
        COMPLETED = "completed", "COMPLETED"

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="processing_history")
    retry_count = models.PositiveIntegerField(default=0)
    status = models.CharField(choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING, max_length=100)
    error_message = models.TextField()
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # seconds

    def __str__(self):
        return f"{self.file.file_name} ({self.status})"


