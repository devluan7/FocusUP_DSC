# Em home/forms/perfil_forms.py
from django import forms
# Importe o modelo UsuarioFoco (ajuste o caminho se necessário)
from ..models.usuario_foco import UsuarioFoco 

# Define as opções de foco, para o usuário não digitar errado
FOCO_CHOICES = [
    ('', '---------'), 
    ('academia', 'Academia'),
    ('estudos', 'Estudos'),
    ('trabalho', 'Trabalho'),
    ('saude', 'Saúde'),
    ('casa', 'Casa'),
    ('lazer', 'Lazer'),
    ('outro', 'Outro (Especifique nos Detalhes)'),
]

# --- CAMPOS ESPECÍFICOS (Apenas para Academia, por enquanto) ---
NIVEL_TREINO_CHOICES = [('', '---------'), ('iniciante', 'Iniciante'), ('intermediario', 'Intermediário'), ('avancado', 'Avançado')]
LOCAL_TREINO_CHOICES = [('', '---------'), ('casa', 'Em Casa'), ('academia', 'Na Academia')]
FREQ_TREINO_CHOICES = [('', '---------'), ('1', '1x'), ('2', '2x'), ('3', '3x'), ('4', '4x'), ('5', '5x'), ('6', '6x'), ('7', '7x')]

class UsuarioFocoForm(forms.ModelForm):
    """
    Formulário para gerenciar os perfis de foco (UsuarioFoco).
    Com campos específicos para ALGUNS focos e placeholder dinâmico para 'detalhes'.
    """
    
    foco_nome = forms.ChoiceField(
        choices=FOCO_CHOICES,
        label="Qual é o Foco?",
        widget=forms.Select(attrs={'id': 'id_foco_nome_select'}) # ID para JS
    )

    # --- CAMPOS ESPECÍFICOS (Apenas Academia, required=False) ---
    
    # Campo Altura (Adicionado)
    altura = forms.DecimalField(
        label="Altura (metros)",
        required=False,
        max_digits=3, # Ex: 1.76
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '1.00', 'max': '2.50', 'placeholder': 'Ex: 1.76'})
    )
    
    # Campo Peso (Ajustado)
    peso = forms.DecimalField(
        label="Peso Atual (kg)", 
        required=False, 
        max_digits=5, 
        decimal_places=1, 
        widget=forms.NumberInput(attrs={'step': '0.5', 'min': '30', 'max': '200'}) 
    )
    
    nivel_treino = forms.ChoiceField(choices=NIVEL_TREINO_CHOICES, label="Seu Nível", required=False)
    local_treino = forms.ChoiceField(choices=LOCAL_TREINO_CHOICES, label="Onde você treina?", required=False)
    freq_treino = forms.ChoiceField(choices=FREQ_TREINO_CHOICES, label="Frequência Semanal", required=False)
    objetivo_academia = forms.CharField(label="Principal Objetivo Fitness", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Ganhar massa, perder peso, definição'}))
    
    # --- Os campos de ESTUDOS foram REMOVIDOS ---

    class Meta:
        model = UsuarioFoco 
        # Mantemos 'detalhes' para notas extras.
        fields = ['foco_nome', 'detalhes'] 
        
        labels = {
            'detalhes': 'Observações Adicionais (para a IA)',
        }
        
        widgets = {
            # O placeholder aqui será genérico, o JS vai trocá-lo.
            'detalhes': forms.Textarea(
                attrs={'rows': 6, 'placeholder': 'Descreva seus objetivos, dificuldades, preferências, etc. Quanto mais detalhes, melhor a IA!', 'id': 'id_detalhes_textarea'}
            ),
        }

    # O __init__ modificado para preencher os campos extras (Academia) a partir do JSONField
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance') 
        initial_data = {}

        if instance and instance.dados_especificos:
            # Pega os dados do JSON para pré-preencher
            initial_data = instance.dados_especificos.copy()

        # Adiciona os dados do JSON ao 'initial' do formulário
        kwargs['initial'] = initial_data 
        
        super().__init__(*args, **kwargs)

        # IDs específicos para o JS encontrar os campos extras
        # Adicionado 'altura' à lista
        campos_extras_academia = [
            'altura', 'peso', 'nivel_treino', 'local_treino', 'freq_treino', 'objetivo_academia'
        ]
        # Adicione outras listas se criar campos para outros focos
        
        for nome_campo in campos_extras_academia:
            if nome_campo in self.fields:
                self.fields[nome_campo].widget.attrs['id'] = f'id_extra_{nome_campo}'