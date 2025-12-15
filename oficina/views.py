from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django import forms
from datetime import datetime, timedelta
from .models import Cliente, Veiculo, OrdemServico, Servico, Pagamento, Oficina
from .forms import ClienteForm, VeiculoForm, OrdemServicoForm, PagamentoForm, OficinaForm


# Helper function para obter a oficina do usuário logado
def get_user_oficina(user):
    """Retorna a oficina do usuário logado (se não for superuser)"""
    if user.is_superuser:
        return None
    try:
        return Oficina.objects.get(proprietario=user, ativo=True)
    except Oficina.DoesNotExist:
        return None


def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        # Redirecionar para dashboard apropriado
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            # Redirecionar para dashboard apropriado
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'oficina/login.html')


def logout_view(request):
    """View de logout"""
    if request.method == 'POST' or request.method == 'GET':
        auth_logout(request)
        messages.success(request, 'Você saiu do sistema com sucesso!')
        return redirect('login')
    return redirect('dashboard')


@login_required
def perfil(request):
    """Visualizar e editar perfil do usuário"""
    # Superusuário não tem oficina
    if request.user.is_superuser:
        messages.info(request, 'Superusuários não possuem perfil de oficina.')
        return redirect('admin_dashboard')
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Você não possui uma oficina associada.')
        return redirect('logout')
    
    context = {
        'oficina': oficina,
    }
    return render(request, 'oficina/perfil.html', context)


@login_required
def alterar_senha(request):
    """Alterar senha do usuário"""
    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        # Validar senha atual
        if not request.user.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
            return redirect('alterar_senha')
        
        # Validar nova senha
        if len(nova_senha) < 6:
            messages.error(request, 'A nova senha deve ter no mínimo 6 caracteres.')
            return redirect('alterar_senha')
        
        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('alterar_senha')
        
        # Alterar senha
        request.user.set_password(nova_senha)
        request.user.save()
        
        # Fazer login novamente (necessário após alterar senha)
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Senha alterada com sucesso!')
        return redirect('perfil')
    
    return render(request, 'oficina/alterar_senha.html')


