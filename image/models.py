from django.db import models
from authentication.models import User 

class Image(models.Model): 
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    modified_at = models.DateTimeField(auto_now=True)  
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="images"
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "image" 