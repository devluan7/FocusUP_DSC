# home/backends.py

from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class EmailOrUsernameBackend(ModelBackend):
   
    def authenticate(self, request, username=None, password=None, **kwargs):
        # O parâmetro 'username' pode conter tanto o nome_usuario quanto o email
        try:
            # Verifica se o input do usuário é um email e busca por ele
            if '@' in username:
                user = Usuario.objects.get(email__iexact=username)
            # Se não for um email, busca pelo nome_usuario
            else:
                user = Usuario.objects.get(nome_usuario__iexact=username)
        except Usuario.DoesNotExist:
            # Se não encontrar nenhum usuário, a autenticação falha
            return None

        # Se encontrou um usuário, verifica se a senha está correta
        if user.check_password(password):
            return user # Retorna o objeto do usuário se a senha estiver correta
        
        return None # Retorna None se a senha estiver incorreta

    def get_user(self, user_id):
        # Este método é necessário para que o Django consiga obter o usuário da sessão
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None