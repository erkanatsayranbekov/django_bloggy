from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator

class User(AbstractUser):
    image = models.ImageField(upload_to="users", default='users/user.png')
    birthdate = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=2550, null=True, blank=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
class Tag(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="posts")
    image = models.ImageField(upload_to="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_by = models.ManyToManyField(User, related_name="liked_posts")
    def __str__(self):
        return self.title + " - " + self.user.first_name + "(" + str(self.created_at) + ")"
    
    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
    
class Rate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rate = models.IntegerField(validators=[MaxValueValidator(5)])
    
    def __str__(self):
        return self.rate
    
    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.body
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"