# Guia Rápido de Instalação - MecanoSync

## Passo 1: Instalar Python
1. Acesse: https://www.python.org/downloads/
2. Baixe a versão mais recente (3.8+)
3. **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação

## Passo 2: Abrir PowerShell no diretório do projeto
1. Abra o PowerShell
2. Navegue até o diretório onde você baixou/clonou o projeto:
```powershell
cd caminho\para\MecanoSync
```

## Passo 3: Criar ambiente virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

## Passo 4: Instalar Django e dependências
```powershell
pip install -r requirements.txt
```

## Passo 5: Configurar banco de dados
```powershell
python manage.py makemigrations
python manage.py migrate
```

## Passo 6: Criar usuário admin
```powershell
python manage.py createsuperuser
```
- Digite um nome de usuário
- Digite um email (pode deixar em branco)
- Digite e confirme a senha

## Passo 7: Executar o servidor
```powershell
python manage.py runserver
```

## Passo 8: Acessar o sistema
Abra o navegador e acesse:
- Login: http://localhost:8000/login/
- Sistema: http://localhost:8000/ (após login)
- Admin: http://localhost:8000/admin/

**IMPORTANTE**: Use o usuário e senha criados no Passo 6!

## Comandos Úteis

### Parar o servidor
Pressione `Ctrl + C` no PowerShell

### Iniciar novamente
```powershell
cd caminho\para\MecanoSync
.\venv\Scripts\Activate
python manage.py runserver
```

### Criar dados de exemplo (opcional)
Acesse o admin (http://localhost:8000/admin/) e cadastre manualmente:
1. Clientes
2. Veículos
3. Serviços
4. Ordens de Serviço
5. Pagamentos

## Problemas Comuns

### "Python não é reconhecido"
- Reinstale o Python marcando "Add to PATH"
- OU adicione manualmente às variáveis de ambiente

### "Porta 8000 em uso"
```powershell
python manage.py runserver 8080
```

### Esquecer senha do admin
```powershell
python manage.py changepassword seu_usuario
```

## Estrutura de URLs

- `/` - Dashboard
- `/clientes/` - Lista de clientes
- `/clientes/novo/` - Cadastrar cliente
- `/ordens/` - Lista de ordens
- `/ordens/nova/` - Nova ordem
- `/faturamento/` - Página de faturamento
- `/admin/` - Painel administrativo

Pronto! Seu sistema está funcionando! 🎉
