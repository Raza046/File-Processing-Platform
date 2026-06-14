from django.contrib import admin
from files.models import File, ProcessingHistory

# Register your models here.
admin.site.register(File)
admin.site.register(ProcessingHistory)
