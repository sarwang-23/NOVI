import logging
import os
import uuid
from typing import Optional, BinaryIO
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """
    File storage service supporting local filesystem and S3/GCS.
    Configure via environment variables:
      STORAGE_BACKEND: "local" | "s3" | "gcs"
      STORAGE_LOCAL_PATH: local directory (default: ./uploads)
      AWS_S3_BUCKET, AWS_S3_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY (for S3)
      GCS_BUCKET, GCS_PROJECT_ID (for GCS)
    """

    @staticmethod
    def _get_backend() -> str:
        return getattr(settings, "STORAGE_BACKEND", "local")

    @staticmethod
    def _get_local_path() -> str:
        path = getattr(settings, "STORAGE_LOCAL_PATH", "./uploads")
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def generate_filename(original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1].lower()
        return f"{uuid.uuid4().hex}{ext}"

    @classmethod
    def upload_file(
        cls,
        file_content: bytes,
        original_filename: str,
        folder: str = "general",
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        """
        Upload a file and return the storage URL/path.
        Returns None on failure.
        """
        backend = cls._get_backend()
        filename = cls.generate_filename(original_filename)
        key = f"{folder}/{filename}"

        try:
            if backend == "s3":
                return cls._upload_to_s3(file_content, key, content_type)
            elif backend == "gcs":
                return cls._upload_to_gcs(file_content, key, content_type)
            else:
                return cls._upload_to_local(file_content, key)
        except Exception as exc:
            logger.error(f"[StorageService] Upload failed for {original_filename}: {exc}")
            return None

    @classmethod
    def _upload_to_local(cls, file_content: bytes, key: str) -> str:
        base_path = cls._get_local_path()
        full_path = os.path.join(base_path, key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(file_content)
        return f"/uploads/{key}"

    @classmethod
    def _upload_to_s3(cls, file_content: bytes, key: str, content_type: str) -> str:
        import boto3
        from botocore.exceptions import ClientError

        bucket = getattr(settings, "AWS_S3_BUCKET", "")
        region = getattr(settings, "AWS_S3_REGION", "us-east-1")

        s3 = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY", ""),
            aws_secret_access_key=getattr(settings, "AWS_SECRET_KEY", ""),
        )

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_content,
            ContentType=content_type,
        )

        return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    @classmethod
    def _upload_to_gcs(cls, file_content: bytes, key: str, content_type: str) -> str:
        from google.cloud import storage

        bucket_name = getattr(settings, "GCS_BUCKET", "")
        project_id = getattr(settings, "GCS_PROJECT_ID", "")

        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(key)
        blob.upload_from_string(file_content, content_type=content_type)

        return f"https://storage.googleapis.com/{bucket_name}/{key}"

    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """Delete a file by its storage path/URL."""
        backend = cls._get_backend()

        try:
            if backend == "s3":
                import boto3
                bucket = getattr(settings, "AWS_S3_BUCKET", "")
                key = file_path.split(f"{bucket}.s3.")[-1].split("/", 1)[1] if bucket in file_path else file_path
                s3 = boto3.client("s3", region_name=getattr(settings, "AWS_S3_REGION", "us-east-1"))
                s3.delete_object(Bucket=bucket, Key=key)
                return True
            elif backend == "gcs":
                from google.cloud import storage
                bucket_name = getattr(settings, "GCS_BUCKET", "")
                key = file_path.split(f"{bucket_name}/")[-1] if bucket_name in file_path else file_path
                client = storage.Client(project=getattr(settings, "GCS_PROJECT_ID", ""))
                bucket = client.bucket(bucket_name)
                bucket.blob(key).delete()
                return True
            else:
                base_path = cls._get_local_path()
                relative = file_path.replace("/uploads/", "")
                full_path = os.path.join(base_path, relative)
                if os.path.exists(full_path):
                    os.remove(full_path)
                return True
        except Exception as exc:
            logger.error(f"[StorageService] Delete failed for {file_path}: {exc}")
            return False
