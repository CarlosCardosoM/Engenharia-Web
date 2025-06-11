from django import forms
from django.contrib.auth.models import User
from .models import PerfilCliente, PerfilFuncionario, HorarioDisponivel, Consulta
from .models import HorarioDisponivel
from datetime import date

class RegistroClienteForm(forms.ModelForm):
    username = forms.CharField(label="Nome de Usuário", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    matricula = forms.CharField(label="Matrícula", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefone = forms.CharField(label="Telefone", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Senha', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirme a Senha', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")
        return password2

class RegistroFuncionarioForm(forms.ModelForm):
    username = forms.CharField(label='Usuário', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='E-mail', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    especialidade = forms.CharField(label='Especialidade', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Senha', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirme a Senha', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class HorarioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # 1. Primeiro, pegamos nosso argumento personalizado 'funcionario' e o removemos dos kwargs.
        self.funcionario = kwargs.pop('funcionario', None)

        # 2. AGORA, chamamos o __init__ da classe pai, que receberá apenas os argumentos que conhece.
        super().__init__(*args, **kwargs)

        # 3. Depois, podemos fazer outras modificações, como definir a data mínima.
        self.fields['data'].widget.attrs['min'] = date.today().isoformat()

    # O resto da sua classe continua igual
    class Meta:
        model = HorarioDisponivel
        fields = ['data', 'hora_inicio', 'hora_fim']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("data")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fim = cleaned_data.get("hora_fim")

        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise forms.ValidationError("O horário de início deve ser antes do horário de fim.")
        
        if self.funcionario and data and hora_inicio and hora_fim:
            conflitos = HorarioDisponivel.objects.filter(
                funcionario=self.funcionario,
                data=data,
                hora_inicio__lt=hora_fim,
                hora_fim__gt=hora_inicio
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if conflitos.exists():
                raise forms.ValidationError("Este horário conflita com outro já cadastrado.")
        
        return cleaned_data

class EditarPerfilClienteForm(forms.Form):
    username = forms.CharField(label="Nome de Usuário", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)
    matricula = forms.CharField(label="Matrícula", max_length=20, required=True)
    telefone = forms.CharField(label="Telefone", max_length=15, required=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['username'].initial = self.instance.username
            self.fields['email'].initial = self.instance.email
            if hasattr(self.instance, 'perfilcliente'):
                self.fields['matricula'].initial = self.instance.perfilcliente.matricula
                self.fields['telefone'].initial = self.instance.perfilcliente.telefone
    
    def save(self): # Método save simplificado
        user = self.instance
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.save()
        if hasattr(user, 'perfilcliente'):
            perfil = user.perfilcliente
            perfil.matricula = self.cleaned_data['matricula']
            perfil.telefone = self.cleaned_data['telefone']
            perfil.save()
        return user

class EditarPerfilFuncionarioForm(forms.Form):
    username = forms.CharField(label="Nome de Usuário", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)
    especialidade = forms.CharField(label="Especialidade", max_length=100, required=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['username'].initial = self.instance.username
            self.fields['email'].initial = self.instance.email
            if hasattr(self.instance, 'perfilfuncionario'):
                self.fields['especialidade'].initial = self.instance.perfilfuncionario.especialidade
    
    def save(self): # Método save simplificado
        user = self.instance
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.save()
        if hasattr(user, 'perfilfuncionario'):
            perfil = user.perfilfuncionario
            perfil.especialidade = self.cleaned_data['especialidade']
            perfil.save()
        return user