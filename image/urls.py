from django.urls import path
from .views import *

urlpatterns = [
    # Endpoint to get all images
    path('', get_images),  # GET request to fetch all images

    # Endpoint to upload a new image
    path('upload', upload_image),  # POST request to upload an image

    # Endpoint to generate a caption for an image
    path('generate-caption', caption_generator),  # POST request to generate a caption for an image using AI

    # Endpoint to update the description of an image
    path('update-description', update_description),  # POST request to update image description

    # Endpoint to get details of a specific image by its ID
    path('<int:image_id>', single_image),  # GET request to fetch a single image by its ID

    # Endpoint to delete an image
    path('delete-image', delete_image),  # POST request to delete an image
]
