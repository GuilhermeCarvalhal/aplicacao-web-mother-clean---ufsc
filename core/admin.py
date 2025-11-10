from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Componente, ProgressoUsuario, TarefaManutencao

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'data_cadastro', 'ultimo_acesso']
    list_filter = ['data_cadastro', 'is_staff']
    search_fields = ['username', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('data_cadastro', 'ultimo_acesso')
        }),
    )
    
    readonly_fields = ['data_cadastro']

@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ordem_exibicao', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    list_editable = ['ordem_exibicao', 'ativo']
    ordering = ['ordem_exibicao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'imagem_url')
        }),
        ('Instruções', {
            'fields': ('instrucoes_limpeza',)
        }),
        ('Configurações', {
            'fields': ('ordem_exibicao', 'ativo')
        }),
    )

@admin.register(ProgressoUsuario)
class ProgressoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'componente', 'visualizado', 'data_visualizacao']
    list_filter = ['visualizado', 'data_visualizacao', 'componente']
    search_fields = ['usuario__username', 'componente__nome']
    date_hierarchy = 'data_visualizacao'
    
    def has_add_permission(self, request):
        # Não permitir adicionar manualmente (é criado automaticamente)
        return False

@admin.register(TarefaManutencao)
class TarefaManutencaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'componente', 'descricao', 'data_agendada', 'concluida', 'data_conclusao']
    list_filter = ['concluida', 'data_agendada', 'componente']
    search_fields = ['usuario__username', 'componente__nome', 'descricao']
    date_hierarchy = 'data_agendada'
    list_editable = ['concluida']
    
    fieldsets = (
        ('Informações', {
            'fields': ('usuario', 'componente', 'descricao')
        }),
        ('Agendamento', {
            'fields': ('data_agendada',)
        }),
        ('Status', {
            'fields': ('concluida', 'data_conclusao')
        }),
    )
    
    readonly_fields = ['data_criacao', 'data_conclusao']
    
    def save_model(self, request, obj, form, change):
        if obj.concluida and not obj.data_conclusao:
            from django.utils import timezone
            obj.data_conclusao = timezone.now()
        super().save_model(request, obj, form, change)