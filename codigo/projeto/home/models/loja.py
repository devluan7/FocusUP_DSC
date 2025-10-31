# home/models/loja.py

from django.db import models
from .usuario import Usuario

class ItemLoja(models.Model):
    # Exemplo de choices, você pode adicionar mais
    TIPO_CHOICES = [
        ('AVATAR', 'Avatar'),
        ('ITEM_PODER', 'Item de Poder'),
        ('CUSTOMIZACAO', 'Customização'),
    ]

    id_item = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    preco_moedas = models.IntegerField()
    efeito = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.nome

class Compra(models.Model):
    id_compra = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemLoja, on_delete=models.PROTECT) # PROTECT evita apagar um item que já foi comprado
    data_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.nome_usuario} comprou {self.item.nome}'