from django.urls import path
from authentication import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.register, name="register"),
    path("user_login/", views.user_login, name="user_login"),
    path("sair/", views.sair, name="sair"),
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(template_name="reset_password.html"),
        name="password_reset",
    ),
    path(
        "reset_password/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset_password/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_password/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
