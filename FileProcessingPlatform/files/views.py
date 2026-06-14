from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from files.permissions import IsOwnerOfFilePermission
from files.tasks import process_file_task
from files.models import File, ProcessingHistory
from files.pagination import FileListPagination, ProcesingHistoryPagination
from files.serializers import FileListSerializer, FileProcessingHistorySerializer, FileUpdateSerializer, FileUploadSerializer
from files.services.s3_service import generate_presigned_upload_url
# Create your views here.



class FilesListView(ReadOnlyModelViewSet):
    serializer_class = FileListSerializer
    queryset = File.objects.select_related("uploaded_by")
    pagination_class = FileListPagination
    permission_classes = [IsAuthenticated]
    ordering = ["-created_at"]
    # filter_backends = []
    search_fields = [
        "file_name",
        "file_type",
    ]


class FileProcessingHistoryView(ReadOnlyModelViewSet):
    serializer_class = FileProcessingHistorySerializer
    queryset = ProcessingHistory.objects.select_related("file")
    pagination_class = ProcesingHistoryPagination
    permission_classes = [IsAuthenticated]
    ordering = ["-created_at"]
    # filter_backends = []
    search_fields = [
        "file_name",
        "file_type",
    ]


class FileUploadView(CreateAPIView):
    serializer_class = FileUploadSerializer
    model = File
    permission_classes = [IsAuthenticated]


    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_instance = serializer.save()

        presigned_url = generate_presigned_upload_url(
            file_instance.file_name
            )
        file_instance.storage_path = presigned_url['filename']
        file_instance.save(update_fields=['storage_path'])

        return Response(
            {
                "id": file_instance.id,
                "file_name": file_instance.file_name,
                "url":presigned_url['upload_url'],
            },
            status = status.HTTP_201_CREATED
        )


class FileUpdateView(UpdateAPIView):
    serializer_class = FileUpdateSerializer
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfFilePermission]


    def put(self, request, *args, **kwargs):

        response = super().put(request, *args, **kwargs)

        # serializer = self.get_serializer(instance, data=request.data, partial=True)
        # serializer.is_valid(raise_exception=True)
        # file_instance = serializer.save()
        file_instance = self.get_object()
        # start celery task
        process_file_task(file_instance.id)

        return response


class FileStatusView(ReadOnlyModelViewSet):
    serializer_class = FileListSerializer
    queryset = File.objects.select_related("uploaded_by")
    permission_classes = [IsAuthenticated, IsOwnerOfFilePermission]
    ordering = ["-created_at"]
    lookup_field = 'id'
    # lookup_url_kwarg = "id"

    @action(detail=True, methods=["get"])
    def status(self, request, id=None):
        instance = self.get_object().status
        return Response({"status":instance})

