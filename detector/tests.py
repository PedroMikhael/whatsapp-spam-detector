from django.test import TestCase
from detector.services import verificar_texto_spam

class SpamTestCase(TestCase):
    def test_texto_spam(self):
        resultado = verificar_texto_spam("Ganhe dinheiro agora!")
        self.assertTrue(resultado["spam"])

    def test_texto_legitimo(self):
        resultado = verificar_texto_spam("Oi, tudo bem?")
        self.assertFalse(resultado["spam"])
