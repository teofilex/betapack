"""
Custom Cloudinary storage backend for Django
"""
import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage
from django.conf import settings
import os


class CloudinaryMediaStorage(Storage):
    """
    Custom storage backend that uploads files to Cloudinary
    """

    def __init__(self):
        # Configure Cloudinary
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
        print(f"[CLOUDINARY] Attempting to upload file: {name}")
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
            raise

    def url(self, name):
        """
        Return the URL for accessing the file
        """
        # Build Cloudinary URL with proper format
        # Cloudinary URLs need /image/upload/ in the path
        return cloudinary.CloudinaryImage(name).build_url(
            secure=True,
            resource_type='image'
        )

    def exists(self, name):
        """
        Check if file exists - always return False to allow uploads
        """
        return False

    def delete(self, name):
        """
        Delete file from Cloudinary
        """
        try:
            cloudinary.uploader.destroy(name)
        except Exception as e:
            print(f"Error deleting from Cloudinary: {e}")
