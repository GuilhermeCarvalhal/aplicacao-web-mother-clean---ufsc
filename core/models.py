# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Componente(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    instrucoes_limpeza = models.TextField(help_text="Como limpar este componente")
    imagem_url = models.CharField(max_length=500, blank=True)
    ordem_exibicao = models.IntegerField(default=0, help_text="Ordem de exibição no gabinete")
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'
        ordering = ['ordem_exibicao']
    
    def __str__(self):
        return self.nome

class ProgressoUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='progressos')
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    visualizado = models.BooleanField(default=True)
    data_visualizacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Progresso do Usuário'
        verbose_name_plural = 'Progressos dos Usuários'
        unique_together = ['usuario', 'componente']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.componente.nome}"

class TarefaManutencao(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tarefas')
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_agendada = models.DateField()
    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Tarefa de Manutenção'
        verbose_name_plural = 'Tarefas de Manutenção'
        ordering = ['data_agendada', 'concluida']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.descricao}"
    
    def marcar_concluida(self):
        self.concluida = True
        self.data_conclusao = timezone.now()
        self.save()