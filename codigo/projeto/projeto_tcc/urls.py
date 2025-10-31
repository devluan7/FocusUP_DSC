# projeto_tcc/urls.py

from django.contrib import admin
# IMPORTANTE: Verifique estes imports
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- URLs de Reset de Senha (Globais) ---
    path('reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name="home/reset_senha/password_reset_form.html",
            # Verifique se este caminho está correto:
            email_template_name="home/reset_senha/password_reset_email.html",
            success_url=reverse_lazy('password_reset_done')
        ),
        name='password_reset'),

    path('reset_password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name="home/reset_senha/password_reset_done.html"
        ),
        name='password_reset_done'),

    # Verifique se o name='password_reset_confirm' está aqui:
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name="home/reset_senha/password_reset_confirm.html",
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'), # <-- O nome que a view procura

    path('reset_password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name="home/reset_senha/password_reset_complete.html"
        ),
        name='password_reset_complete'),

    # URL do app 'home' (deve vir DEPOIS das de reset)
    path('', include('home.urls', namespace='home')),
]

urlpatterns += staticfiles_urlpatterns()