@login_required
def dashboard(request):
    """Dashboard principal com estatísticas da oficina do usuário"""
    # Verificar se é superusuário (redireciona para admin dashboard)
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    
    # Obter oficina do usuário
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Você não possui uma oficina associada. Entre em contato com o administrador.')
        return redirect('logout')
    
    hoje = timezone.now().date()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Estatísticas filtradas por oficina
    ordens_abertas = OrdemServico.objects.filter(
        oficina=oficina,
        status__in=['aguardando_aprovacao', 'em_andamento', 'aguardando_pecas']
    ).count()
    
    faturamento_mensal = Pagamento.objects.filter(
        ordem__oficina=oficina,
        data_pagamento__month=mes_atual,
        data_pagamento__year=ano_atual,
        status='pago'
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    clientes_ativos = Cliente.objects.filter(oficina=oficina, ativo=True).count()
    
    ordens_atrasadas = OrdemServico.objects.filter(
        oficina=oficina,
        data_previsao__lt=hoje,
        status__in=['aguardando_aprovacao', 'em_andamento', 'aguardando_pecas']
    ).count()
    
    # Ordens recentes da oficina
    ordens_recentes = OrdemServico.objects.filter(oficina=oficina).select_related('cliente', 'veiculo').order_by('-data_entrada')[:5]
    
    # Faturamento últimos 6 meses da oficina
    faturamento_meses = []
    for i in range(5, -1, -1):
        data = hoje - timedelta(days=30*i)
        mes = data.month
        ano = data.year
        total = Pagamento.objects.filter(
            ordem__oficina=oficina,
            data_pagamento__month=mes,
            data_pagamento__year=ano,
            status='pago'
        ).aggregate(total=Sum('valor'))['total'] or 0
        faturamento_meses.append({
            'mes': data.strftime('%b'),
            'valor': float(total)
        })
    
    context = {
        'oficina': oficina,
        'ordens_abertas': ordens_abertas,
        'faturamento_mensal': faturamento_mensal,
        'clientes_ativos': clientes_ativos,
        'ordens_atrasadas': ordens_atrasadas,
        'ordens_recentes': ordens_recentes,
        'faturamento_meses': faturamento_meses,
    }
    
    return render(request, 'oficina/dashboard.html', context)


# CLIENTES
@login_required
def clientes_lista(request):
    """Lista todos os clientes da oficina"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    busca = request.GET.get('busca', '')
    filtro = request.GET.get('filtro', 'todos')
    
    clientes = Cliente.objects.filter(oficina=oficina)
    
    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca) |
            Q(cpf_cnpj__icontains=busca) |
            Q(telefone__icontains=busca) |
            Q(email__icontains=busca)
        )
    
    if filtro == 'ativos':
        clientes = clientes.filter(ativo=True)
    elif filtro == 'inativos':
        clientes = clientes.filter(ativo=False)
    
    clientes = clientes.order_by('-data_cadastro')
    
    return render(request, 'oficina/clientes.html', {'clientes': clientes})


@login_required
def cliente_criar(request):
    """Criar novo cliente"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.oficina = oficina
            cliente.save()
            
            # Criar veículo se solicitado
            if form.cleaned_data.get('adicionar_veiculo'):
                try:
                    veiculo = Veiculo.objects.create(
                        cliente=cliente,
                        marca=form.cleaned_data['veiculo_marca'],
                        modelo=form.cleaned_data['veiculo_modelo'],
                        ano=form.cleaned_data['veiculo_ano'],
                        placa=form.cleaned_data['veiculo_placa'].upper(),
                        cor=form.cleaned_data.get('veiculo_cor', ''),
                        km_atual=form.cleaned_data.get('veiculo_km')
                    )
                    messages.success(request, f'Cliente e veículo {veiculo.placa} cadastrados com sucesso!')
                except Exception as e:
                    messages.warning(request, f'Cliente cadastrado, mas erro ao criar veículo: {str(e)}')
            else:
                messages.success(request, 'Cliente cadastrado com sucesso!')
            
            return redirect('clientes_lista')
    else:
        form = ClienteForm()
    
    return render(request, 'oficina/cliente_form.html', {'form': form, 'titulo': 'Novo Cliente'})


@login_required
def cliente_editar(request, pk):
    """Editar cliente existente"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    cliente = get_object_or_404(Cliente, pk=pk, oficina=oficina)
    veiculos = cliente.veiculos.all()
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            
            # Criar veículo adicional se solicitado
            if form.cleaned_data.get('adicionar_veiculo'):
                try:
                    veiculo = Veiculo.objects.create(
                        cliente=cliente,
                        marca=form.cleaned_data['veiculo_marca'],
                        modelo=form.cleaned_data['veiculo_modelo'],
                        ano=form.cleaned_data['veiculo_ano'],
                        placa=form.cleaned_data['veiculo_placa'].upper(),
                        cor=form.cleaned_data.get('veiculo_cor', ''),
                        km_atual=form.cleaned_data.get('veiculo_km')
                    )
                    messages.success(request, f'Cliente atualizado e veículo {veiculo.placa} adicionado com sucesso!')
                except Exception as e:
                    messages.warning(request, f'Cliente atualizado, mas erro ao adicionar veículo: {str(e)}')
            else:
                messages.success(request, 'Cliente atualizado com sucesso!')
            
            return redirect('clientes_lista')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'oficina/cliente_form.html', {
        'form': form,
        'titulo': 'Editar Cliente',
        'cliente': cliente,
        'veiculos': veiculos
    })


@login_required
def cliente_deletar(request, pk):
    """Deletar cliente"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    cliente = get_object_or_404(Cliente, pk=pk, oficina=oficina)
    cliente.delete()
    messages.success(request, 'Cliente excluído com sucesso!')
    return redirect('clientes_lista')


# ORDENS DE SERVIÇO
@login_required
def ordens_lista(request):
    """Lista todas as ordens de serviço da oficina"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    busca = request.GET.get('busca', '')
    filtro = request.GET.get('filtro', 'todas')
    
    ordens = OrdemServico.objects.filter(oficina=oficina).select_related('cliente', 'veiculo')
    
    if busca:
        ordens = ordens.filter(
            Q(numero_os__icontains=busca) |
            Q(cliente__nome__icontains=busca) |
            Q(veiculo__placa__icontains=busca)
        )
    
    if filtro != 'todas':
        ordens = ordens.filter(status=filtro)
    
    ordens = ordens.order_by('-data_entrada')
    
    return render(request, 'oficina/ordens.html', {'ordens': ordens})


@login_required
def ordem_criar(request):
    """Criar nova ordem de serviço"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST, oficina=oficina)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.oficina = oficina
            ordem.save()
            messages.success(request, f'Ordem de Serviço #{ordem.numero_os} criada com sucesso!')
            return redirect('ordens_lista')
    else:
        form = OrdemServicoForm(oficina=oficina)
    
    return render(request, 'oficina/ordem_form.html', {'form': form, 'titulo': 'Nova Ordem de Serviço'})


@login_required
def ordem_editar(request, pk):
    """Editar ordem de serviço"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    ordem = get_object_or_404(OrdemServico, pk=pk, oficina=oficina)
    
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST, instance=ordem, oficina=oficina)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ordem de Serviço atualizada com sucesso!')
            return redirect('ordens_lista')
    else:
        form = OrdemServicoForm(instance=ordem, oficina=oficina)
    
    return render(request, 'oficina/ordem_form.html', {'form': form, 'titulo': 'Editar Ordem de Serviço'})


@login_required
def ordem_visualizar(request, pk):
    """Visualizar detalhes da ordem de serviço"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    ordem = get_object_or_404(OrdemServico, pk=pk, oficina=oficina)
    return render(request, 'oficina/ordem_detalhes.html', {'ordem': ordem})


# FATURAMENTO
@login_required
def faturamento(request):
    """Página de faturamento da oficina"""
    oficina = get_user_oficina(request.user)
    if not oficina:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    pagamentos = Pagamento.objects.filter(ordem__oficina=oficina).select_related('ordem', 'ordem__cliente')
    
    if data_inicio:
        pagamentos = pagamentos.filter(data_pagamento__gte=data_inicio)
    if data_fim:
        pagamentos = pagamentos.filter(data_pagamento__lte=data_fim)
    
    # Estatísticas da oficina
    receita_total = pagamentos.filter(status='pago').aggregate(total=Sum('valor'))['total'] or 0
    ordens_finalizadas = OrdemServico.objects.filter(
        oficina=oficina, 
        status__in=['concluida', 'entregue']
    ).count()
    contas_receber = pagamentos.filter(status='pendente').aggregate(total=Sum('valor'))['total'] or 0
    ticket_medio = receita_total / ordens_finalizadas if ordens_finalizadas > 0 else 0
    
    pagamentos = pagamentos.order_by('-data_pagamento')
    
    context = {
        'pagamentos': pagamentos,
        'receita_total': receita_total,
        'ordens_finalizadas': ordens_finalizadas,
        'contas_receber': contas_receber,
        'ticket_medio': ticket_medio,
    }
    
    return render(request, 'oficina/faturamento.html', context)


# ESTOQUE
@login_required
def estoque(request):
    """Página de estoque (em desenvolvimento)"""
    return render(request, 'oficina/estoque.html')


# RELATÓRIOS
@login_required
def relatorios(request):
    """Página de relatórios (em desenvolvimento)"""
    return render(request, 'oficina/relatorios.html')


# ==================== VIEWS DO SUPERUSUÁRIO ====================

@login_required
def admin_dashboard(request):
    """Dashboard do superusuário para gerenciar todas as oficinas"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas superusuários podem acessar esta página.')
        return redirect('dashboard')
    
    # Estatísticas gerais
    total_oficinas = Oficina.objects.count()
    oficinas_ativas = Oficina.objects.filter(ativo=True).count()
    oficinas_inativas = Oficina.objects.filter(ativo=False).count()
    
    # Receita total de todas as oficinas
    receita_total = Pagamento.objects.filter(status='pago').aggregate(total=Sum('valor'))['total'] or 0
    
    # Total de ordens do mês atual
    hoje = timezone.now().date()
    total_ordens = OrdemServico.objects.filter(
        data_entrada__month=hoje.month,
        data_entrada__year=hoje.year
    ).count()
    
    # Lista de oficinas com estatísticas
    oficinas = Oficina.objects.annotate(
        total_clientes=Count('clientes'),
        total_ordens=Count('ordens'),
        faturamento_total=Sum('ordens__pagamentos__valor', filter=Q(ordens__pagamentos__status='pago'))
    ).order_by('-ativo', '-data_cadastro')
    
    context = {
        'total_oficinas': total_oficinas,
        'oficinas_ativas': oficinas_ativas,
        'oficinas_inativas': oficinas_inativas,
        'receita_total': receita_total,
        'total_ordens': total_ordens,
        'oficinas': oficinas,
    }
    
    return render(request, 'oficina/admin_dashboard.html', context)


@login_required
def admin_oficina_criar(request):
    """Criar nova oficina cliente"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = OficinaForm(request.POST)
        if form.is_valid():
            oficina = form.save(commit=False)
            
            # Criar usuário se solicitado
            if form.cleaned_data.get('criar_usuario'):
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password']
                )
                oficina.proprietario = user
            
            oficina.save()
            messages.success(request, f'Oficina {oficina.nome} criada com sucesso!')
            return redirect('admin_dashboard')
    else:
        form = OficinaForm()
    
    context = {
        'form': form,
        'title': 'Nova Oficina',
        'button_text': 'Criar Oficina'
    }
    return render(request, 'oficina/admin_oficina_form.html', context)


