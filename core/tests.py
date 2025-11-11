from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Componente, ProgressoUsuario, TarefaManutencao
from django.utils import timezone
from datetime import timedelta

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    # Testes do modelo Usuario
    
    def setUp(self):
        # Configuração inicial para os testes
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='senha123'
        )
    
    def test_criar_usuario(self):
        # Teste: Criar um usuário
        self.assertEqual(self.usuario.username, 'testuser')
        self.assertEqual(self.usuario.email, 'test@example.com')
        self.assertTrue(self.usuario.check_password('senha123'))
    
    def test_usuario_string_representation(self):
        # Teste: Representação em string do usuário
        self.assertEqual(str(self.usuario), 'testuser')


class ComponenteModelTest(TestCase):
    # Testes do modelo Componente
    
    def setUp(self):
        self.componente = Componente.objects.create(
            nome='Processador',
            descricao='CPU do computador',
            instrucoes_limpeza='Use ar comprimido',
            ordem_exibicao=1,
            ativo=True
        )
    
    def test_criar_componente(self):
        # Teste: Criar um componente
        self.assertEqual(self.componente.nome, 'Processador')
        self.assertEqual(self.componente.ordem_exibicao, 1)
        self.assertTrue(self.componente.ativo)
    
    def test_componente_string_representation(self):
        # Teste: Representação em string do componente
        self.assertEqual(str(self.componente), 'Processador')


class ProgressoUsuarioModelTest(TestCase):
    # Testes do modelo ProgressoUsuario
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='senha123'
        )
        self.componente = Componente.objects.create(
            nome='Memória RAM',
            descricao='Memória do computador',
            instrucoes_limpeza='Limpe com pano seco',
            ordem_exibicao=2
        )
        self.progresso = ProgressoUsuario.objects.create(
            usuario=self.usuario,
            componente=self.componente,
            visualizado=True
        )
    
    def test_criar_progresso(self):
        # Teste: Criar um registro de progresso
        self.assertEqual(self.progresso.usuario, self.usuario)
        self.assertEqual(self.progresso.componente, self.componente)
        self.assertTrue(self.progresso.visualizado)
    
    def test_progresso_unique_constraint(self):
        # Teste: Não permitir duplicação de progresso
        with self.assertRaises(Exception):
            ProgressoUsuario.objects.create(
                usuario=self.usuario,
                componente=self.componente,
                visualizado=True
            )


class TarefaManutencaoModelTest(TestCase):
    # Testes do modelo TarefaManutencao
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='senha123'
        )
        self.componente = Componente.objects.create(
            nome='Placa de Vídeo',
            descricao='GPU do computador',
            instrucoes_limpeza='Limpe as ventoinhas',
            ordem_exibicao=3
        )
        self.tarefa = TarefaManutencao.objects.create(
            usuario=self.usuario,
            componente=self.componente,
            descricao='Limpar Placa de Vídeo',
            data_agendada=timezone.now().date() + timedelta(days=30)
        )
    
    def test_criar_tarefa(self):
        # Teste: Criar uma tarefa de manutenção
        self.assertEqual(self.tarefa.descricao, 'Limpar Placa de Vídeo')
        self.assertFalse(self.tarefa.concluida)
        self.assertIsNone(self.tarefa.data_conclusao)
    
    def test_marcar_tarefa_concluida(self):
        # Teste: Marcar uma tarefa como concluída
        self.tarefa.marcar_concluida()
        self.assertTrue(self.tarefa.concluida)
        self.assertIsNotNone(self.tarefa.data_conclusao)


