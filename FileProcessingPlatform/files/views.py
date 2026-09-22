from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from files.permissions import IsOwnerOfFilePermission
from files.tasks import process_file_chunk, start_file_processing
from files.models import File, ProcessingHistory
from files.pagination import FileListPagination, ProcesingHistoryPagination
from files.serializers import ( CompleteMultipartUploadSerializer, FileListSerializer, FileProcessingHistorySerializer, FileUpdateSerializer,
                                FileUploadSerializer, GeneratePreSignedUrlSerializer, AbortMultipartUploadSerializer, ListPartsUploadedSerializer )
from files.services.s3_service import generate_presigned_upload_url, create_multipart_upload, complete_multipart_upload, list_parts_uploaded
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



class InitiateFileUploadView(CreateAPIView):
    serializer_class = FileUploadSerializer
    model = File
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_instance = serializer.save()

        # presigned_url = generate_presigned_upload_url(
        #     file_instance.file_name
        #     )

        multipart_upload_response = create_multipart_upload(
            file_instance.file_name, file_instance.file_size
            )

        file_instance.storage_path = multipart_upload_response['key']
        file_instance.save(update_fields=['storage_path'])

        return Response(multipart_upload_response,
            # {
            #     "id": file_instance.id,
            #     "file_name": file_instance.file_name,
            #     "upload_id":presigned_url['upload_url'],
            # },
            status = status.HTTP_200_OK
        )


class GeneratePreSignedUrlView(CreateAPIView):
    serializer_class = GeneratePreSignedUrlSerializer
    model = File
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        response = serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        presigned_url = generate_presigned_upload_url(
            data["key"],
            data["upload_id"],
            data["part_number"]
        )

        print(presigned_url)

        return Response(presigned_url, status = status.HTTP_200_OK)


class CompleteFileUploadView(CreateAPIView):
    serializer_class = CompleteMultipartUploadSerializer
    model = File
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        print("=========COMPLETE VALIDATED DATA==========")
        print(data)
        print("=========COMPLETE VALIDATED DATA==========")
        response = complete_multipart_upload(
            data["key"],
            data["upload_id"],
            data["part_number"]
        )

        print(response)

        return Response(response, status = status.HTTP_200_OK)



class AbortMultipartUploadView(CreateAPIView):
    serializer_class = AbortMultipartUploadSerializer
    model = File
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        data = serializer.validated_data
        response = abort_multipart_upload(
            data["key"],
            data["upload_id"],
            data["part_number"]
        )

        print(response)

        return Response(response, status = status.HTTP_200_OK)


class ListPartsUploadedView(CreateAPIView):
    serializer_class = ListPartsUploadedSerializer
    model = File
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        data = serializer.validated_data
        response = list_parts_uploaded(
            data["key"],
            data["upload_id"]
        )

        print(response)

        return Response(response, status = status.HTTP_200_OK)


class StartProcessingFileView(RetrieveAPIView):
    serializer_class = None
    model = File
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        file = self.get_object()
        start_file_processing(file.id)
        file.status = File.FileStatus.PROCESSING
        file.save(update_fields=['status'])

        return Response("Processing Started..!", status = status.HTTP_200_OK)


# class FileUploadView(CreateAPIView):.
#     serializer_class = FileUploadSerializer
#     model = File
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         file_instance = serializer.save()

#         presigned_url = generate_presigned_upload_url(
#             file_instance.file_name
#             )
#         file_instance.storage_path = presigned_url['filename']
#         file_instance.save(update_fields=['storage_path'])

#         return Response(
#             {
#                 "id": file_instance.id,
#                 "file_name": file_instance.file_name,
#                 "url":presigned_url['upload_url'],
#             },
#             status = status.HTTP_201_CREATED
#         )



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
        process_file_chunk(file_instance.id)

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

