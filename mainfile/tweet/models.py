from django.db import models
from django.contrib.auth.models import User
import os

class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    img_url = models.URLField(blank=True, null=True, max_length=2000)
    img = models.ImageField(upload_to='tweets/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='tweet_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='tweet_dislikes', blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
    
    def total_likes(self):
        return self.likes.count()
    
    def total_dislikes(self):
        return self.dislikes.count()
    
    def has_media(self):
        return bool(self.img or self.img_url or self.video)
    
    def save(self, *args, **kwargs):
        # Check if this is an update and if there's a new image
        if self.pk:
            try:
                old_instance = Tweet.objects.get(pk=self.pk)
                # If there's a new image and an old one exists, delete the old one
                if self.img and old_instance.img and self.img != old_instance.img:
                    if os.path.isfile(old_instance.img.path):
                        os.remove(old_instance.img.path)
                # If there's a new video and an old one exists, delete the old one
                if self.video and old_instance.video and self.video != old_instance.video:
                    if os.path.isfile(old_instance.video.path):
                        os.remove(old_instance.video.path)
            except Tweet.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete associated media files before deleting the tweet
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        if self.video and os.path.isfile(self.video.path):
            os.remove(self.video.path)
        super().delete(*args, **kwargs)

class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

