# 📅 Projeto Agenda
O Projeto Agenda é uma aplicação que permite aos usuários gerenciar seus contatos e compromissos de forma prática e organizada. Através da aplicação, é possível criar, editar, visualizar e excluir registros, além de buscar informações rapidamente.

## 🚀 Demonstração
Para executar o projeto localmente:

### Clone este repositório
git clone git@github.com:anajugrzyb/agenda.git

### Acesse a pasta do projeto
cd agenda

### Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv venv source venv/bin/activate # Linux/Mac 
venv\Scripts\activate # Windows

### Instale as dependências
pip install -r requirements.txt

### Configure as variáveis de ambiente
O arquivo `.env.example` documenta as variáveis aceitas. A aplicação lê essas
variáveis diretamente do ambiente; ela não carrega o arquivo `.env`
automaticamente.

No PowerShell, para desenvolvimento local:

```powershell
$env:DJANGO_DEBUG = "true"
$env:DJANGO_SECRET_KEY = "uma-chave-local-longa-e-aleatoria"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
```

Em produção, defina `DJANGO_DEBUG=false`, use uma chave secreta exclusiva e
informe o domínio público em `DJANGO_ALLOWED_HOSTS`. Se a aplicação estiver
atrás de um proxy reverso confiável, defina também `DJANGO_BEHIND_PROXY=true`.

### Execute o projeto
python manage.py migrate

### Execute o servidor local
python manage.py runserver

### Acesse a aplicação
Painel Admin: http://127.0.0.1:8000/admin
Sistema Agenda: http://127.0.0.1:8000/
