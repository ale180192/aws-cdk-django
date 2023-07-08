from django.db import models


class Post(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    user_id = models.PositiveIntegerField()
    title = models.CharField(max_length=128)
    body = models.TextField()

class Comments(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    body = models.TextField()
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name="comments")


