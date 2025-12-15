from django import forms
from django.contrib.auth.models import User
from .models import Cliente, Veiculo, OrdemServico, ItemServico, Pagamento, Oficina


class ClienteForm(forms.ModelForm):
    # Campos opcionais para cadastrar veículo junto com cliente
    adicionar_veiculo = forms.BooleanField(
        required=False,
        initial=False,
        label='Cadastrar veículo do cliente',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
    veiculo_marca = forms.CharField(
        required=False,
        max_length=50,
        label='Marca',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ex: Honda'})
    )
    veiculo_modelo = forms.CharField(
        required=False,
        max_length=100,
        label='Modelo',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ex: Civic'})
    )
    veiculo_ano = forms.IntegerField(
        required=False,
        label='Ano',
        widget=forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Ex: 2020'})
    )
    veiculo_placa = forms.CharField(
        required=False,
        max_length=8,
        label='Placa',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'ABC-1234'})
    )
    veiculo_cor = forms.CharField(
        required=False,
        max_length=30,
        label='Cor',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ex: Prata'})
    )
    veiculo_km = forms.IntegerField(
        required=False,
        label='KM Atual',
        widget=forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Ex: 50000'})
    )
    
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf_cnpj', 'telefone', 'email', 'endereco', 'cidade', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nome completo'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'input', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'input', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'email@exemplo.com'}),
            'endereco': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Rua, número'}),
            'cidade': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Cidade'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        adicionar_veiculo = cleaned_data.get('adicionar_veiculo')
        
        if adicionar_veiculo:
            # Validar campos obrigatórios do veículo
            if not cleaned_data.get('veiculo_marca'):
                self.add_error('veiculo_marca', 'Marca é obrigatória ao adicionar veículo')
            if not cleaned_data.get('veiculo_modelo'):
                self.add_error('veiculo_modelo', 'Modelo é obrigatório ao adicionar veículo')
            if not cleaned_data.get('veiculo_ano'):
                self.add_error('veiculo_ano', 'Ano é obrigatório ao adicionar veículo')
            if not cleaned_data.get('veiculo_placa'):
                self.add_error('veiculo_placa', 'Placa é obrigatória ao adicionar veículo')
        
        return cleaned_data


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['cliente', 'marca', 'modelo', 'ano', 'placa', 'cor', 'km_atual']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'input'}),
            'marca': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Honda'}),
            'modelo': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Civic'}),
            'ano': forms.NumberInput(attrs={'class': 'input', 'placeholder': '2020'}),
            'placa': forms.TextInput(attrs={'class': 'input', 'placeholder': 'ABC-1234'}),
            'cor': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Prata'}),
            'km_atual': forms.NumberInput(attrs={'class': 'input', 'placeholder': '50000'}),
        }


class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = [
            'cliente', 'veiculo', 'data_entrada', 'data_previsao',
            'status', 'descricao_problema', 'observacoes',
            'valor_total', 'desconto'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'input', 'id': 'id_cliente'}),
            'veiculo': forms.Select(attrs={'class': 'input', 'id': 'id_veiculo'}),
            'data_entrada': forms.DateInput(attrs={'class': 'input', 'type': 'date'}, format='%Y-%m-%d'),
            'data_previsao': forms.DateInput(attrs={'class': 'input', 'type': 'date'}, format='%Y-%m-%d'),
            'status': forms.Select(attrs={'class': 'input'}),
            'descricao_problema': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
            'valor_total': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'desconto': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        oficina = kwargs.pop('oficina', None)
        super().__init__(*args, **kwargs)
        
        # Configurar formato de data para input type="date"
        self.fields['data_entrada'].input_formats = ['%Y-%m-%d']
        self.fields['data_previsao'].input_formats = ['%Y-%m-%d']
        
        # Filtrar clientes e veículos pela oficina
        if oficina:
            self.fields['cliente'].queryset = Cliente.objects.filter(oficina=oficina, ativo=True)
            self.fields['veiculo'].queryset = Veiculo.objects.filter(cliente__oficina=oficina)
        
        # Se estiver editando e já tiver cliente, filtrar veículos
        if self.instance and self.instance.pk and self.instance.cliente:
            self.fields['veiculo'].queryset = Veiculo.objects.filter(cliente=self.instance.cliente)


class ItemServicoForm(forms.ModelForm):
    class Meta:
        model = ItemServico
        fields = ['servico', 'quantidade', 'valor_unitario', 'observacao']
        widgets = {
            'servico': forms.Select(attrs={'class': 'input'}),
            'quantidade': forms.NumberInput(attrs={'class': 'input'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'observacao': forms.TextInput(attrs={'class': 'input'}),
        }


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['ordem', 'data_pagamento', 'valor', 'metodo', 'status', 'observacao']
        widgets = {
            'ordem': forms.Select(attrs={'class': 'input'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'valor': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'metodo': forms.Select(attrs={'class': 'input'}),
            'status': forms.Select(attrs={'class': 'input'}),
            'observacao': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
        }


class OficinaForm(forms.ModelForm):
    # Campo adicional para criar usuário proprietário
    criar_usuario = forms.BooleanField(
        required=False, 
        initial=True,
        label='Criar usuário proprietário',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
    username = forms.CharField(
        required=False,
        max_length=150,
        label='Nome de usuário',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'usuario_oficina'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Senha para acesso'})
    )
    password_confirm = forms.CharField(
        required=False,
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Repita a senha'})
    )
    
    class Meta:
        model = Oficina
        fields = [
            'nome', 'cnpj', 'telefone', 'email', 'endereco', 'cidade',
            'proprietario', 'ativo',
            'modulo_clientes', 'modulo_ordens', 'modulo_faturamento', 
            'modulo_estoque', 'modulo_relatorios'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nome da Oficina'}),
            'cnpj': forms.TextInput(attrs={'class': 'input', 'placeholder': '00.000.000/0001-00'}),
            'telefone': forms.TextInput(attrs={'class': 'input', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'contato@oficina.com'}),
            'endereco': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Rua, número'}),
            'cidade': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Cidade'}),
            'proprietario': forms.Select(attrs={'class': 'input'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'modulo_clientes': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'modulo_ordens': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'modulo_faturamento': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'modulo_estoque': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'modulo_relatorios': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar proprietario opcional quando criar novo usuário
        self.fields['proprietario'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        criar_usuario = cleaned_data.get('criar_usuario')
        proprietario = cleaned_data.get('proprietario')
        
        # Validar que ou cria novo usuário ou seleciona existente
        if not criar_usuario and not proprietario:
            self.add_error('proprietario', 'Selecione um proprietário existente ou crie um novo usuário')
        
        if criar_usuario:
            username = cleaned_data.get('username')
            password = cleaned_data.get('password')
            password_confirm = cleaned_data.get('password_confirm')
            
            if not username:
                self.add_error('username', 'Nome de usuário é obrigatório ao criar novo usuário')
            elif User.objects.filter(username=username).exists():
                self.add_error('username', 'Este nome de usuário já existe')
            
            if not password:
                self.add_error('password', 'Senha é obrigatória ao criar novo usuário')
            elif len(password) < 6:
                self.add_error('password', 'A senha deve ter no mínimo 6 caracteres')
            
            if password != password_confirm:
                self.add_error('password_confirm', 'As senhas não coincidem')
        
        return cleaned_data
