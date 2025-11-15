from django.test import TestCase
from .models.usuario import Usuario
from .models.conquista import Conquista, UsuarioConquista

# Testa o que acontece quando um usuário ganha uma conquista (XP, nível, etc.)
class ConquistaSignalTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email='testuser@example.com',
            nome='Test User',
            nome_usuario='testuser',
            senha='password123'
        )
        self.conquista = Conquista.objects.create(
            nome="Primeira Conquista",
            criterio="Completar uma tarefa",
            xp_points=80
        )

    def test_ganha_xp_ao_receber_conquista(self):
        self.usuario.xp_atual = 10
        self.usuario.save()

        UsuarioConquista.objects.create(usuario=self.usuario, conquista=self.conquista)

        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.xp_atual, 90)
        self.assertEqual(self.usuario.nivel, 1)

    def test_sobe_de_nivel_ao_receber_conquista(self):
        self.usuario.xp_atual = 50
        self.usuario.save()

        UsuarioConquista.objects.create(usuario=self.usuario, conquista=self.conquista)

        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nivel, 2)
        self.assertEqual(self.usuario.xp_atual, 30)