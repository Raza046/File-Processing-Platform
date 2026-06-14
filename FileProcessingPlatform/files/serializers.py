from rest_framework.serializers import Serializer, ModelSerializer

from files.models import File, ProcessingHistory
from files.services.s3_service import generate_presigned_upload_url



class FileListSerializer(ModelSerializer):

    class Meta:
        exclude = ("id",)
        model = File
        read_only_fields = ("created_at", "updated_at")


class FileProcessingHistorySerializer(ModelSerializer):

    class Meta:
        exclude = ("id",)
        model = ProcessingHistory
        read_only_fields = ("storage_path", "status", "created_at", "updated_at")


class FileUpdateSerializer(ModelSerializer):

    class Meta:
        model = File
        fields = ("status",)



class FileUploadSerializer(ModelSerializer):

    class Meta:
        model = File
        exclude = ("id", "storage_path", "uploaded_by", "metadata")


    def validate_file_size(self, file_size):

        max_size = 10 * 1024 * 1024; # 10MB
        if file_size > max_size:
            raise ValueError("File size exceed 10MB!")

        return file_size


    def validate_file_name(self, file_name):

        if len(file_name) < 4:
            raise ValueError("File name too short!")

        return file_name


    def create(self, validated_data):

        # Generate S3 file link and then return that link in response.
        # storage_path = validated_data.get("storage_path")
        uploaded_by = self.context.get("request").user

        validated_data["uploaded_by"] = uploaded_by
        return super().create(validated_data)

