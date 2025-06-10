from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from datetime import date
from .forms import *
from .models import *

def home(request):
    return render(request, 'home.html')

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            PerfilCliente.objects.create(
                usuario=user,
                matricula=form.cleaned_data['matricula'],
                telefone=form.cleaned_data['telefone']
            )
            messages.success(request, 'Cadastro de cliente realizado com sucesso! Por favor, faça o login.')
            return redirect('login')
    else:
        form = RegistroClienteForm()
    return render(request, 'registro_cliente.html', {'form': form})

def registro_funcionario(request):
    if request.method == 'POST':
        form = RegistroFuncionarioForm(request.POST)
        if form.is_valid():
            user = form.save() # O save do form já lida com a senha
            PerfilFuncionario.objects.create(
                usuario=user,
                especialidade=form.cleaned_data['especialidade']
            )
            messages.success(request, 'Cadastro de funcionário realizado com sucesso! Por favor, faça o login.')
            return redirect('login')
    else:
        form = RegistroFuncionarioForm()
    return render(request, 'registro_funcionario.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo_usuario = request.POST.get('tipo_usuario')
        if not (email and password and tipo_usuario):
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'login.html')
        user_qs = User.objects.filter(email=email)
        if not user_qs.exists():
            messages.error(request, 'Email ou senha inválidos.')
            return render(request, 'login.html')
        user_auth = authenticate(request, username=user_qs.first().username, password=password)
        if user_auth and user_auth.is_active:
            login(request, user_auth)
            if tipo_usuario == 'cliente' and hasattr(user_auth, 'perfilcliente'):
                return redirect('cliente_dashboard')
            elif tipo_usuario == 'funcionario' and hasattr(user_auth, 'perfilfuncionario'):
                return redirect('funcionario_dashboard')
            else:
                messages.error(request, 'O tipo de usuário selecionado não corresponde ao seu cadastro.')
                logout(request)
                return render(request, 'login.html')
        else:
            messages.error(request, 'Email ou senha inválidos.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')

@login_required
def cliente_dashboard(request):
    if not hasattr(request.user, 'perfilcliente'): return redirect('home')
    return render(request, 'cliente_dashboard.html', {'pagina': 'dashboard'})

@login_required
def agendar_consulta(request):
    if not hasattr(request.user, 'perfilcliente'): return redirect('home')
    if request.method == 'POST':
        horario_id = request.POST.get('horario_id')
        if horario_id:
            horario = get_object_or_404(HorarioDisponivel, id=horario_id)
            Consulta.objects.create(
                cliente=request.user.perfilcliente,
                funcionario=horario.funcionario,
                horario=horario,
                observacoes=request.POST.get('observacoes', '')
            )
            messages.success(request, 'Consulta agendada com sucesso!')
            return redirect('minhas_consultas')
        else:
            messages.error(request, 'Por favor, selecione um horário.')
    return render(request, 'cliente_dashboard.html', {'pagina': 'agendar_consulta', 'funcionarios': PerfilFuncionario.objects.all()})

@login_required
def minhas_consultas(request):
    if not hasattr(request.user, 'perfilcliente'): return redirect('home')
    consultas = Consulta.objects.filter(cliente=request.user.perfilcliente).order_by('horario__data', 'horario__hora_inicio')
    return render(request, 'cliente_dashboard.html', {'pagina': 'minhas_consultas', 'consultas': consultas, 'today': date.today()})

@login_required
def cancelar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id, cliente__usuario=request.user)
    consulta.delete()
    messages.success(request, 'Consulta cancelada com sucesso.')
    return redirect('minhas_consultas')

@login_required
def editar_perfil(request):
    user = request.user
    FormClasse, base_dashboard = (EditarPerfilClienteForm, 'cliente_dashboard.html') if hasattr(user, 'perfilcliente') else (EditarPerfilFuncionarioForm, 'funcionario_dashboard.html')
    
    if request.method == 'POST':
        # SIMPLIFICADO: Não precisa mais de request.FILES
        form = FormClasse(request.POST, instance=user)
        if form.is_valid():
            # SIMPLIFICADO: Não precisa mais passar 'files'
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('editar_perfil')
    else:
        form = FormClasse(instance=user)
        
    return render(request, base_dashboard, {'pagina': 'editar_perfil', 'form': form})


@login_required
def funcionario_dashboard(request):
    if not hasattr(request.user, 'perfilfuncionario'): return redirect('home')
    return render(request, 'funcionario_dashboard.html', {'pagina': 'dashboard'})

@login_required
def adicionar_horario(request):
    if not hasattr(request.user, 'perfilfuncionario'): return redirect('home')
    if request.method == 'POST':
        form = HorarioForm(request.POST, funcionario=request.user.perfilfuncionario)
        if form.is_valid():
            form.save()
            return redirect('adicionar_horario')
    form = HorarioForm()
    return render(request, 'funcionario_dashboard.html', {'pagina': 'adicionar_horario', 'form': form})