@login_required
def admin_oficina_editar(request, pk):
    """Editar oficina existente"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    oficina = get_object_or_404(Oficina, pk=pk)
    
    if request.method == 'POST':
        form = OficinaForm(request.POST, instance=oficina)
        # Não permitir criar novo usuário na edição
        form.fields['criar_usuario'].widget = forms.HiddenInput()
        form.fields['username'].widget = forms.HiddenInput()
        form.fields['password'].widget = forms.HiddenInput()
        form.fields['password_confirm'].widget = forms.HiddenInput()
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Oficina {oficina.nome} atualizada com sucesso!')
            return redirect('admin_dashboard')
    else:
        form = OficinaForm(instance=oficina)
        # Ocultar campos de usuário na edição
        form.fields['criar_usuario'].widget = forms.HiddenInput()
        form.fields['username'].widget = forms.HiddenInput()
        form.fields['password'].widget = forms.HiddenInput()
        form.fields['password_confirm'].widget = forms.HiddenInput()
    
    context = {
        'form': form,
        'oficina': oficina,
        'title': f'Editar Oficina: {oficina.nome}',
        'button_text': 'Salvar Alterações'
    }
    return render(request, 'oficina/admin_oficina_form.html', context)


@login_required
def admin_oficina_detalhes(request, pk):
    """Ver detalhes da oficina"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    oficina = get_object_or_404(Oficina, pk=pk)
    
    # Estatísticas da oficina
    hoje = timezone.now().date()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    total_clientes = oficina.clientes.filter(ativo=True).count()
    total_veiculos = Veiculo.objects.filter(cliente__oficina=oficina).count()
    
    # Ordens de serviço
    ordens_mes = oficina.ordens.filter(
        data_entrada__month=mes_atual,
        data_entrada__year=ano_atual
    )
    total_ordens_mes = ordens_mes.count()
    
    ordens_por_status = ordens_mes.values('status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Faturamento
    faturamento_mes = Pagamento.objects.filter(
        ordem__oficina=oficina,
        status='pago',
        data_pagamento__month=mes_atual,
        data_pagamento__year=ano_atual
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    faturamento_total = Pagamento.objects.filter(
        ordem__oficina=oficina,
        status='pago'
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Últimas ordens
    ultimas_ordens = oficina.ordens.select_related('cliente', 'veiculo').order_by('-data_entrada')[:10]
    
    # Módulos ativos
    modulos = {
        'Clientes': oficina.modulo_clientes,
        'Ordens de Serviço': oficina.modulo_ordens,
        'Faturamento': oficina.modulo_faturamento,
        'Estoque': oficina.modulo_estoque,
        'Relatórios': oficina.modulo_relatorios,
    }
    
    context = {
        'oficina': oficina,
        'total_clientes': total_clientes,
        'total_veiculos': total_veiculos,
        'total_ordens_mes': total_ordens_mes,
        'ordens_por_status': ordens_por_status,
        'faturamento_mes': faturamento_mes,
        'faturamento_total': faturamento_total,
        'ultimas_ordens': ultimas_ordens,
        'modulos': modulos,
    }
    return render(request, 'oficina/admin_oficina_detalhes.html', context)


@login_required
def admin_oficina_toggle(request, pk):
    """Ativar/Desativar oficina"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    oficina = get_object_or_404(Oficina, pk=pk)
    oficina.ativo = not oficina.ativo
    oficina.save()
    
    status = 'ativada' if oficina.ativo else 'desativada'
    messages.success(request, f'Oficina {oficina.nome} foi {status} com sucesso!')
    return redirect('admin_dashboard')


@login_required
def admin_oficina_excluir(request, pk):
    """Excluir oficina"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    oficina = get_object_or_404(Oficina, pk=pk)
    
    if request.method == 'POST':
        nome_oficina = oficina.nome
        proprietario = oficina.proprietario
        
        # Verificar se o usuário é proprietário de outras oficinas
        outras_oficinas = Oficina.objects.filter(proprietario=proprietario).exclude(pk=pk).exists()
        
        # Excluir oficina primeiro (cascade deletará clientes, ordens, etc.)
        oficina.delete()
        
        # Depois excluir usuário proprietário se não for superusuário e não tiver outras oficinas
        if proprietario and not proprietario.is_superuser and not outras_oficinas:
            proprietario.delete()
        
        messages.success(request, f'Oficina "{nome_oficina}" foi excluída com sucesso!')
        return redirect('admin_dashboard')
    
    # Contar dados relacionados
    total_clientes = oficina.clientes.count()
    total_ordens = oficina.ordens.count()
    total_veiculos = Veiculo.objects.filter(cliente__oficina=oficina).count()
    
    context = {
        'oficina': oficina,
        'total_clientes': total_clientes,
        'total_ordens': total_ordens,
        'total_veiculos': total_veiculos,
    }
    return render(request, 'oficina/admin_oficina_excluir.html', context)


@login_required
def admin_resetar_senha(request, pk):
    """Resetar senha do proprietário da oficina"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    oficina = get_object_or_404(Oficina, pk=pk)
    
    if not oficina.proprietario:
        messages.error(request, 'Esta oficina não possui um proprietário associado.')
        return redirect('admin_oficina_detalhes', pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validações
        if not new_password or not confirm_password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('admin_oficina_detalhes', pk=pk)
        
        if len(new_password) < 6:
            messages.error(request, 'A senha deve ter no mínimo 6 caracteres.')
            return redirect('admin_oficina_detalhes', pk=pk)
        
        if new_password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('admin_oficina_detalhes', pk=pk)
        
        # Resetar senha
        proprietario = oficina.proprietario
        proprietario.set_password(new_password)
        proprietario.save()
        
        messages.success(request, f'Senha do usuário "{proprietario.username}" foi resetada com sucesso!')
        return redirect('admin_oficina_detalhes', pk=pk)
    
    return redirect('admin_oficina_detalhes', pk=pk)


@login_required
def get_veiculos_cliente(request):
    """API para buscar veículos de um cliente"""
    from django.http import JsonResponse
    
    cliente_id = request.GET.get('cliente_id')
    if not cliente_id:
        return JsonResponse({'veiculos': []})
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    veiculos = Veiculo.objects.filter(
        cliente_id=cliente_id,
        cliente__oficina=oficina
    ).values('id', 'marca', 'modelo', 'ano', 'placa')
    
    return JsonResponse({'veiculos': list(veiculos)})


@login_required
def criar_veiculo_rapido(request):
    """API para criar veículo rapidamente"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        cliente_id = request.POST.get('cliente')
        cliente = get_object_or_404(Cliente, pk=cliente_id, oficina=oficina)
        
        veiculo = Veiculo.objects.create(
            cliente=cliente,
            marca=request.POST.get('marca'),
            modelo=request.POST.get('modelo'),
            ano=int(request.POST.get('ano')),
            placa=request.POST.get('placa').upper()
        )
        
        return JsonResponse({
            'success': True,
            'veiculo': {
                'id': veiculo.id,
                'marca': veiculo.marca,
                'modelo': veiculo.modelo,
                'ano': veiculo.ano,
                'placa': veiculo.placa
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def obter_veiculo(request, pk):
    """API para obter dados de um veículo"""
    from django.http import JsonResponse
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        veiculo = get_object_or_404(Veiculo, pk=pk, cliente__oficina=oficina)
        return JsonResponse({
            'success': True,
            'veiculo': {
                'id': veiculo.id,
                'marca': veiculo.marca,
                'modelo': veiculo.modelo,
                'ano': veiculo.ano,
                'placa': veiculo.placa,
                'cor': veiculo.cor or '',
                'km_atual': veiculo.km_atual
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def editar_veiculo(request, pk):
    """API para editar um veículo"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        veiculo = get_object_or_404(Veiculo, pk=pk, cliente__oficina=oficina)
        
        veiculo.marca = request.POST.get('marca')
        veiculo.modelo = request.POST.get('modelo')
        veiculo.ano = int(request.POST.get('ano'))
        veiculo.placa = request.POST.get('placa').upper()
        veiculo.cor = request.POST.get('cor', '')
        
        km = request.POST.get('km_atual')
        veiculo.km_atual = int(km) if km else None
        
        veiculo.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def excluir_veiculo(request, pk):
    """API para excluir um veículo"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        veiculo = get_object_or_404(Veiculo, pk=pk, cliente__oficina=oficina)
        veiculo.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def alterar_status_ordem(request, pk):
    """API para alterar status de uma ordem de serviço"""
    from django.http import JsonResponse
    from datetime import date
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        ordem = get_object_or_404(OrdemServico, pk=pk, oficina=oficina)
        status_anterior = ordem.status
        novo_status = request.POST.get('status')
        
        # Validar status
        status_validos = ['em_andamento', 'aguardando_pecas', 'aguardando_aprovacao', 'concluida', 'entregue', 'cancelada']
        if novo_status not in status_validos:
            return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)
        
        ordem.status = novo_status
        
        # Se mudou para concluída, registrar data de conclusão
        if novo_status == 'concluida' and status_anterior != 'concluida':
            ordem.data_conclusao = date.today()
            
            # Criar pagamento pendente se não existir
            if not ordem.pagamentos.exists() and ordem.valor_final > 0:
                Pagamento.objects.create(
                    ordem=ordem,
                    valor=ordem.valor_final,
                    metodo='dinheiro',  # Método padrão, pode ser alterado depois
                    status='pendente',
                    data_pagamento=date.today()
                )
        
        ordem.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def alterar_status_pagamento(request, pk):
    """API para alterar status de um pagamento"""
    from django.http import JsonResponse
    from datetime import date
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        pagamento = get_object_or_404(Pagamento, pk=pk, ordem__oficina=oficina)
        novo_status = request.POST.get('status')
        
        # Validar status
        status_validos = ['pendente', 'pago', 'cancelado']
        if novo_status not in status_validos:
            return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)
        
        pagamento.status = novo_status
        
        # Se marcou como pago, atualizar data de pagamento
        if novo_status == 'pago':
            pagamento.data_pagamento = date.today()
        
        pagamento.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def alterar_metodo_pagamento(request, pk):
    """API para alterar método de pagamento"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    oficina = get_user_oficina(request.user)
    if not oficina:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        pagamento = get_object_or_404(Pagamento, pk=pk, ordem__oficina=oficina)
        
        # Não permitir alterar método se já foi pago
        if pagamento.status == 'pago':
            return JsonResponse({'success': False, 'error': 'Não é possível alterar método de pagamento já pago'}, status=400)
        
        novo_metodo = request.POST.get('metodo')
        
        # Validar método
        metodos_validos = ['dinheiro', 'cartao_credito', 'cartao_debito', 'pix', 'transferencia', 'boleto']
        if novo_metodo not in metodos_validos:
            return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)
        
        pagamento.metodo = novo_metodo
        pagamento.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
