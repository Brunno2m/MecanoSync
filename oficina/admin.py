from django.contrib import admin
from .models import Cliente, Veiculo, Servico, OrdemServico, ItemServico, Pagamento, Oficina


@admin.register(Oficina)
class OficinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'proprietario', 'cidade', 'ativo', 'data_cadastro')
    list_filter = ('ativo', 'cidade', 'modulo_clientes', 'modulo_ordens', 'modulo_faturamento')
    search_fields = ('nome', 'cnpj', 'proprietario__username', 'cidade')
    date_hierarchy = 'data_cadastro'
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'cnpj', 'proprietario', 'telefone', 'email')
        }),
        ('Localização', {
            'fields': ('endereco', 'cidade')
        }),
        ('Controle de Acesso', {
            'fields': ('ativo', 'data_renovacao')
        }),
        ('Módulos Habilitados', {
            'fields': ('modulo_clientes', 'modulo_ordens', 'modulo_faturamento', 'modulo_estoque', 'modulo_relatorios')
        }),
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf_cnpj', 'telefone', 'email', 'cidade', 'ativo', 'data_cadastro')
    list_filter = ('ativo', 'cidade', 'data_cadastro')
    search_fields = ('nome', 'cpf_cnpj', 'telefone', 'email')
    date_hierarchy = 'data_cadastro'


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'ano', 'cliente', 'cor')
    list_filter = ('marca', 'ano')
    search_fields = ('placa', 'marca', 'modelo', 'cliente__nome')


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_padrao', 'tempo_estimado', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')


class ItemServicoInline(admin.TabularInline):
    model = ItemServico
    extra = 1


class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 1


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('numero_os', 'cliente', 'veiculo', 'status', 'data_entrada', 'data_previsao', 'valor_final')
    list_filter = ('status', 'data_entrada', 'data_previsao')
    search_fields = ('numero_os', 'cliente__nome', 'veiculo__placa')
    date_hierarchy = 'data_entrada'
    inlines = [ItemServicoInline, PagamentoInline]
    readonly_fields = ('numero_os', 'criado_em', 'atualizado_em')


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'data_pagamento', 'valor', 'metodo', 'status')
    list_filter = ('status', 'metodo', 'data_pagamento')
    search_fields = ('ordem__numero_os', 'ordem__cliente__nome')
    date_hierarchy = 'data_pagamento'
