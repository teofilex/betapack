"""
Custom Cloudinary storage backend for Django
"""
import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings


class CloudinaryMediaStorage(Storage):
    """Upload product images to Cloudinary with size/quality optimization."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
            secure=True
        )

    def _save(self, name, content):
        result = cloudinary.uploader.upload(
            content,
            folder='products',
            resource_type='image',
            use_filename=True,
            unique_filename=True,
            transformation=[
                {'width': 1600, 'crop': 'limit', 'quality': 'auto:good', 'fetch_format': 'auto'}
            ],
        )
        return result['public_id']

    def _open(self, name, mode='rb'):
        return ContentFile(b'')

    def get_available_name(self, name, max_length=None):
        return name

    def url(self, name):
        return cloudinary.CloudinaryImage(name).build_url(
            secure=True,
            resource_type='image'
        )

    def exists(self, name):
        return False

    def delete(self, name):
        try:
            cloudinary.uploader.destroy(name)
        except Exception:
            pass
