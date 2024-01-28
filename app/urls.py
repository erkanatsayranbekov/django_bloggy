from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('welcome/', Welcome.as_view(), name='welcome'),
    path('signup/', SignUpWithVerification.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name = 'login.html', next_page = reverse_lazy('home')), name='login'),
    path('verify/<int:user_pk>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('verification_success/', VerificationSuccessView.as_view(), name='verification_success'),
    path('verification_error/', VerificationErrorView.as_view(), name='verification_error'),
    path('posts/', MyPosts.as_view(), name='posts'),
    path('post/<int:post_id>', DetailPost.as_view(), name='post'),
    path('delete/<int:post_id>', DeletePost.as_view(), name='delete'),
    path('update_post/<int:post_id>', UpdatePost.as_view(), name='update_post'),
    path('create/', CreatePostView.as_view(), name='create_post'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/<int:user_id>', Profile.as_view(), name='profile'),
    path('like/<int:post_id>', SetLike.as_view(), name='like'),
    path('favorite/', Favorite.as_view(), name='favorite'),
] 