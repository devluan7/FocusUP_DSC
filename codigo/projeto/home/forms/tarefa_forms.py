# home/forms/Tarefa_forms.py
from django import forms
from ..models import Tarefa

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'frequencia', 'hora_lembrete', 'descricao']
        widgets = {
            'hora_lembrete': forms.TimeInput(attrs={'type': 'time'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adicione uma descrição (opcional)'}),
        }