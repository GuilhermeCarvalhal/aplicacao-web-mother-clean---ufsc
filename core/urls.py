from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Páginas principais
    path('', views.home_view, name='home'),
    path('componente/<int:componente_id>/', views.componente_detalhe_view, name='componente_detalhe'),
    
    # Cronograma
    path('cronograma/', views.cronograma_view, name='cronograma'),
    path('cronograma/gerar/', views.gerar_cronograma_view, name='gerar_cronograma'),
    path('tarefa/<int:tarefa_id>/concluir/', views.tarefa_concluir_view, name='tarefa_concluir'),
    path('tarefa/<int:tarefa_id>/deletar/', views.tarefa_deletar_view, name='tarefa_deletar'),
]