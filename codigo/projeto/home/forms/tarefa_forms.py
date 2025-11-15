from django import forms
from ..models import Tarefa

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'hora_lembrete', 'descricao']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: Fazer almoço'}),
            'hora_lembrete': forms.TimeInput(attrs={'type': 'time'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adicione uma descrição (opcional)'}),
        }
        
        labels = {
            'titulo': 'Título da Tarefa',
            'hora_lembrete': 'Horário Padrão (opcional)',
        }