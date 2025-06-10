
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro_cliente/', views.registro_cliente, name='registro_cliente'),
    path('registro_funcionario/', views.registro_funcionario, name='registro_funcionario'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cliente/', views.cliente_dashboard, name='cliente_dashboard'),
    path('funcionario/', views.funcionario_dashboard, name='funcionario_dashboard'),
    path('adicionar_horario/', views.adicionar_horario, name='adicionar_horario'),
    path('meus_horarios/', views.meus_horarios, name='meus_horarios'),
    path('excluir_horario/<int:horario_id>/', views.excluir_horario, name='excluir_horario'),
    path('agendar_consulta/', views.agendar_consulta, name='agendar_consulta'),
    path('minhas_consultas/', views.minhas_consultas, name='minhas_consultas'),
    path('cancelar_consulta/<int:consulta_id>/', views.cancelar_consulta, name='cancelar_consulta'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('funcionarios/', views.listar_funcionarios, name='listar_funcionarios'),
    path('api/horarios/<int:funcionario_id>/', views.get_horarios_disponiveis, name='get_horarios_disponiveis'),
    path('api/meus-horarios/', views.api_meus_horarios, name='api_meus_horarios'),
    path('funcionario/consultas/', views.consultas_agendadas_funcionario, name='consultas_agendadas_funcionario'),
    path('consulta/cancelar_pelo_funcionario/<int:consulta_id>/', views.cancelar_consulta_funcionario, name='cancelar_consulta_funcionario'),
    
]