@login_required
def meus_horarios(request):
    if not hasattr(request.user, 'perfilfuncionario'): return redirect('home')
    horarios = HorarioDisponivel.objects.filter(funcionario=request.user.perfilfuncionario).order_by('-data', '-hora_inicio')
    return render(request, 'funcionario_dashboard.html', {'pagina': 'meus_horarios', 'horarios': horarios})
@login_required
def consultas_agendadas_funcionario(request):
    """
    Exibe todas as consultas agendadas para o funcionário logado.
    """
    if not hasattr(request.user, 'perfilfuncionario'):
        return redirect('home')

    consultas = Consulta.objects.filter(
        funcionario=request.user.perfilfuncionario
    ).order_by('horario__data', 'horario__hora_inicio')

    return render(request, 'funcionario_dashboard.html', {
        'pagina': 'consultas_agendadas',
        'consultas': consultas,
        'today': date.today() # Passamos 'today' para comparar as datas no template
    })


@login_required
def cancelar_consulta_funcionario(request, consulta_id):
    """
    Permite que um funcionário cancele uma consulta agendada com ele.
    """
    # Garante que o funcionário só pode cancelar suas próprias consultas
    consulta = get_object_or_404(
        Consulta, 
        id=consulta_id, 
        funcionario__usuario=request.user
    )
    
    if request.method == 'POST':
        # Aqui você poderia adicionar uma lógica para notificar o cliente por e-mail, se desejado.
        cliente_nome = consulta.cliente.usuario.get_full_name() or consulta.cliente.usuario.username
        consulta.delete()
        messages.success(request, f'A consulta com {cliente_nome} foi cancelada com sucesso.')
        return redirect('consultas_agendadas_funcionario')

    # Se não for POST, redireciona de volta para a lista (ou pode mostrar uma página de confirmação)
    return redirect('consultas_agendadas_funcionario')

@login_required
def excluir_horario(request, horario_id):
    horario = get_object_or_404(HorarioDisponivel, id=horario_id, funcionario__usuario=request.user)
    if horario.consulta_set.exists():
        messages.error(request, 'Não é possível excluir. Este horário já foi agendado.')
    else:
        horario.delete()
        messages.success(request, 'Horário excluído com sucesso.')
    return redirect('adicionar_horario')

@login_required
def get_horarios_disponiveis(request, funcionario_id):
    funcionario = get_object_or_404(PerfilFuncionario, id=funcionario_id)
    horarios = HorarioDisponivel.objects.filter(funcionario=funcionario, data__gte=date.today()).exclude(consulta__isnull=False).order_by('data', 'hora_inicio')
    lista_horarios = [{'id': h.id, 'data': h.data.strftime('%d/%m/%Y'), 'dia_semana': ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][h.data.weekday()], 'hora_inicio': h.hora_inicio.strftime('%H:%M')} for h in horarios]
    return JsonResponse({'horarios': lista_horarios})

@login_required
def api_meus_horarios(request):
    if not hasattr(request.user, 'perfilfuncionario'): return JsonResponse({'error': 'Acesso negado'}, status=403)
    horarios = HorarioDisponivel.objects.filter(funcionario=request.user.perfilfuncionario)
    eventos = [{'id': h.id, 'title': f'{h.hora_inicio.strftime("%H:%M")}-{h.hora_fim.strftime("%H:%M")}', 'start': f'{h.data.isoformat()}T{h.hora_inicio.isoformat()}', 'end': f'{h.data.isoformat()}T{h.hora_fim.isoformat()}', 'backgroundColor': '#dc3545' if h.consulta_set.exists() else '#0d6efd', 'borderColor': '#dc3545' if h.consulta_set.exists() else '#0d6efd'} for h in horarios]
    return JsonResponse(eventos, safe=False)

@login_required
def api_detalhes_consulta(request, horario_id):
    if not hasattr(request.user, 'perfilfuncionario'): return JsonResponse({'error': 'Acesso negado'}, status=403)
    try:
        consulta = Consulta.objects.get(horario__id=horario_id)
        return JsonResponse({'encontrado': True, 'cliente_nome': consulta.cliente.usuario.get_full_name() or consulta.cliente.usuario.username, 'cliente_telefone': consulta.cliente.telefone, 'observacoes': consulta.observacoes or "Nenhuma observação."})
    except Consulta.DoesNotExist:
        return JsonResponse({'encontrado': False})

def listar_funcionarios(request): # Esta view não parece estar sendo usada, mas a mantenho aqui.
    return render(request, 'listar_funcionarios.html', {'funcionarios': PerfilFuncionario.objects.all()})