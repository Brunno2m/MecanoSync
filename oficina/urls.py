from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Perfil e Configurações
    path('perfil/', views.perfil, name='perfil'),
    path('alterar-senha/', views.alterar_senha, name='alterar_senha'),
    
    # Admin - Gerenciar Oficinas (apenas superusuário)
    path('gerenciar/oficinas/', views.admin_dashboard, name='admin_dashboard'),
    path('gerenciar/oficinas/nova/', views.admin_oficina_criar, name='admin_oficina_criar'),
    path('gerenciar/oficinas/<int:pk>/editar/', views.admin_oficina_editar, name='admin_oficina_editar'),
    path('gerenciar/oficinas/<int:pk>/detalhes/', views.admin_oficina_detalhes, name='admin_oficina_detalhes'),
    path('gerenciar/oficinas/<int:pk>/toggle/', views.admin_oficina_toggle, name='admin_oficina_toggle'),
    path('gerenciar/oficinas/<int:pk>/excluir/', views.admin_oficina_excluir, name='admin_oficina_excluir'),
    path('gerenciar/oficinas/<int:pk>/resetar-senha/', views.admin_resetar_senha, name='admin_resetar_senha'),
    
    # Clientes
    path('clientes/', views.clientes_lista, name='clientes_lista'),
    path('clientes/novo/', views.cliente_criar, name='cliente_criar'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('clientes/<int:pk>/deletar/', views.cliente_deletar, name='cliente_deletar'),
    
    # Ordens de Serviço
    path('ordens/', views.ordens_lista, name='ordens_lista'),
    path('ordens/nova/', views.ordem_criar, name='ordem_criar'),
    path('ordens/<int:pk>/editar/', views.ordem_editar, name='ordem_editar'),
    path('ordens/<int:pk>/', views.ordem_visualizar, name='ordem_visualizar'),
    
    # API
    path('api/veiculos-cliente/', views.get_veiculos_cliente, name='get_veiculos_cliente'),
    path('api/criar-veiculo-rapido/', views.criar_veiculo_rapido, name='criar_veiculo_rapido'),
    path('api/obter-veiculo/<int:pk>/', views.obter_veiculo, name='obter_veiculo'),
    path('api/editar-veiculo/<int:pk>/', views.editar_veiculo, name='editar_veiculo'),
    path('api/excluir-veiculo/<int:pk>/', views.excluir_veiculo, name='excluir_veiculo'),
    path('api/alterar-status-ordem/<int:pk>/', views.alterar_status_ordem, name='alterar_status_ordem'),
    path('api/alterar-status-pagamento/<int:pk>/', views.alterar_status_pagamento, name='alterar_status_pagamento'),
    path('api/alterar-metodo-pagamento/<int:pk>/', views.alterar_metodo_pagamento, name='alterar_metodo_pagamento'),
    
    # Faturamento
    path('faturamento/', views.faturamento, name='faturamento'),
    
    # Estoque
    path('estoque/', views.estoque, name='estoque'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
]
