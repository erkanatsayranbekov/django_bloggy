from django.forms import ModelForm, modelformset_factory
from .models import Tag, User, Post, Comment, Rate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django import forms

class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Пароль"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Подтвердите пароль"}),
        strip=False,
        help_text=("Подтвердите ваш пароль"),
    )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'image', 'birthdate', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder':'Имя пользователя', 'class': 'email_input'}),
            'email': forms.EmailInput(attrs={'placeholder':'Почта'}),
            'first_name': forms.TextInput(attrs={'placeholder':'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Фамилия'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }
    
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class PostForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите тэги через запятую'}), required=False)

    class Meta:
        model = Post
        fields = ['title', 'body', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Заголовок'}),
            'body': forms.Textarea(attrs={'placeholder': 'Текст поста'}),
        }

    def clean_tags(self):
        tag_names = self.cleaned_data['tags'].strip().split(',')
        tags = [Tag.objects.get_or_create(name=name.strip())[0] for name in tag_names]
        return tags

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        
class RateForm(ModelForm):
    class Meta:
        model = Rate
        fields = ['rate']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Добавьте комментарий', 'cols': 30, 'rows': 10}),
        }