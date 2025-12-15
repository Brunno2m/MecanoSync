from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User


class Oficina(models.Model):
    """Modelo para representar cada oficina cliente do sistema (multi-tenant)"""
    nome = models.CharField(max_length=200, verbose_name='Nome da Oficina')
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name='CNPJ'
    )
    proprietario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='oficinas',
        verbose_name='Proprietário'
    )
    telefone = models.CharField(max_length=15, verbose_name='Telefone')
    email = models.EmailField(verbose_name='E-mail')
    endereco = models.CharField(max_length=300, blank=True, null=True, verbose_name='Endereço')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    
    # Controle de acesso
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    data_renovacao = models.DateField(blank=True, null=True, verbose_name='Data de Renovação')
    
    # Funcionalidades/Módulos habilitados
    modulo_clientes = models.BooleanField(default=True, verbose_name='Módulo Clientes')
    modulo_ordens = models.BooleanField(default=True, verbose_name='Módulo Ordens de Serviço')
    modulo_faturamento = models.BooleanField(default=True, verbose_name='Módulo Faturamento')
    modulo_estoque = models.BooleanField(default=False, verbose_name='Módulo Estoque')
    modulo_relatorios = models.BooleanField(default=False, verbose_name='Módulo Relatórios')
    
    class Meta:
        verbose_name = 'Oficina'
        verbose_name_plural = 'Oficinas'
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return self.nome


class Cliente(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE, related_name='clientes', verbose_name='Oficina', null=True, blank=True)
    nome = models.CharField(max_length=200, verbose_name='Nome Completo')
    cpf_cnpj = models.CharField(
        max_length=18,
        verbose_name='CPF/CNPJ'
    )
    telefone = models.CharField(
        max_length=15,
        verbose_name='Telefone'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    endereco = models.CharField(max_length=300, blank=True, null=True, verbose_name='Endereço')
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cidade')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    ultima_visita = models.DateField(blank=True, null=True, verbose_name='Última Visita')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-data_cadastro']

    def __str__(self):
        return self.nome


class Veiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='veiculos')
    marca = models.CharField(max_length=50, verbose_name='Marca')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    ano = models.IntegerField(verbose_name='Ano')
    placa = models.CharField(
        max_length=8,
        unique=True,
        verbose_name='Placa'
    )
    cor = models.CharField(max_length=30, blank=True, null=True, verbose_name='Cor')
    km_atual = models.IntegerField(blank=True, null=True, verbose_name='KM Atual')

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['marca', 'modelo']

    def __str__(self):
        return f"{self.marca} {self.modelo} {self.ano} - {self.placa}"


class Servico(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Nome do Serviço')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Padrão')
    tempo_estimado = models.IntegerField(
        help_text='Tempo em horas',
        verbose_name='Tempo Estimado (h)',
        blank=True,
        null=True
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('aguardando_aprovacao', 'Aguardando Aprovação'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando_pecas', 'Aguardando Peças'),
        ('concluida', 'Concluída'),
        ('entregue', 'Entregue'),
        ('cancelada', 'Cancelada'),
    ]

    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE, related_name='ordens', verbose_name='Oficina', null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ordens')
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name='ordens')
    servicos = models.ManyToManyField(Servico, through='ItemServico')
    
    numero_os = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Nº OS')
    data_entrada = models.DateField(default=timezone.now, verbose_name='Data de Entrada')
    data_previsao = models.DateField(verbose_name='Previsão de Entrega')
    data_conclusao = models.DateField(blank=True, null=True, verbose_name='Data de Conclusão')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aguardando',
        verbose_name='Status'
    )
    
    descricao_problema = models.TextField(verbose_name='Descrição do Problema')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Valor Total')
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Desconto')
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Valor Final')
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_entrada', '-numero_os']

    def __str__(self):
        return f"OS #{self.numero_os} - {self.cliente.nome}"

    def save(self, *args, **kwargs):
        if not self.numero_os:
            # Gerar número da OS
            last_os = OrdemServico.objects.all().order_by('-id').first()
            if last_os and last_os.numero_os:
                last_number = int(last_os.numero_os)
                self.numero_os = str(last_number + 1).zfill(4)
            else:
                self.numero_os = '1001'
        
        # Calcular valor final
        self.valor_final = self.valor_total - self.desconto
        
        super().save(*args, **kwargs)


class ItemServico(models.Model):
    ordem = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name='itens')
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    quantidade = models.IntegerField(default=1, verbose_name='Quantidade')
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Unitário')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Total')
    observacao = models.CharField(max_length=500, blank=True, null=True, verbose_name='Observação')

    class Meta:
        verbose_name = 'Item de Serviço'
        verbose_name_plural = 'Itens de Serviço'

    def __str__(self):
        return f"{self.servico.nome} - OS #{self.ordem.numero_os}"

    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)


class Pagamento(models.Model):
    METODO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência Bancária'),
        ('boleto', 'Boleto'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]

    ordem = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name='pagamentos')
    data_pagamento = models.DateField(default=timezone.now, verbose_name='Data de Pagamento')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES, verbose_name='Método de Pagamento')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    observacao = models.TextField(blank=True, null=True, verbose_name='Observação')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_pagamento']

    def __str__(self):
        return f"Pagamento OS #{self.ordem.numero_os} - R$ {self.valor}"
