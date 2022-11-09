from io import BytesIO
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


def get_django_file(url: str):
    r = requests.get(url, allow_redirects=True)

    file_name = url.rsplit('/', 1)[1]
    file_type = r.headers.get('content-type')

    file_io = BytesIO(r.content)
    django_file = InMemoryUploadedFile(
        file_io, None, file_name, file_type, file_io.tell(), None)

    return django_file