class AutenticacaoViewsTest(TestCase):
    # Testes das views de autenticação
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='senha123'
        )
    
    def test_pagina_login_get(self):
        # Teste: Acessar página de login
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_login_com_credenciais_validas(self):
        # Teste: Login com credenciais válidas
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'senha123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('home'))
    
    def test_login_com_credenciais_invalidas(self):
        # Teste: Login com credenciais inválidas
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'senhaerrada'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuário ou senha incorretos')
    
    def test_pagina_cadastro_get(self):
        # Teste: Acessar página de cadastro
        response = self.client.get(reverse('cadastro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastro.html')
    
    def test_cadastro_usuario_valido(self):
        # Teste: Cadastrar novo usuário com dados válidos
        response = self.client.post(reverse('cadastro'), {
            'username': 'novouser',
            'email': 'novo@example.com',
            'password': 'senha123',
            'password_confirm': 'senha123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Usuario.objects.filter(username='novouser').exists())
    
    def test_cadastro_senhas_diferentes(self):
        # Teste: Cadastro com senhas não coincidentes
        response = self.client.post(reverse('cadastro'), {
            'username': 'novouser',
            'email': 'novo@example.com',
            'password': 'senha123',
            'password_confirm': 'senha456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'As senhas não coincidem')
    
    def test_logout(self):
        # Teste: Logout do usuário
        self.client.login(username='testuser', password='senha123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class HomeViewTest(TestCase):
    # Testes da view home
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='senha123'
        )
        self.componente = Componente.objects.create(
            nome='Processador',
            descricao='CPU',
            instrucoes_limpeza='Limpar',
            ordem_exibicao=1,
            ativo=True
        )
    
    def test_home_requer_login(self):
        # Teste: Home requer autenticação
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect para login
    
    def test_home_com_usuario_logado(self):
        # Teste: Home com usuário autenticado
        self.client.login(username='testuser', password='senha123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Processador')


class ComponenteDetalheViewTest(TestCase):
    # Testes da view de detalhes do componente
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='senha123'
        )
        self.componente = Componente.objects.create(
            nome='Memória RAM',
            descricao='Memória do PC',
            instrucoes_limpeza='Limpe com cuidado',
            ordem_exibicao=2,
            ativo=True
        )
    
    def test_componente_detalhe_requer_login(self):
        # Teste: Detalhes do componente requer autenticação
        response = self.client.get(
            reverse('componente_detalhe', args=[self.componente.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect para login
    
    def test_componente_detalhe_registra_progresso(self):
        # Teste: Visualizar componente registra progresso
        self.client.login(username='testuser', password='senha123')
        response = self.client.get(
            reverse('componente_detalhe', args=[self.componente.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o progresso foi registrado
        progresso = ProgressoUsuario.objects.filter(
            usuario=self.usuario,
            componente=self.componente
        )
        self.assertTrue(progresso.exists())


class CronogramaViewTest(TestCase):
    # Testes da view de cronograma
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='senha123'
        )
        self.componente = Componente.objects.create(
            nome='Fonte',
            descricao='Fonte de alimentação',
            instrucoes_limpeza='Limpe com ar comprimido',
            ordem_exibicao=4,
            ativo=True
        )
    
    def test_cronograma_requer_login(self):
        # Teste: Cronograma requer autenticação
        response = self.client.get(reverse('cronograma'))
        self.assertEqual(response.status_code, 302)
    
    def test_gerar_cronograma(self):
        # Teste: Gerar cronograma automático
        self.client.login(username='testuser', password='senha123')
        
        # Primeiro visualizar um componente
        ProgressoUsuario.objects.create(
            usuario=self.usuario,
            componente=self.componente
        )
        
        # Gerar cronograma
        response = self.client.post(reverse('gerar_cronograma'))
        self.assertEqual(response.status_code, 302)
        
        # Verificar se tarefa foi criada
        tarefa = TarefaManutencao.objects.filter(
            usuario=self.usuario,
            componente=self.componente
        )
        self.assertTrue(tarefa.exists())


class CRUDOperacoesTest(TestCase):
    # Testes das operações CRUD
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='senha123'
        )
        self.componente = Componente.objects.create(
            nome='HD/SSD',
            descricao='Armazenamento',
            instrucoes_limpeza='Não precisa limpar internamente',
            ordem_exibicao=5,
            ativo=True
        )
        self.client.login(username='testuser', password='senha123')
    
    def test_crud_create(self):
        # Teste: Operação CREATE
        tarefa = TarefaManutencao.objects.create(
            usuario=self.usuario,
            componente=self.componente,
            descricao='Verificar HD/SSD',
            data_agendada=timezone.now().date()
        )
        self.assertIsNotNone(tarefa.id)
    
    def test_crud_read(self):
        # Teste: Operação READ
        TarefaManutencao.objects.create(
            usuario=self.usuario,
            componente=self.componente,
            descricao='Verificar HD/SSD',
            data_agendada=timezone.now().date()
        )
        tarefas = TarefaManutencao.objects.filter(usuario=self.usuario)
        self.assertEqual(tarefas.count(), 1)
    
    def test_crud_update(self):
        # Teste: Operação UPDATE
        tarefa = TarefaManutencao.objects.create(
            usuario=self.usuario,
            componente=self.componente,
            descricao='Verificar HD/SSD',
            data_agendada=timezone.now().date()
        )
        tarefa.concluida = True
        tarefa.save()
        
        tarefa_atualizada = TarefaManutencao.objects.get(id=tarefa.id)
        self.assertTrue(tarefa_atualizada.concluida)
    
    def test_crud_delete(self):
        # Teste: Operação DELETE
        tarefa = TarefaManutencao.objects.create(
            usuario=self.usuario,
            componente=self.componente,
            descricao='Verificar HD/SSD',
            data_agendada=timezone.now().date()
        )
        tarefa_id = tarefa.id
        tarefa.delete()
        
        with self.assertRaises(TarefaManutencao.DoesNotExist):
            TarefaManutencao.objects.get(id=tarefa_id)