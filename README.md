# MecanoSync - Sistema de Gestão para Oficinas Mecânicas

Sistema completo de gestão para oficinas mecânicas desenvolvido em Django, com interface moderna e responsiva.

## 🚀 Funcionalidades

- **Dashboard Interativo**: Visão geral com indicadores de desempenho
- **Gestão de Clientes**: Cadastro completo de clientes e veículos
- **Ordens de Serviço**: Controle total das ordens com status e acompanhamento
- **Faturamento**: Gestão financeira com pagamentos e relatórios
- **Interface Moderna**: Design responsivo e intuitivo
- **Gráficos Visuais**: Visualização de faturamento dos últimos 6 meses

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

### 1. Instalar Python

Baixe e instale o Python em: https://www.python.org/downloads/
**IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação

### 2. Clonar/Baixar o Projeto

Clone ou baixe este repositório para o seu computador e navegue até o diretório:

```bash
cd caminho/para/MecanoSync
```

### 3. Criar Ambiente Virtual (Recomendado)

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 4. Instalar Dependências

```powershell
pip install -r requirements.txt
```

### 5. Configurar Banco de Dados

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. Criar Superusuário (Admin)

```powershell
python manage.py createsuperuser
```

Siga as instruções e crie seu usuário administrativo.
**Este usuário será usado para fazer login no sistema!**

### 7. Executar o Servidor

```powershell
python manage.py runserver
```

### 8. Acessar o Sistema

Abra seu navegador e acesse:
- **Login**: http://localhost:8000/login/
- **Sistema Principal**: http://localhost:8000/ (requer login)
- **Painel Admin**: http://localhost:8000/admin/

**Use o usuário e senha criados no passo 6 para fazer login!**

## 📁 Estrutura do Projeto

```
MecanoSync/
│
├── mecanosync_project/      # Configurações do projeto
│   ├── settings.py          # Configurações principais
│   ├── urls.py              # URLs principais
│   └── wsgi.py              # Configuração WSGI
│
├── oficina/                 # Aplicação principal
│   ├── models.py            # Modelos de dados
│   ├── views.py             # Lógica de visualização
│   ├── forms.py             # Formulários
│   ├── admin.py             # Configuração do admin
│   ├── urls.py              # URLs da aplicação
│   └── templates/           # Templates HTML
│       └── oficina/
│           ├── base.html
│           ├── dashboard.html
│           ├── clientes.html
│           ├── ordens.html
│           └── ...
│
├── static/                  # Arquivos estáticos
│   ├── css/
│   │   └── styles.css       # Estilos CSS
│   ├── js/
│   │   └── script.js        # JavaScript
│   └── img/
│       └── logo1.png        # Logo da oficina
│
├── manage.py                # Gerenciador Django
└── requirements.txt         # Dependências
```

## 💾 Modelos de Dados

### Cliente
- Nome, CPF/CNPJ, Telefone, Email
- Endereço, Cidade
- Data de cadastro, Última visita

### Veículo
- Marca, Modelo, Ano, Placa
- Cor, KM Atual
- Relacionado ao Cliente

### Ordem de Serviço
- Número da OS, Status
- Cliente e Veículo
- Descrição do problema
- Datas (entrada, previsão, conclusão)
- Valores (total, desconto, final)

### Serviço
- Nome, Descrição
- Valor padrão
- Tempo estimado

### Pagamento
- Método de pagamento
- Valor, Status
- Data e observações

## 🎨 Interface

- Design moderno com gradientes e animações
- Totalmente responsivo (mobile, tablet, desktop)
- Gráficos interativos em CSS puro
- Sistema de notificações e mensagens
- Filtros e busca avançada

## 🔐 Segurança

- Sistema de autenticação Django
- Proteção CSRF
- Validação de formulários
- Proteção contra SQL Injection

## 📊 Funcionalidades em Desenvolvimento

- Módulo de Estoque
- Relatórios Avançados
- Integração com APIs de pagamento
- Notificações por email/SMS
- Sistema de agendamento

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Icons**: Font Awesome
- **Patterns**: MTV (Model-Template-View)

## 📝 Uso do Sistema

### Dashboard
Visualize estatísticas em tempo real:
- Ordens abertas
- Faturamento mensal
- Clientes ativos
- Ordens atrasadas

### Cadastro de Clientes
1. Acesse "Clientes" no menu
2. Clique em "Novo Cliente"
3. Preencha os dados
4. Salve

### Criar Ordem de Serviço
1. Acesse "Ordens de Serviço"
2. Clique em "Nova Ordem"
3. Selecione cliente e veículo
4. Descreva o serviço
5. Defina valores e prazos

### Gerenciar Pagamentos
1. Acesse "Faturamento"
2. Visualize transações
3. Filtre por período
4. Acompanhe contas a receber

## 🐛 Solução de Problemas

### Erro ao executar manage.py
```powershell
# Certifique-se de que está no diretório correto
cd c:\Users\brunn_mexf451\Documents\MecanoSync

# Ative o ambiente virtual
.\venv\Scripts\Activate
```

### Erro de porta em uso
```powershell
# Execute em outra porta
python manage.py runserver 8080
```

### Erro de migrations
```powershell
# Delete o db.sqlite3 e recrie
python manage.py makemigrations
python manage.py migrate
```

## 📧 Suporte

Para dúvidas ou problemas, consulte a documentação do Django: https://docs.djangoproject.com/

## 📄 Licença

Este projeto é de uso livre para fins educacionais e comerciais.

## 👨‍💻 Desenvolvimento

Sistema desenvolvido com base em requisitos de gestão de oficinas mecânicas, priorizando:
- Usabilidade
- Performance
- Segurança
- Escalabilidade

---

**MecanoSync** - Gestão Inteligente para sua Oficina 🔧
