import os
import json
from replit.object_storage import Client

BUCKET_NAME = "NewEventData"


def get_client() -> Client:
    """Gets the Replit Object Storage client for the NewEventData bucket."""
    return Client()


def upload_file(file_path: str, destination_name: str | None = None) -> str:
    """
    Uploads a file to the NewEventData bucket.
    
    Args:
        file_path: Path to the local file to upload
        destination_name: Name for the file in storage (optional, uses original name if not provided)
    
    Returns:
        str: The path to the uploaded file in storage
    """
    client = get_client()
    
    if destination_name is None:
        destination_name = os.path.basename(file_path)
    
    with open(file_path, 'rb') as f:
        client.upload_from_file(destination_name, f)
    
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
    client = get_client()
    client.upload_from_bytes(destination_name, data)
    
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
    client = get_client()
    client.upload_from_text(destination_name, content)
    
    return f"/{BUCKET_NAME}/{destination_name}"


def upload_json(data: dict | list, destination_name: str) -> str:
    """
    Uploads a JSON object to the NewEventData bucket.
    
    Args:
        data: The dict or list to serialize and upload as JSON
        destination_name: Name for the file in storage (should end with .json)
    
    Returns:
        str: The path to the uploaded file in storage
    """
    client = get_client()
    json_content = json.dumps(data, indent=2)
    client.upload_from_text(destination_name, json_content)
    
    return f"/{BUCKET_NAME}/{destination_name}"


def download_file(source_name: str, destination_path: str) -> str:
    """
    Downloads a file from the NewEventData bucket.
    
    Args:
        source_name: Name of the file in storage
        destination_path: Local path to save the file
    
    Returns:
        str: The local path to the downloaded file
    """
    client = get_client()
    
    with open(destination_path, 'wb') as f:
        client.download_to_file(source_name, f)
    
    return destination_path


def download_as_bytes(source_name: str) -> bytes:
    """
    Downloads a file from the NewEventData bucket as bytes.
    
    Args:
        source_name: Name of the file in storage
    
    Returns:
        bytes: The file content as bytes
    """
    client = get_client()
    return client.download_as_bytes(source_name)


def download_as_string(source_name: str) -> str:
    """
    Downloads a file from the NewEventData bucket as a string.
    
    Args:
        source_name: Name of the file in storage
    
    Returns:
        str: The file content as string
    """
    client = get_client()
    return client.download_as_text(source_name)


def delete_file(file_name: str) -> bool:
    """
    Deletes a file from the NewEventData bucket.
    
    Args:
        file_name: Name of the file to delete
    
    Returns:
        bool: True if deletion was successful
    """
    client = get_client()
    client.delete(file_name)
    return True


def list_files(prefix: str | None = None) -> list:
    """
    Lists all files in the NewEventData bucket.
    
    Args:
        prefix: Optional prefix to filter files
    
    Returns:
        list: List of file names in the bucket
    """
    client = get_client()
    objects = client.list()
    
    if prefix:
        return [obj.name for obj in objects if obj.name.startswith(prefix)]
    return [obj.name for obj in objects]


def file_exists(file_name: str) -> bool:
    """
    Checks if a file exists in the NewEventData bucket.
    
    Args:
        file_name: Name of the file to check
    
    Returns:
        bool: True if the file exists
    """
    client = get_client()
    return client.exists(file_name)
