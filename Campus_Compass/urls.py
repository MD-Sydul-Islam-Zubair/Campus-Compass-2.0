from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from CC import views as CC_views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


from CC import views


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
    path('createinstitute/', CC_views.upload_institute, name='upload_institute'),
    path('createcircular/', CC_views.upload_circular, name='upload_circular'),
    path('compare/', CC_views.institute_comparison, name='institute_comparison'),
    path('institute/<int:institute_id>/update/', CC_views.update_institute, name='update_institute'),
    path('institute/image/<int:image_id>/delete/', CC_views.delete_institute_image, name='delete_institute_image'),
  
    path('notifications/', CC_views.notifications_view, name='notifications'),
    path('notifications/unread-count/', CC_views.get_unread_notification_count, name='unread_notification_count'),
    path('notifications/<int:notification_id>/mark-read/', CC_views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', CC_views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', CC_views.delete_notification, name='delete_notification'),
    path('notifications/preview/', CC_views.notification_preview, name='notification_preview'),
    path('notifications/<int:notification_id>/mark-unread/', CC_views.mark_notification_unread, name='mark_notification_unread'),
    path('notifications/clear-all/', CC_views.clear_all_notifications, name='clear_all_notifications'),

    # Authentication URLs
    path('accounts/login/', CC_views.login_view, name='login'),
    path('accounts/logout/', CC_views.logout_view, name='logout'),
    path('accounts/signup/', CC_views.signup_view, name='signup'),
    path('accounts/profile/', CC_views.profile_view, name='profile'),

    path('institute/<int:institute_id>/comment/', CC_views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', CC_views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', CC_views.delete_comment, name='delete_comment'),

 # ... your existing URLs ...
    path('institute/<int:institute_id>/toggle-bookmark/', CC_views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', CC_views.bookmarked_institutes, name='bookmarks'),


    path('institute/<int:institute_id>/create-hostel/', CC_views.create_hostel, name='create_hostel'),
    path('hostel/<int:pk>/', CC_views.HostelDetailView.as_view(), name='hostel_detail'),
    path('hostel/<int:hostel_id>/delete/', CC_views.delete_hostel, name='delete_hostel'),
    path('hostel/<int:hostel_id>/update/', CC_views.update_hostel, name='update_hostel'),
    path('hostel/image/<int:image_id>/delete/', CC_views.delete_hostel_image, name='delete_hostel_image'),




    path('subscribe/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('subscribe/redirect/', views.subscribe_redirect, name='subscribe_redirect'),


    # Blog URLs
    path('blog/', views.blog_home, name='blog_home'),
    path('blog/create/', views.create_blog_post, name='create_blog_post'),
    path('blog/post/<int:post_id>/', views.blog_post_detail, name='blog_post_detail'),
    path('blog/post/<int:post_id>/like/', views.like_blog_post, name='like_blog_post'),


    # Password change
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='CC/registration/password_change.html',
        success_url=reverse_lazy('password_change_done')
    ), name='password_change'),

    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='CC/password_change_done.html'
    ), name='password_change_done'),

    # Password reset
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='CC/password_reset_form.html',
        email_template_name='CC/password_reset_email.html',
        subject_template_name='CC/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done'),
        html_email_template_name='CC/password_reset_email.html',
    ), name='password_reset'),

    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='CC/password_reset_done.html'
    ), name='password_reset_done'),

    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='CC/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='CC/password_reset_complete.html'
    ), name='password_reset_complete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
