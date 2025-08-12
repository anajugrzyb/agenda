# 📅 Projeto Agenda
O Projeto Agenda é uma aplicação que permite aos usuários gerenciar seus contatos e compromissos de forma prática e organizada. Através da aplicação, é possível criar, editar, visualizar e excluir registros, além de buscar informações rapidamente.

##🚀 Demonstração
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

### Execute o projeto
python manage.py migrate

### Execute o servidor local
python manage.py runserver

### Acesse a aplicação
Painel Admin: http://127.0.0.1:8000/admin
Sistema Agenda: http://127.0.0.1:8000/
