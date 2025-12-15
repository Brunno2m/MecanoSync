# MecanoSync 🔧

Sistema de gestão para oficinas mecânicas

## 📋 Pré-requisitos

- **Python 3.8+** instalado no sistema
- Baixe em: https://www.python.org/downloads/
- ⚠️ **IMPORTANTE**: Marcar "Add Python to PATH" durante a instalação

## 🚀 Como Rodar o Sistema

### 1. Criar Ambiente Virtual (Recomendado)

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Instalar Dependências

```powershell
pip install -r requirements.txt
```

### 3. Aplicar Migrações

```powershell
python manage.py migrate
```

### 4. Criar Superusuário (Admin)

```powershell
python manage.py createsuperuser
```

Siga as instruções para definir usuário, email e senha.

### 5. Iniciar o Servidor

```powershell
python manage.py runserver
```

### 6. Acessar o Sistema

Abra o navegador: **http://127.0.0.1:8000**

---

## 🔐 Login

**Superusuário** (administrador do sistema):
- Gerencia múltiplas oficinas
- Cria acesso para donos de oficina
- URL: http://127.0.0.1:8000/login

**Dono da Oficina**:
- Gerencia sua própria oficina
- Acesso criado pelo superusuário

---

## 📌 Funcionalidades

✅ Multi-tenant (várias oficinas no mesmo sistema)  
✅ Gestão de clientes e veículos  
✅ Ordens de serviço com status dinâmico  
✅ Faturamento e controle de pagamentos  
✅ Máscaras automáticas (CPF, CNPJ, telefone, placa)  
✅ Dashboard com estatísticas  
✅ Perfil e troca de senha  

---

## 📦 Dependências Principais

- Django 4.2.27
- Python 3.8+
- SQLite (banco padrão)

---

## 📁 Estrutura

```
MecanoSync/
├── oficina/              # App principal
├── mecanosync_project/   # Configurações
├── static/               # CSS, JS, imagens
└── manage.py             # Gerenciador Django
```

---

## 🛠️ Tecnologias

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite
- **Arquitetura**: Multi-tenant SaaS
