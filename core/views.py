from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Usuario, Componente, ProgressoUsuario, TarefaManutencao

# ============= AUTENTICAÇÃO =============

def cadastro_view(request):
    #View de cadastro de usuário
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validações básicas
        if password != password_confirm:
            messages.error(request, 'As senhas não coincidem!')
            return render(request, 'cadastro.html')
        
        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe!')
            return render(request, 'cadastro.html')
        
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado!')
            return render(request, 'cadastro.html')
        
        # Criar usuário
        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
        return redirect('login')
    
    return render(request, 'cadastro.html')


def login_view(request):
    # View de Login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            user.ultimo_acesso = timezone.now()
            user.save()
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha incorretos!')
    
    return render(request, 'login.html')


def logout_view(request):
    #View de logout
    logout(request)
    messages.success(request, 'Você saiu do sistema.')
    return redirect('login')


# ============= PÁGINAS PRINCIPAIS =============

@login_required
def home_view(request):
    #Página inicial - Gabinete interativo
    componentes = Componente.objects.filter(ativo=True)
    
    # Pegar progresso do usuário
    componentes_visualizados = ProgressoUsuario.objects.filter(
        usuario=request.user
    ).values_list('componente_id', flat=True)
    
    context = {
        'componentes': componentes,
        'componentes_visualizados': list(componentes_visualizados),
    }
    
    return render(request, 'home.html', context)


@login_required
def componente_detalhe_view(request, componente_id):
    #Página de detalhe do componente
    componente = get_object_or_404(Componente, id=componente_id, ativo=True)
    
    # Registrar que o usuário visualizou este componente
    progresso, created = ProgressoUsuario.objects.get_or_create(
        usuario=request.user,
        componente=componente
    )
    
    # Verificar se usuário já tem tarefa de manutenção para este componente
    tem_tarefa = TarefaManutencao.objects.filter(
        usuario=request.user,
        componente=componente
    ).exists()
    
    context = {
        'componente': componente,
        'tem_tarefa': tem_tarefa,
    }
    
    return render(request, 'componente_detalhe.html', context)


@login_required
def cronograma_view(request):
    #Página do cronograma de manutenção
    tarefas_pendentes = TarefaManutencao.objects.filter(
        usuario=request.user,
        concluida=False
    ).order_by('data_agendada')
    
    tarefas_concluidas = TarefaManutencao.objects.filter(
        usuario=request.user,
        concluida=True
    ).order_by('-data_conclusao')[:10]  # Últimas 10
    
    context = {
        'tarefas_pendentes': tarefas_pendentes,
        'tarefas_concluidas': tarefas_concluidas,
    }
    
    return render(request, 'cronograma.html', context)


@login_required
def gerar_cronograma_view(request):
    #Gera cronograma automático de manutenção
    if request.method == 'POST':
        # Pegar componentes que o usuário já visualizou
        componentes_visualizados = ProgressoUsuario.objects.filter(
            usuario=request.user
        ).select_related('componente')
        
        if not componentes_visualizados:
            messages.warning(request, 'Você precisa visualizar pelo menos um componente primeiro!')
            return redirect('home')
        
        # Criar tarefas de manutenção para cada componente
        data_base = timezone.now().date()
        tarefas_criadas = 0
        
        for progresso in componentes_visualizados:
            componente = progresso.componente
            
            # Verificar se já existe tarefa para este componente
            if not TarefaManutencao.objects.filter(
                usuario=request.user,
                componente=componente
            ).exists():
                
                # Criar tarefa (agendada para daqui 30 dias)
                TarefaManutencao.objects.create(
                    usuario=request.user,
                    componente=componente,
                    descricao=f"Limpar {componente.nome}",
                    data_agendada=data_base + timedelta(days=30)
                )
                tarefas_criadas += 1
        
        if tarefas_criadas > 0:
            messages.success(request, f'{tarefas_criadas} tarefa(s) de manutenção criada(s)!')
        else:
            messages.info(request, 'Você já tem tarefas criadas para todos os componentes visualizados.')
        
        return redirect('cronograma')
    
    return redirect('cronograma')


@login_required
def tarefa_concluir_view(request, tarefa_id):
    #Marca uma tarefa como concluída
    tarefa = get_object_or_404(TarefaManutencao, id=tarefa_id, usuario=request.user)
    tarefa.marcar_concluida()
    messages.success(request, 'Tarefa concluída!')
    return redirect('cronograma')


@login_required
def tarefa_deletar_view(request, tarefa_id):
    #Deleta uma tarefa
    tarefa = get_object_or_404(TarefaManutencao, id=tarefa_id, usuario=request.user)
    tarefa.delete()
    messages.success(request, 'Tarefa removida!')
    return redirect('cronograma')