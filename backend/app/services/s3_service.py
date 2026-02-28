import boto3
import os
from typing import Optional
from datetime import datetime

class S3Service:
    """
    Service for uploading resumes and cover letters to S3
    """
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.aws_region = os.getenv("AWS_REGION", "us-west-2")
        
        # Initialize S3 client if bucket is configured
        if self.bucket_name:
            try:
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.aws_region
                )
            except Exception as e:
                print(f"Warning: Could not initialize S3 client: {e}")
                self.s3_client = None
        else:
            self.s3_client = None
    
    def upload_resume(self, resume_content: str, application_id: int) -> Optional[str]:
        """
        Upload resume content to S3
        
        Returns:
            S3 URL if successful, None otherwise
        """
        if not self.s3_client or not self.bucket_name:
            return None
        
        try:
            key = f"resumes/application_{application_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=resume_content.encode('utf-8'),
                ContentType='text/markdown'
            )
            
            url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{key}"
            return url
        except Exception as e:
            print(f"Error uploading resume to S3: {e}")
            return None
    
    def upload_cover_letter(self, cover_letter_content: str, application_id: int) -> Optional[str]:
        """
        Upload cover letter content to S3
        
        Returns:
            S3 URL if successful, None otherwise
        """
        if not self.s3_client or not self.bucket_name:
            return None
        
        try:
            key = f"cover-letters/application_{application_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=cover_letter_content.encode('utf-8'),
                ContentType='text/markdown'
            )
            
            url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{key}"
            return url
        except Exception as e:
            print(f"Error uploading cover letter to S3: {e}")
            return None

# Singleton instance
s3_service = S3Service()
