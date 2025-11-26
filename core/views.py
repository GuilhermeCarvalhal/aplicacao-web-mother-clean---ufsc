import requests
from django.http import JsonResponse
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

def handler404(request, exception):
    #View personalizada para erro 404
    return render(request, '404.html', status=404)

def handler500(request):
    #View personalizada para erro 500
    return render(request, '500.html', status=500)

@login_required
def clima_view(request):
    """Busca informações de clima para recomendações de manutenção"""
    cidade = request.GET.get('cidade', 'Florianopolis')
    
    # Sua chave da API aqui
    api_key = 'f778b45fe8ff8d766118f33b351ad9cd' 
    
    url = f'http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br'
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            temperatura = data['main']['temp']
            umidade = data['main']['humidity']
            descricao = data['weather'][0]['description']
            
            # Recomendação baseada na umidade
            if umidade < 40:
                recomendacao = "⚠️ Umidade baixa! Aumente a frequência de limpeza - pó acumula mais rápido."
            elif umidade > 70:
                recomendacao = "💧 Umidade alta! Fique atento à condensação nos componentes."
            else:
                recomendacao = "✅ Umidade ideal para seus componentes!"
            
            clima_info = {
                'temperatura': round(temperatura, 1),
                'umidade': umidade,
                'descricao': descricao,
                'recomendacao': recomendacao,
                'cidade': data['name']
            }
            
            return JsonResponse(clima_info)
        else:
            return JsonResponse({'erro': 'Cidade não encontrada'}, status=404)
    
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)