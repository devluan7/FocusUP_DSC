# home/forms/usuario_forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

# --- CORREÇÃO AQUI ---
from ..models.usuario import Usuario # <-- Corrigido para buscar na pasta models
# -----------------------

class UsuarioCadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('email', 'nome', 'nome_usuario', 'sexo', 'data_nascimento')

        widgets = {
            'email': forms.EmailInput(
                attrs={'placeholder': 'exemplo@email.com'}
            ),
            'nome': forms.TextInput(
                attrs={'placeholder': 'Digite seu nome completo'}
            ),
            'nome_usuario': forms.TextInput(
                attrs={'placeholder': 'Nome no FocusUP'}
            ),
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'} 
            ),
            'sexo': forms.Select(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajuste para garantir que choices seja uma lista antes de concatenar
        current_choices = list(self.fields['sexo'].choices)
        if current_choices and current_choices[0][0] != '':
             self.fields['sexo'].choices = [('', '---------')] + current_choices
        elif not current_choices:
             self.fields['sexo'].choices = [('', '---------')]


    def clean_nome_usuario(self):
        nome_usuario = self.cleaned_data.get("nome_usuario")
        if Usuario.objects.filter(nome_usuario__iexact=nome_usuario).exists():
            raise ValidationError("Esse nome de usuário já está em uso.")
        return nome_usuario

# -------------------------------------------------------------------
# --- NOVO FORMULÁRIO ADICIONADO ---
# -------------------------------------------------------------------

class UsuarioEditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        # Campos que o usuário poderá editar
        fields = ['nome', 'nome_usuario', 'email', 'sexo', 'data_nascimento']

        widgets = {
            'email': forms.EmailInput(
                attrs={'placeholder': 'exemplo@email.com'}
            ),
            'nome': forms.TextInput(
                attrs={'placeholder': 'Digite seu nome completo'}
            ),
            'nome_usuario': forms.TextInput(
                attrs={'placeholder': 'Nome no FocusUP'}
            ),
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'} 
            ),
            'sexo': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajuste para garantir que o "--------- " apareça no 'sexo'
        current_choices = list(self.fields['sexo'].choices)
        if current_choices and current_choices[0][0] != '':
             self.fields['sexo'].choices = [('', '---------')] + current_choices
        elif not current_choices:
             self.fields['sexo'].choices = [('', '---------')]

    def clean_nome_usuario(self):
        """ Validação para nome de usuário duplicado. """
        nome_usuario = self.cleaned_data.get('nome_usuario')
        # self.instance é o objeto 'Usuario' que está sendo editado
        if nome_usuario != self.instance.nome_usuario:
            # Se o nome mudou, verifica se o novo nome já existe
            if Usuario.objects.filter(nome_usuario__iexact=nome_usuario).exists():
                raise ValidationError("Esse nome de usuário já está em uso por outra conta.")
        return nome_usuario

    def clean_email(self):
        """ Validação para email duplicado. """
        email = self.cleaned_data.get('email')
        if email != self.instance.email:
            # Se o email mudou, verifica se o novo email já existe
            if Usuario.objects.filter(email__iexact=email).exists():
                raise ValidationError("Esse e-mail já está em uso por outra conta.")
        return email