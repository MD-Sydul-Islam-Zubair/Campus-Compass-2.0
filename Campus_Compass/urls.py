from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from CC import views as CC_views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Main Application URLs
    path('home/', CC_views.Home, name='Home'),
    path('', CC_views.Login, name='home_redirect'),
    path('universities/', CC_views.Universities, name='Universities'),
    path('colleges/', CC_views.Colleges, name='Colleges'),
    path('institute/<int:institute_id>/', CC_views.institute_detail, name='institute_detail'),
    path('circulars/', CC_views.circulars, name='circulars'),
    path('search/', CC_views.search_results, name='search_results'),
    path('update_profile_pic/', CC_views.update_profile_pic, name='update_profile_pic'),
    path('clear-signup-session/', CC_views.clear_signup_session, name='clear_signup_session'),
    path('createuniversity/',CC_views.upload_institute, name='upload_institute'),
    path('createcircular/',CC_views.upload_circular, name='upload_circular'),
 
    # Authentication URLs - Using accounts/ prefix
    path('accounts/', include([
        # Custom auth views
   
            path('login/', CC_views.login_view, name='login'),
        path('logout/', CC_views.logout_view, name='logout'),
        path('signup/', CC_views.signup_view, name='signup'),
        path('profile/', CC_views.profile_view, name='profile'),
        # Password change
       path('password_change/', auth_views.PasswordChangeView.as_view(
    template_name='CC/registration/password_change.html',
    success_url=reverse_lazy('password_change_done')
), name='password_change'),

path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
    template_name='CC/password_change_done.html'
), name='password_change_done'),



        # Password reset
        path('password_reset/', auth_views.PasswordResetView.as_view(
            template_name='CC/password_reset_form.html',
            email_template_name='CC/password_reset_email.html',
            subject_template_name='CC/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
            html_email_template_name='CC/password_reset_email.html',
        ), name='password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='CC/password_reset_done.html'
        ), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='CC/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ), name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='CC/password_reset_complete.html'
        ), name='password_reset_complete'),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)