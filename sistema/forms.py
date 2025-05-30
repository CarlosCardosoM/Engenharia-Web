from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import PerfilCliente, PerfilFuncionario, HorarioDisponivel, Consulta

class RegistroClienteForm(forms.ModelForm):
    matricula = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirme a Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

class RegistroFuncionarioForm(forms.ModelForm):
    especialidade = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirme a Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

class HorarioForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponivel
        fields = ['data', 'hora_inicio', 'hora_fim']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fim = cleaned_data.get('hora_fim')
        
        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise forms.ValidationError("O horário de início deve ser antes do horário de fim.")
        
        # Verificar sobreposição com outros horários do mesmo funcionário
        if data and hora_inicio and hora_fim:
            funcionario = self.instance.funcionario if self.instance else None
            if funcionario is None and hasattr(self, 'funcionario'):
                funcionario = self.funcionario
                
            if funcionario:
                conflitos = HorarioDisponivel.objects.filter(
                    funcionario=funcionario,
                    data=data,
                    hora_inicio__lt=hora_fim,
                    hora_fim__gt=hora_inicio
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if conflitos.exists():
                    raise forms.ValidationError("Este horário conflita com outro horário já cadastrado.")
        
        return cleaned_data

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['funcionario', 'horario', 'observacoes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'funcionario' in self.data:
            try:
                funcionario_id = int(self.data.get('funcionario'))
                self.fields['horario'].queryset = HorarioDisponivel.objects.filter(
                    funcionario_id=funcionario_id
                ).exclude(
                    id__in=Consulta.objects.values_list('horario__id', flat=True)
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['horario'].queryset = self.instance.funcionario.horarios_disponiveis.exclude(
                id__in=Consulta.objects.values_list('horario__id', flat=True)
            )

class EditarPerfilForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
