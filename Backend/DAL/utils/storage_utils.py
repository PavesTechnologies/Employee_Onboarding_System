# storage_utils.py
import aioboto3
from botocore.exceptions import ClientError
from uuid import uuid4
from datetime import datetime
import mimetypes
import os
from typing import Optional, BinaryIO
import asyncio
from contextlib import asynccontextmanager
from ...config.env_loader import get_env_var

class S3StorageService:
    """
    Async S3 Storage Service for Employee Onboarding Files
    """
    
    def __init__(
        self,
        access_key_id: str = None,
        secret_access_key: str = None,
        region_name: str = None,
        bucket_name: str = None
    ):
        self.access_key_id = get_env_var('AWS_ACCESS_KEY_ID')
        self.secret_access_key = get_env_var('AWS_SECRET_ACCESS_KEY')
        self.region_name = get_env_var('AWS_REGION')
        self.bucket_name = get_env_var('S3_BUCKET_NAME')
        print("AWS_ACCESS_KEY_ID:", self.access_key_id)
        print("AWS_SECRET_ACCESS_KEY:", self.secret_access_key)
        print("BUCKET:", self.bucket_name)
        
        if not all([self.access_key_id, self.secret_access_key, self.bucket_name]):
            raise ValueError("AWS credentials and bucket name must be provided")
        
        self.session = aioboto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name
        )
    
    @asynccontextmanager
    async def get_client(self):
        """Context manager for S3 client"""
        async with self.session.client('s3') as client:
            yield client
    
    async def upload_file(
        self,
        file,                       # UploadFile OR bytes
        folder: str,
        original_filename: str = None,
        employee_uuid: str = None,
        custom_filename: str = None
    ) -> str:
        try:
           
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid4())[:8]

            # ✅ Determine filename & extension safely
            if custom_filename:
                filename = custom_filename

            elif original_filename:
                name, ext = os.path.splitext(original_filename)
                ext = ext if ext else ".bin"   # fallback only if truly missing
                safe_name = name.replace(" ", "_")[:50]
                filename = f"{safe_name}_{timestamp}_{unique_id}{ext}"

            else:
                filename = f"file_{timestamp}_{unique_id}.bin"

            # ✅ Build S3 key
            if employee_uuid:
                s3_key = f"{folder}/{employee_uuid}/{filename}"
            else:
                s3_key = f"{folder}/{filename}"

            # ✅ Detect content type
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

            # ✅ Read file correctly
            if hasattr(file, "read"):
                if hasattr(file, "seek"):
                    await file.seek(0)
                file_content = await file.read()
            else:
                file_content = file

            # ✅ Upload to S3
            async with self.get_client() as s3_client:
                await s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_content,
                    ContentType=content_type,
                    ServerSideEncryption="AES256",
                    Metadata={
                        "uploaded_at": datetime.utcnow().isoformat(),
                        "original_filename": original_filename or "unknown"
                    }
                )

            return f"s3://{self.bucket_name}/{s3_key}"

        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")
        except Exception as e:
            raise Exception(f"File upload error: {str(e)}")
    
    async def download_file(self, s3_path: str) -> bytes:
        """
        Download file from S3
        
        Args:
            s3_path: S3 URI (e.g., 's3://bucket-name/folder/file.pdf')
        
        Returns:
            bytes: File content
        
        Example:
            file_content = await storage.download_file('s3://bucket/folder/file.pdf')
        """
        try:
            # Parse S3 path
            if s3_path.startswith('s3://'):
                s3_path = s3_path.replace('s3://', '')
                parts = s3_path.split('/', 1)
                bucket = parts[0]
                s3_key = parts[1] if len(parts) > 1 else ''
            else:
                bucket = self.bucket_name
                s3_key = s3_path
            
            # Download from S3
            async with self.get_client() as s3_client:
                response = await s3_client.get_object(
                    Bucket=bucket,
                    Key=s3_key
                )
                
                # Read the streaming body
                file_content = await response['Body'].read()
                return file_content
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise Exception(f"File not found: {s3_path}")
            raise Exception(f"S3 download failed: {str(e)}")
        except Exception as e:
            raise Exception(f"File download error: {str(e)}")
    
    async def get_presigned_url(
        self,
        s3_path: str,
        expiration: int = 3600,
        download: bool = False  # default open in browser
    ) -> str:
        try:
            # Parse S3 path
            if s3_path.startswith('s3://'):
                s3_path = s3_path.replace('s3://', '')
                bucket, s3_key = s3_path.split('/', 1)
            else:
                bucket = self.bucket_name
                s3_key = s3_path

            async with self.get_client() as s3_client:
                params = {
                    'Bucket': bucket,
                    'Key': s3_key
                }

                filename = s3_key.split('/')[-1]

                if download:
                    # Force download
                    params['ResponseContentDisposition'] = (
                        f'attachment; filename="{filename}"'
                    )
                else:
                    # Open in browser
                    params['ResponseContentDisposition'] = (
                        f'inline; filename="{filename}"'
                    )

                url = await s3_client.generate_presigned_url(
                    'get_object',
                    Params=params,
                    ExpiresIn=expiration
                )

                return url

        except ClientError as e:
            raise Exception(f"URL generation failed: {str(e)}")

    
    async def delete_file(self, s3_path: str) -> bool:
        """
        Delete file from S3
        
        Args:
            s3_path: S3 URI
        
        Returns:
            bool: True if successful
        
        Example:
            success = await storage.delete_file('s3://bucket/folder/file.pdf')
        """
        try:
            # Parse S3 path
            if s3_path.startswith('s3://'):
                s3_path = s3_path.replace('s3://', '')
                parts = s3_path.split('/', 1)
                bucket = parts[0]
                s3_key = parts[1] if len(parts) > 1 else ''
            else:
                bucket = self.bucket_name
                s3_key = s3_path
            
            # Delete from S3
            async with self.get_client() as s3_client:
                await s3_client.delete_object(
                    Bucket=bucket,
                    Key=s3_key
                )
            
            return True
            
        except ClientError as e:
            raise Exception(f"S3 deletion failed: {str(e)}")
        except Exception as e:
            raise Exception(f"File deletion error: {str(e)}")
    
    async def file_exists(self, s3_path: str) -> bool:
        """
        Check if file exists in S3
        
        Args:
            s3_path: S3 URI
        
        Returns:
            bool: True if file exists
        
        Example:
            exists = await storage.file_exists('s3://bucket/folder/file.pdf')
        """
        try:
            # Parse S3 path
            if s3_path.startswith('s3://'):
                s3_path = s3_path.replace('s3://', '')
                parts = s3_path.split('/', 1)
                bucket = parts[0]
                s3_key = parts[1] if len(parts) > 1 else ''
            else:
                bucket = self.bucket_name
                s3_key = s3_path
            
            # Check if file exists
            async with self.get_client() as s3_client:
                await s3_client.head_object(
                    Bucket=bucket,
                    Key=s3_key
                )
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise Exception(f"Error checking file existence: {str(e)}")
        except Exception as e:
            return False
    
    async def get_file_metadata(self, s3_path: str) -> dict:
        """
        Get file metadata from S3
        
        Args:
            s3_path: S3 URI
        
        Returns:
            dict: File metadata including size, content_type, last_modified
        
        Example:
            metadata = await storage.get_file_metadata('s3://bucket/file.pdf')
        """
        try:
            # Parse S3 path
            if s3_path.startswith('s3://'):
                s3_path = s3_path.replace('s3://', '')
                parts = s3_path.split('/', 1)
                bucket = parts[0]
                s3_key = parts[1] if len(parts) > 1 else ''
            else:
                bucket = self.bucket_name
                s3_key = s3_path
            
            # Get metadata
            async with self.get_client() as s3_client:
                response = await s3_client.head_object(
                    Bucket=bucket,
                    Key=s3_key
                )
            
            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            raise Exception(f"Error getting metadata: {str(e)}")


# Singleton instance
_storage_instance: Optional[S3StorageService] = None

def get_storage_service() -> S3StorageService:
    """
    Get or create singleton storage service instance
    
    Returns:
        S3StorageService: Storage service instance
    
    Example:
        storage = get_storage_service()
        file_path = await storage.upload_file(...)
    """
    global _storage_instance
    
    if _storage_instance is None:
        _storage_instance = S3StorageService()
    
    return _storage_instance