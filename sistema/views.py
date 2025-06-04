from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from .forms import *
from .models import *

def home(request):
    return render(request, 'home.html')

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # 👈 Importante!
            user.save()
            PerfilCliente.objects.create(
                usuario=user,
                matricula=form.cleaned_data['matricula'],
                telefone=form.cleaned_data['telefone']
            )
            return redirect('login')
    else:
        form = RegistroClienteForm()
    return render(request, 'registro_cliente.html', {'form': form})

def registro_funcionario(request):
    if request.method == 'POST':
        form = RegistroFuncionarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # 👈 Importante!
            user.save()
            PerfilFuncionario.objects.create(
                usuario=user,
                especialidade=form.cleaned_data['especialidade']
            )
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

        users = User.objects.filter(email=email)
        if not users.exists():
            messages.error(request, 'Email ou senha inválidos.')
            return render(request, 'login.html')

        user = users.first()
        user = authenticate(request, username=user.username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            # DEBUG
            print(f"Usuário: {user.username}, Tipo selecionado: {tipo_usuario}")
            try:
                print("Perfil cliente:", user.perfilcliente)
            except PerfilCliente.DoesNotExist:
                print("Não tem perfil cliente")
            try:
                print("Perfil funcionario:", user.perfilfuncionario)
            except PerfilFuncionario.DoesNotExist:
                print("Não tem perfil funcionario")

            if tipo_usuario == 'cliente':
                try:
                    _ = user.perfilcliente
                    return redirect('cliente_dashboard')
                except PerfilCliente.DoesNotExist:
                    messages.error(request, 'Tipo de usuário não corresponde ao cadastro.')
                    logout(request)
                    return render(request, 'login.html')

            elif tipo_usuario == 'funcionario':
                try:
                    _ = user.perfilfuncionario
                    return redirect('funcionario_dashboard')
                except PerfilFuncionario.DoesNotExist:
                    messages.error(request, 'Tipo de usuário não corresponde ao cadastro.')
                    logout(request)
                    return render(request, 'login.html')

            else:
                messages.error(request, 'Tipo de usuário inválido.')
                logout(request)
                return render(request, 'login.html')

        else:
            messages.error(request, 'Email ou senha inválidos.')
            return render(request, 'login.html')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def cliente_dashboard(request):
    if not hasattr(request.user, 'perfilcliente'):
        return redirect('home')
    return render(request, 'cliente_dashboard.html', {'pagina': 'dashboard'})

@login_required
def agendar_consulta(request):
    if not hasattr(request.user, 'perfilcliente'):
        return redirect('home')

    cliente = get_object_or_404(PerfilCliente, usuario=request.user)

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.cliente = cliente
            consulta.save()
            return redirect('cliente_dashboard')
    else:
        form = ConsultaForm()

    return render(request, 'cliente_dashboard.html', {
        'pagina': 'agendar_consulta',
        'form': form,
        'cliente': cliente,
    })

@login_required
def minhas_consultas(request):
    if not hasattr(request.user, 'perfilcliente'):
        return redirect('home')

    cliente = get_object_or_404(PerfilCliente, usuario=request.user)
    consultas = Consulta.objects.filter(cliente=cliente)
    return render(request, 'cliente_dashboard.html', {
        'pagina': 'minhas_consultas',
        'consultas': consultas,
    })

@login_required
def cancelar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id, cliente__usuario=request.user)
    consulta.delete()
    return redirect('minhas_consultas')

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('cliente_dashboard')
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'cliente_dashboard.html', {
        'pagina': 'editar_perfil',
        'form': form
    })

@login_required
def funcionario_dashboard(request):
    if not hasattr(request.user, 'perfilfuncionario'):
        return redirect('home')
    return render(request, 'funcionario_dashboard.html')

@login_required
def adicionar_horario(request):
    funcionario = get_object_or_404(PerfilFuncionario, usuario=request.user)

    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.funcionario = funcionario
            horario.save()
            return redirect('meus_horarios')
    else:
        form = HorarioForm()

    return render(request, 'adicionar_horario.html', {
        'form': form,
        'funcionario': funcionario
    })

@login_required
def meus_horarios(request):
    funcionario = get_object_or_404(PerfilFuncionario, usuario=request.user)
    horarios = HorarioDisponivel.objects.filter(funcionario=funcionario)
    return render(request, 'meus_horarios.html', {'horarios': horarios})

@login_required
def excluir_horario(request, horario_id):
    horario = get_object_or_404(HorarioDisponivel, id=horario_id, funcionario__usuario=request.user)
    if Consulta.objects.filter(horario=horario).exists():
        return HttpResponse('Não é possível excluir. Este horário já foi agendado.')
    horario.delete()
    return redirect('meus_horarios')

def listar_funcionarios(request):
    funcionarios = PerfilFuncionario.objects.all()
    return render(request, 'listar_funcionarios.html', {'funcionarios': funcionarios})
