import os
import requests
from datetime import datetime, timedelta
from google.cloud import storage
from google.oauth2 import credentials as google_credentials

REPLIT_SIDECAR_ENDPOINT = "http://127.0.0.1:1106"
BUCKET_NAME = "NewEventData"


def get_storage_client():
    """Creates and returns a Google Cloud Storage client configured for Replit."""
    credential_response = requests.get(f"{REPLIT_SIDECAR_ENDPOINT}/credential")
    credential_response.raise_for_status()
    access_token = credential_response.json().get("access_token")
    
    creds = google_credentials.Credentials(token=access_token)
    client = storage.Client(credentials=creds, project="")
    return client


def upload_file(file_path: str, destination_name: str | None = None) -> str:
    """
    Uploads a file to the NewEventData bucket.
    
    Args:
        file_path: Path to the local file to upload
        destination_name: Name for the file in storage (optional, uses original name if not provided)
    
    Returns:
        str: The path to the uploaded file in storage
    """
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    
    if destination_name is None:
        destination_name = os.path.basename(file_path)
    
    blob = bucket.blob(destination_name)
    blob.upload_from_filename(file_path)
    
    return f"/{BUCKET_NAME}/{destination_name}"


def upload_bytes(data: bytes, destination_name: str, content_type: str = "application/octet-stream") -> str:
    """
    Uploads bytes data to the NewEventData bucket.
    
    Args:
        data: The bytes data to upload
        destination_name: Name for the file in storage
        content_type: MIME type of the content
    
    Returns:
        str: The path to the uploaded file in storage
    """
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    
    blob = bucket.blob(destination_name)
    blob.upload_from_string(data, content_type=content_type)
    
    return f"/{BUCKET_NAME}/{destination_name}"


def upload_string(content: str, destination_name: str, content_type: str = "text/plain") -> str:
    """
    Uploads string content to the NewEventData bucket.
    
    Args:
        content: The string content to upload
        destination_name: Name for the file in storage
        content_type: MIME type of the content
    
    Returns:
        str: The path to the uploaded file in storage
    """
    return upload_bytes(content.encode('utf-8'), destination_name, content_type)


def download_file(source_name: str, destination_path: str) -> str:
    """
    Downloads a file from the NewEventData bucket.
    
    Args:
        source_name: Name of the file in storage
        destination_path: Local path to save the file
    
    Returns:
        str: The local path to the downloaded file
    """
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    
    blob = bucket.blob(source_name)
    blob.download_to_filename(destination_path)
    
    return destination_path


def download_as_bytes(source_name: str) -> bytes:
    """
    Downloads a file from the NewEventData bucket as bytes.
    
    Args:
        source_name: Name of the file in storage
    
    Returns:
        bytes: The file content as bytes
    """
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    
    blob = bucket.blob(source_name)
    return blob.download_as_bytes()


def download_as_string(source_name: str) -> str:
    """
    Downloads a file from the NewEventData bucket as a string.
    
    Args:
        source_name: Name of the file in storage
    
    Returns:
        str: The file content as string
    """
    return download_as_bytes(source_name).decode('utf-8')


def delete_file(file_name: str) -> bool:
    """
    Deletes a file from the NewEventData bucket.
    
    Args:
        file_name: Name of the file to delete
    
    Returns:
        bool: True if deletion was successful
    """
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    
    blob = bucket.blob(file_name)
    blob.delete()
    
    return True


def list_files(prefix: str | None = None) -> list:
    """
    Lists all files in the NewEventData bucket.
    
    Args:
        prefix: Optional prefix to filter files
    
    Returns:
        list: List of file names in the bucket
    """
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs]


def file_exists(file_name: str) -> bool:
    """
    Checks if a file exists in the NewEventData bucket.
    
    Args:
        file_name: Name of the file to check
    
    Returns:
        bool: True if the file exists
    """
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    
    blob = bucket.blob(file_name)
    return blob.exists()


def get_signed_url(file_name: str, expiration_minutes: int = 15, method: str = "GET") -> str:
    """
    Gets a signed URL for accessing a file.
    
    Args:
        file_name: Name of the file
        expiration_minutes: How long the URL should be valid (default 15 minutes)
        method: HTTP method (GET, PUT, DELETE)
    
    Returns:
        str: The signed URL
    """
    request_data = {
        "bucket_name": BUCKET_NAME,
        "object_name": file_name,
        "method": method,
        "expires_at": (datetime.utcnow() + timedelta(minutes=expiration_minutes)).isoformat() + "Z"
    }
    
    response = requests.post(
        f"{REPLIT_SIDECAR_ENDPOINT}/object-storage/signed-object-url",
        headers={"Content-Type": "application/json"},
        json=request_data
    )
    response.raise_for_status()
    
    return response.json().get("signed_url")
