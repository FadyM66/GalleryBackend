from django.db import models

class User(models.Model): 
    id = models.AutoField(primary_key=True) 
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True) 
    hashed_password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user" 
        