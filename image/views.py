from .utils import *
from .serializers import *
from .models import Image
from authentication.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def upload_image(request):
    """
    Endpoint to upload an image. The user must be authenticated through the token.
    - Expects 'image' in the request body.
    - One image at a tome.
    - Optionally accepts a 'description' field for the image.
    
    Supported image's format:
    - JPEG
    - PNG
    - BMP
    - GIF
    - WEBP
    """
    # Validate the incoming JWT token
    incoming_token = request.headers.get('token')        
    token_validation = validate_JWT(incoming_token)
    
    if not token_validation['valid']:
        return Response({"message": token_validation["error"]}, status=401)
    
    # Get image from request    
    image = request.FILES.get('image')
    if not image:
        return Response({"message": "No image uploaded"}, status=400)
    
    is_image = image_checker(image)
    if not is_image:
        return Response({"message": "Invalid image"}, status=400)
    
    description = request.data.get('description')
    token = token_validation['token']
    user_id = token['user_id']
    
    # Upload the image to S3 Bucket
    res = upload_to_s3(image)
    if not res:
        return Response({"message": "Internal Server Error"}, status=500)
    
    try:
        # Save image to database
        user = User.objects.get(id=user_id)        
        image_insertion = Image(title=image.name, description=description, url=res, user=user)
        image_insertion.save()
        
    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)
        
    return Response({"message": "Image saved successfully", "image_id": image_insertion.id}, status=200)


@api_view(['GET'])
def get_images(request):
    """
    Endpoint to retrieve all images uploaded by the authenticated user.
    """
    # Validate the incoming JWT token
    incoming_token = request.headers.get('token')
    token_validation = validate_JWT(incoming_token)
    
    if not token_validation['valid']:
        return Response({"message": token_validation["error"]}, status=401)
    
    try:
        # Get user from token
        token = token_validation['token']
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
        
        # Retrieve images for the user
        images = Image.objects.filter(user=user)
        results = image_serializer(images, many=True)
        count = images.count()
        
        return Response({"count": str(count), "results": results.data}, status=200)
    
    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)


@api_view(['POST'])
def caption_generator(request):
    """
    Endpoint to generate a caption for an image using AI. The user must own the image.
    - Expects 'image_id' in the request body.
    """
    # Validate the incoming JWT token
    incoming_token = request.headers.get('token')
    token_validation = validate_JWT(incoming_token)
    
    if not token_validation['valid']:
        return Response({"message": token_validation['error']}, status=401)
    
    image_id = request.data.get('image_id')
    if not image_id:
        return Response({"message": "Image ID is required"}, status=400)
    elif not str(image_id).isdigit():
        return Response({"message": "Image ID is not valid"}, status=400)
    
    # Validate ownership of the image
    token = token_validation['token']
    user_id = token['user_id']
    image = ownership_validation(user_id, image_id)

    if not image["valid"]:
        return Response({"message": image["message"]}, status=int(image["status"]))

    try:
        image_url = str(image['image'].url)
        # Generate caption for the image
        caption = generate_caption(image_url)
        
        if not caption:
            return Response({"message": "Internal Server Error"}, status=500)
        
        return Response({"caption": caption}, status=200)
    
    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)


@api_view(['POST'])
def update_description(request):
    """
    Endpoint to update the description of an image. The user must own the image.
    - Expects 'description' and 'image_id' in the request body.
    """
    # Validate the incoming JWT token
    incoming_token = request.headers.get('token')
    token_validation = validate_JWT(incoming_token)
    
    if not token_validation['valid']:
        return Response({"message": token_validation["error"]}, status=401)

    description = request.data.get('description')
    image_id = request.data.get('image_id')
    
    # Validate the image id
    if not image_id:
        return Response({"message": "Image ID is required"}, status=400)
    elif not str(image_id).isdigit():
        return Response({"message": "Image ID is not valid"}, status=400)
        
    # Validate the new description
    if not description:
        return Response({"message": "Description is required"}, status=400)
    
    # Validate ownership of the image
    token = token_validation['token']
    image = ownership_validation(token['user_id'], image_id)
    
    if not image["valid"]:
        return Response({"message": image["message"]}, status=int(image["status"]))

    try:
        # Update image description
        image = image['image']
        image.description = description.strip()
        image.save()
        
        return Response({"message": "Description updated successfully"}, status=200)
    
    except Image.DoesNotExist:
        return Response({"message": "Image not found"}, status=404)

    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)


@api_view(['GET'])
def single_image(request, image_id):
    """
    Endpoint to retrieve a single image by its ID. The user must own the image.
    """
    # Validate the incoming JWT token
    incoming_token = request.headers.get('token')
    token_validation = validate_JWT(incoming_token)
    
    if not token_validation['valid']:
        return Response({"message": token_validation["error"]}, status=401)

    try:
        # Validate ownership of the image
        token = token_validation['token']
        image = ownership_validation(token['user_id'], image_id)
    
        if not image["valid"]:
            return Response({"message": image["message"]}, status=int(image["status"]))
        # Serialize the image data
        result = image_serializer(image['image'])
        return Response({"image": result.data}, status=200)
    
    except Image.DoesNotExist:
        return Response({"message": "Image not found"}, status=404)
    
    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)


@api_view(["POST"])
def delete_image(request):
    """
    Endpoint to delete an image. The user must own the image.
    - Expects 'image_id' in the request body.
    """
    # Validate the incoming JWT token
    incoming_token = request.headers.get('token')
    token_validation = validate_JWT(incoming_token)
    image_id = request.data.get('image_id')
    
    if not token_validation['valid']:
        return Response({"message": token_validation["error"]}, status=401)
    
        # Validate the image id
    if not image_id:
        return Response({"message": "Image ID is required"}, status=400)
    elif not str(image_id).isdigit():
        return Response({"message": "Image ID is not valid"}, status=400)
    
    # Validate ownership of the image
    token = token_validation['token']
    image = ownership_validation(token['user_id'], image_id)
    
    if not image["valid"]:
        return Response({"message": image["message"]}, status=int(image["status"]))

    try:
        # Delete image from S3 and database
        key = object_key_parser(image['image'].url)
        delete_from_s3(key)
        image["image"].delete()
        
        return Response({"message": "Image deleted successfully"}, status=200)
    
    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)
