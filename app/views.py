from typing import Any
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from .models import Tag, User, Post, Rate, Comment
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView, DeleteView, FormView
from .forms import PostForm, SignUpForm, CommentForm, RateForm
from django.core.mail import send_mail
from django.db.models import Avg, Count
class Welcome(TemplateView):
    template_name = 'welcome.html'

class Home(ListView):
    template_name = 'home.html'
    queryset = Post.objects.all().order_by('-created_at')
    context_object_name = 'posts'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['recommended'] = Post.objects.order_by('?')[:6]
        context['recent_post'] = Post.objects.all().order_by('-created_at')[:6]
        context['top_authors'] = User.objects.all().filter(is_superuser=False)
        context['best_stories'] = 0
        
        
        return context
    
class SignUpWithVerification(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        verify_url = self.request.build_absolute_uri(f'/verify/{user.pk}/{token}/')
        subject = 'Verify your email'
        message = f'Hello {user.username}, please click the link below to verify your email:\n\n{verify_url}'
        send_mail(subject, message, 'sender@example.com', [user.email])

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object  
        user.is_active = False
        user.save()
        self.send_verification_email(self.object)
        return response

class VerificationSuccessView(TemplateView):
    template_name = 'verification_success.html'

class VerificationErrorView(TemplateView):
    template_name = 'verification_error.html'

class VerifyEmailView(View):
    def get(self, request, user_pk, token):
        user = get_user_model().objects.get(pk=user_pk)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('verification_success')
        else:
            return redirect('verification_error')
        
class Login(LoginView):
    template_name = 'login.html'
    next_page = reverse_lazy('home')
    success_url = reverse_lazy('home')

class LogoutView(LoginRequiredMixin, LogoutView):
    login_url = reverse_lazy("login")
    next_page = reverse_lazy('home')

class CreatePostView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy("login")
    template_name = 'create_post.html'
    form_class = PostForm

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            print(form.cleaned_data['tags'])
            post.save()
            post.tags.add(*form.cleaned_data['tags'])
            return redirect('post', post.pk)

class MyPosts(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("login")
    model = Post
    template_name = 'my_posts.html'
    context_object_name = 'posts'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(user=self.request.user)
        return context

class DetailPost(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy("login")
    model = Post
    template_name = 'detail_post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        rating = Rate.objects.filter(post=self.object).aggregate(Avg('rate'))['rate__avg']
        if rating:
            context['rating'] = round(rating, 2)
        else:
            context['rating'] = 0
        context['comments'] = Comment.objects.filter(post=self.object)
        context['comment_form'] = CommentForm()  # Add comment form to context
        context['rate_form'] = RateForm()       # Add rate form to context
        return context

    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(request.POST)
        rate_form = RateForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            post = self.get_object()
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post', post_id=post.pk)  

        if rate_form.is_valid():
            rate = rate_form.save(commit=False)
            post = self.get_object()
            rate.post =post
            rate.user = request.user 
            rate.save()
            return redirect('post', post_id= post.pk)  

        return super().post(request, *args, **kwargs) 

class IsOwenerMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            return redirect('posts')
        return super().dispatch(request, *args, **kwargs)

class UpdatePost(LoginRequiredMixin, IsOwenerMixin, UpdateView):
    login_url = reverse_lazy("login")
    form_class = PostForm
    model = Post
    template_name = 'update_post.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('home')
    
class DeletePost(LoginRequiredMixin, IsOwenerMixin, DeleteView):
    login_url = reverse_lazy("login")
    model = Post
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('posts')
    
class Profile(DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['post_num'] = Post.objects.filter(user=self.object).count()
        context['comments_num'] = Comment.objects.filter(user=self.object).count()
        return context
    
class SetLike(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    def get(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        if request.user in post.liked_by.all():
            post.liked_by.remove(request.user)
        else:
            post.liked_by.add(request.user)
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer)

class Favorite(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("login")
    model = Post
    template_name = 'my_posts_fav.html'  
    context_object_name = 'posts'
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(liked_by=self.request.user)