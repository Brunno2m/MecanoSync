"""
Script para criar oficina padrão e vincular dados existentes
Execute com: python manage.py shell < setup_oficina_padrao.py
"""

from django.contrib.auth.models import User
from oficina.models import Oficina, Cliente, OrdemServico

print("=== Configuração da Oficina Padrão ===\n")

# Verificar se já existe uma oficina
if Oficina.objects.exists():
    print("✓ Já existe(m) oficina(s) cadastrada(s).")
    oficinas = Oficina.objects.all()
    for of in oficinas:
        print(f"  - {of.nome} (Proprietário: {of.proprietario.username})")
else:
    print("Nenhuma oficina encontrada. Criando oficina padrão...\n")
    
    # Obter ou criar usuário proprietário
    superuser = User.objects.filter(is_superuser=True).first()
    
    if not superuser:
        print("❌ Nenhum superusuário encontrado. Crie um primeiro com 'python manage.py createsuperuser'")
    else:
        # Criar usuário proprietário (não superuser)
        proprietario, created = User.objects.get_or_create(
            username='oficina_demo',
            defaults={
                'email': 'demo@mecanosync.com',
                'first_name': 'Oficina',
                'last_name': 'Demo'
            }
        )
        
        if created:
            proprietario.set_password('demo123')
            proprietario.save()
            print(f"✓ Usuário proprietário criado: {proprietario.username}")
            print(f"  Senha: demo123")
        else:
            print(f"✓ Usuário proprietário já existe: {proprietario.username}")
        
        # Criar oficina padrão
        oficina, created = Oficina.objects.get_or_create(
            cnpj='00.000.000/0001-00',
            defaults={
                'nome': 'Oficina Mecânica Demo',
                'proprietario': proprietario,
                'telefone': '(11) 99999-9999',
                'email': 'contato@oficina.com',
                'cidade': 'São Paulo',
                'endereco': 'Rua Exemplo, 123',
                'ativo': True,
                'modulo_clientes': True,
                'modulo_ordens': True,
                'modulo_faturamento': True,
                'modulo_estoque': True,
                'modulo_relatorios': True,
            }
        )
        
        if created:
            print(f"\n✓ Oficina criada: {oficina.nome}")
            print(f"  CNPJ: {oficina.cnpj}")
            print(f"  Proprietário: {oficina.proprietario.username}")
            print(f"  Módulos: Todos ativos")
        else:
            print(f"\n✓ Oficina já existe: {oficina.nome}")

print("\n=== Vinculando Dados Existentes ===\n")

# Vincular clientes sem oficina
clientes_sem_oficina = Cliente.objects.filter(oficina__isnull=True)
if clientes_sem_oficina.exists():
    oficina_padrao = Oficina.objects.first()
    if oficina_padrao:
        count = clientes_sem_oficina.update(oficina=oficina_padrao)
        print(f"✓ {count} cliente(s) vinculado(s) à oficina {oficina_padrao.nome}")
    else:
        print("❌ Nenhuma oficina disponível para vincular clientes")
else:
    print("✓ Todos os clientes já estão vinculados a uma oficina")

# Vincular ordens sem oficina
ordens_sem_oficina = OrdemServico.objects.filter(oficina__isnull=True)
if ordens_sem_oficina.exists():
    oficina_padrao = Oficina.objects.first()
    if oficina_padrao:
        count = ordens_sem_oficina.update(oficina=oficina_padrao)
        print(f"✓ {count} ordem(ns) vinculada(s) à oficina {oficina_padrao.nome}")
    else:
        print("❌ Nenhuma oficina disponível para vincular ordens")
else:
    print("✓ Todas as ordens já estão vinculadas a uma oficina")

print("\n=== Configuração Concluída ===")
print("\n🎉 Sistema multi-tenant configurado com sucesso!")
print("\nVocê pode agora:")
print("1. Login como SUPERUSUÁRIO para gerenciar oficinas")
print("2. Login como 'oficina_demo' (senha: demo123) para acessar o dashboard da oficina")
