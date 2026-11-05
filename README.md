# Agenda de Contatos

[![CI](https://github.com/anajugrzyb/agenda/actions/workflows/ci.yml/badge.svg)](https://github.com/anajugrzyb/agenda/actions/workflows/ci.yml)

Aplicação web para gerenciamento privado de contatos, desenvolvida com Django.
Cada usuário possui sua própria agenda e pode cadastrar, pesquisar, editar e
excluir contatos sem expor dados para outras contas.

## Funcionalidades

- Cadastro, login, atualização de perfil e alteração de senha.
- Agenda isolada por usuário.
- Criação, visualização, edição e exclusão de contatos.
- Busca por nome, sobrenome, telefone ou e-mail.
- Organização por categorias privadas de cada usuário.
- Upload protegido de foto do contato.
- Paginação da listagem.
- Mensagens de confirmação e validação de formulários.
- Administração de contatos e categorias pelo Django Admin.

## Segurança e privacidade

- Todas as páginas da agenda exigem autenticação.
- Contatos e categorias possuem proprietário obrigatório no banco de dados.
- Consultas, edições e exclusões são limitadas ao proprietário do contato.
- Categorias de outras contas não são exibidas nem aceitas pelos formulários.
- Fotos são entregues por uma rota autenticada, em vez de uma URL pública de
  mídia.
- Logout e exclusão definitiva utilizam `POST` com proteção CSRF.
- Segredos e configurações de produção são recebidos por variáveis de ambiente.
- HTTPS, cookies seguros e HSTS são ativados automaticamente quando
  `DJANGO_DEBUG=false`.

## Tecnologias

- Python 3.13
- Django 5.2
- SQLite para desenvolvimento local
- HTML5 e CSS3
- Pillow para processamento de imagens
- Django TestCase para testes automatizados

## Estrutura do projeto

```text
agenda/
├── base_static/            # CSS da aplicação
├── base_templates/         # Layout e componentes compartilhados
├── contact/
│   ├── migrations/         # Histórico do banco de dados
│   ├── templates/          # Páginas da agenda
│   ├── views/              # Contatos, formulários e autenticação
│   ├── forms.py            # Formulários e validações
│   ├── models.py           # Contatos e categorias
│   ├── tests.py            # Testes de segurança e fluxos principais
│   └── urls.py             # Rotas da aplicação
├── project/                # Configurações e entrada do Django
├── .env.example            # Referência das variáveis de ambiente
├── manage.py
└── requirements.txt
```

## Executando localmente

### 1. Clone o repositório

```bash
git clone https://github.com/anajugrzyb/agenda.git
cd agenda
```

### 2. Crie e ative um ambiente virtual

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configure o ambiente

O arquivo `.env.example` documenta as variáveis disponíveis. A aplicação lê as
variáveis diretamente do ambiente e não carrega arquivos `.env`
automaticamente.

No PowerShell:

```powershell
$env:DJANGO_DEBUG = "true"
$env:DJANGO_SECRET_KEY = "uma-chave-local-longa-e-aleatoria"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
```

No Bash:

```bash
export DJANGO_DEBUG=true
export DJANGO_SECRET_KEY="uma-chave-local-longa-e-aleatoria"
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
```

### 5. Prepare o banco e inicie a aplicação

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse:

- Aplicação: <http://127.0.0.1:8000/>
- Administração: <http://127.0.0.1:8000/admin/>

## Variáveis de ambiente

| Variável | Obrigatória em produção | Descrição |
| --- | --- | --- |
| `DJANGO_DEBUG` | Sim | Use `false` em produção. |
| `DJANGO_SECRET_KEY` | Sim | Chave longa, aleatória e exclusiva do ambiente. |
| `DJANGO_ALLOWED_HOSTS` | Sim | Hosts separados por vírgula. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Conforme o deploy | Origens HTTPS separadas por vírgula. |
| `DJANGO_BEHIND_PROXY` | Não | Use `true` apenas atrás de um proxy confiável. |
| `DJANGO_SECURE_HSTS_SECONDS` | Não | Duração do HSTS; o padrão de produção é 3600 segundos. |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | Não | Inclui subdomínios na política HSTS. |
| `DJANGO_SECURE_HSTS_PRELOAD` | Não | Habilita a diretiva de preload do HSTS. |

Ative HSTS para subdomínios ou preload somente quando todos os domínios
envolvidos estiverem preparados para HTTPS permanente.

## Testes

O projeto possui 23 testes para isolamento entre usuários, autenticação, fotos
protegidas, CRUD de contatos, atualização de perfil, alteração de senha, logout
e exclusão. A cobertura atual é de 97,4%, com limite mínimo de 95% na CI.

```bash
python -m pip install -r requirements-dev.txt
python -m coverage run manage.py test
python -m coverage report
python -m coverage html
python manage.py check
```

Para revisar a configuração antes de um deploy:

```bash
python manage.py check --deploy
```

O workflow de integração contínua executa automaticamente os checks, verifica
se existem migrations ausentes, exige pelo menos 95% de cobertura e publica o
relatório HTML como artefato em cada push ou pull request direcionado à branch
`main`.

## Próximas melhorias

- Publicar uma demonstração com PostgreSQL.
- Adicionar importação e exportação de contatos em CSV.
- Incluir filtros por categoria e ordenação da listagem.

## Autora

Desenvolvido por [Ana Júlia Grzyb](https://github.com/anajugrzyb).
