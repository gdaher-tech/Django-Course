from django.urls import path
from . import views

urlpatterns = [
    # PÁGINA INICIAL
    path('pagina-do-doador/', views.pagina_do_doador, name='pagina_do_doador'),
    path('pagina-do-receptor/', views.pagina_do_receptor, name='pagina_do_receptor'),
    path('', views.index, name='index'),

    # DOADORES
    path('doadores/importar/', views.importar_doadores, name='importar_doadores'),
    path('doadores/cadastrar/', views.cadastrar_doador, name='cadastrar_doador'),
    path('doadores/listar', views.listar_doadores, name='listar_doadores'),
    path('doadores/editar/<int:pk>/', views.editar_doador, name='editar_doador'),
    path('doadores/deletar/<int:pk>/', views.deletar_doador, name='deletar_doador'),

    # RECEPTORES
    path('receptores/importar/', views.importar_receptores, name='importar_receptores'),
    path('receptores/cadastrar/', views.cadastrar_receptor, name='cadastrar_receptor'),
    path('receptores/', views.listar_receptores, name='listar_receptores'),
    path('receptores/editar/<int:pk>/', views.editar_receptor, name='editar_receptor'),
    path('receptores/deletar/<int:pk>/', views.deletar_receptor, name='deletar_receptor'),

    # ADMINISTRADORES
    path('login/', views.login_administrador, name='login_administrador'),
    path('administradores/', views.listar_administradores, name='listar_administradores'),
    path('administradores/cadastrar/', views.cadastrar_administrador, name='cadastrar_administrador'),
    path('administradores/<int:pk>/', views.buscar_administrador, name='detalhes_administrador'),
    path('administradores/editar/<int:pk>/', views.editar_administrador, name='editar_administrador'),
    path('administradores/excluir/<int:pk>/', views.excluir_administrador, name='excluir_administrador'),

    # PAINEL ADMINSTRADOR 
    path('painel/', views.painel_admin, name='painel_admin'),

    # ORGÃOS 
    path('orgaos/', views.listar_orgaos, name='listar_orgaos'),
    path('orgaos/adicionar/', views.adicionar_orgao, name='adicionar_orgao'),
    path('orgaos/editar/<int:pk>/', views.editar_orgao, name='editar_orgao'),
    path('orgaos/excluir/<int:pk>/', views.excluir_orgao, name='excluir_orgao'),

    # CENTROS DE DISTRIBUIÇÃO 
    path('centros/', views.listar_centros, name='listar_centros'),
    path('centros/editar/<int:pk>/', views.editar_centro, name='editar_centro'),

    # LOGOUT 
    path('logout/', views.logout_administrador, name='logout_administrador'),
]
