import os
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def upload_to_supabase(file_data: bytes, bucket_name: str, file_path: str = None) -> str:
    """
    Upload a file to Supabase Storage
    
    Args:
        file_data (bytes): The file data to upload
        bucket_name (str): Name of the Supabase storage bucket
        file_path (str, optional): The path where the file should be stored. If not provided, a UUID will be generated.
        
    Returns:
        str: The public URL of the uploaded file
    """
    try:
        if file_path is None:
            # Generate a unique filename if none provided
            file_path = f"audio/{uuid.uuid4()}.wav"
            
        # Upload the file to Supabase Storage
        result = supabase.storage.from_(bucket_name).upload(
            file_path,
            file_data,
            {"content-type": "audio/wav"}
        )
        
        # Get the public URL
        url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return url
        
    except Exception as e:
        print(f"Error uploading to Supabase Storage: {e}")
        raise 