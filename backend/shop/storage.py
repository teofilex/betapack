"""
Custom Cloudinary storage backend for Django
"""
import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
import os


class CloudinaryMediaStorage(Storage):
    """
    Custom storage backend that uploads files to Cloudinary
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configure Cloudinary
        print("[CLOUDINARY] Initializing CloudinaryMediaStorage")
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
            secure=True
        )

    def _save(self, name, content):
        """
        Save file to Cloudinary
        """
        print(f"[CLOUDINARY] _save() called with name: {name}")
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                content,
                folder='products',
                resource_type='auto',
                use_filename=True,
                unique_filename=True
            )
            print(f"[CLOUDINARY] Upload successful! Public ID: {result['public_id']}")
            print(f"[CLOUDINARY] Secure URL: {result.get('secure_url')}")
            # Return the public_id (Cloudinary's identifier)
            return result['public_id']
        except Exception as e:
            print(f"[CLOUDINARY] Upload FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _open(self, name, mode='rb'):
        """
        Required by Django - open file for reading
        """
        print(f"[CLOUDINARY] _open() called with name: {name}")
        # Return a ContentFile with the Cloudinary URL
        # This is needed for Django to work properly
        return ContentFile(b'')

    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's available for writing
        """
        print(f"[CLOUDINARY] get_available_name() called with name: {name}")
        return name

    def url(self, name):
        """
        Return the URL for accessing the file
        """
        print(f"[CLOUDINARY] url() called with name: {name}")
        # Build Cloudinary URL with proper format
        # Cloudinary URLs need /image/upload/ in the path
        url = cloudinary.CloudinaryImage(name).build_url(
            secure=True,
            resource_type='image'
        )
        print(f"[CLOUDINARY] Generated URL: {url}")
        return url

    def exists(self, name):
        """
        Check if file exists - always return False to allow uploads
        """
        print(f"[CLOUDINARY] exists() called with name: {name}")
        return False

    def delete(self, name):
        """
        Delete file from Cloudinary
        """
        print(f"[CLOUDINARY] delete() called with name: {name}")
        try:
            cloudinary.uploader.destroy(name)
        except Exception as e:
            print(f"[CLOUDINARY] Error deleting: {e}")
