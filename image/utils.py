import jwt
import uuid
import boto3
import requests
from io import BytesIO
from .models import Image
from decouple import config
from PIL import Image as Img
from django.conf import settings
from authentication.models import User
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from transformers import BlipProcessor, BlipForConditionalGeneration 


s3 = boto3.client(
    's3',
    aws_access_key_id = config('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
    region_name = config('AWS_S3_REGION_NAME')
)


def upload_to_s3(image_file):

    new_id = uuid.uuid1()
    file_name = str(new_id) + '.' + str(image_file.name).split('.')[-1]
    key = f"images/{file_name}"    
    
    image_file.seek(0)  # reseting the pointer
    try:
        s3.upload_fileobj(
            image_file,  
            config('AWS_STORAGE_BUCKET_NAME'),
            key, 
            ExtraArgs={'ContentType': image_file.content_type}
        )

        file_url = f"https://gallery-cloud-storage.s3.eu-north-1.amazonaws.com/images/{file_name}"
        return file_url
    
    except:
        
        return False
 
 
def image_checker(file):
    try:
        img = Img.open(BytesIO(file.read()))
        img.verify()
        return True
    except Exception:
        return False   
    
    
def object_key_parser(image_url):
    object_key = '/'.join(image_url.split('/')[-2:])
    return object_key
    
    
def delete_from_s3(object_key):

    try:

        response = s3.delete_object(
            Bucket=config('AWS_STORAGE_BUCKET_NAME'),
            Key=object_key
        )
        if response.status_code == 202:
            return {"status": True}
        
    except Exception as e:
        return {"status": False, "error": str(e)}


def validate_JWT(token):
    try:
        if not token:
            return {"valid": False, "error": "Token is missing"}    
        decoded_token = jwt.decode(token, settings.SECRET_KEY_JWT, algorithms=["HS256"])

        return {"valid": True, "token": decoded_token}

    except ExpiredSignatureError:
        return {"valid": False, "error": "Token has expired"}
    except InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}


def generate_caption(image_url):
    
    img = requests.get(image_url).content
    img_bytes = BytesIO(img).getvalue()
    
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f"Bearer {config('HUGGING_KEY')}"}
    
    caption = requests.post(API_URL, headers=headers, data=img_bytes).json()[0]['generated_text']
    
    return caption


def ownership_validation(user_id, image_id):

    
    try:
        img = Image.objects.filter(id=image_id).first()
        
        if not img:
            return {"valid": False, "message": "Image does not exist", "status": 404}
        
        user = User.objects.get(id=user_id)
        
        if img.user == user:
            return {"valid": True, "image": img}
        
        else:
            return {"valid": False, "message": "Unauthorized to use this image", "status": 403}
    
    except Exception as e:
        return {"valid": False, "message": "Internal Server Error--", "status": 500}
    
    