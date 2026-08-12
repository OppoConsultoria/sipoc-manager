# SIPOC Manager

Sistema web para gestão de diagramas SIPOC por empresa/cliente: cadastro de empresas e áreas,
criação de SIPOCs, dashboard com indicadores e relatório detalhado e imprimível por SIPOC.

## O que o sistema faz

- Login e criação de conta (múltiplos usuários, mesmo nível de acesso).
- Cadastro de **empresas** (clientes) e **áreas** dentro de cada empresa.
- Cadastro de **SIPOCs**, com linhas dinâmicas para Fornecedores, Entradas, Etapas do
  Processo, Saídas e Clientes.
- **Dashboard** com indicadores: total de empresas, áreas, SIPOCs, média de etapas por
  processo, SIPOCs por empresa (gráfico), últimos SIPOCs atualizados, empresas ainda sem
  SIPOC cadastrado.
- Página de **empresa** listando todas as áreas e todos os SIPOCs daquele cliente.
- **Relatório** elegante e imprimível (Ctrl+P / "Salvar como PDF" no navegador) para cada
  SIPOC, com indicadores (nº de fornecedores, entradas, etapas, saídas, clientes) e o fluxo
  do processo.

## Stack

Python + Flask, SQLAlchemy (SQLite por padrão, pronto para PostgreSQL), Flask-Login,
Flask-WTF (CSRF), Bootstrap 5 + Chart.js via CDN. Sem build step de frontend.

## Rodando localmente

Pré-requisitos: Python 3.10+.

```bash
cd sipoc_system
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # ajuste SECRET_KEY se quiser
python run.py
```

Acesse http://localhost:5000, clique em "Criar conta" para o primeiro usuário e comece a
cadastrar empresas, áreas e SIPOCs. O banco SQLite é criado automaticamente em
`instance/sipoc.db`.

## Estrutura do projeto

```
sipoc_system/
  run.py                  # ponto de entrada (flask run / gunicorn run:app)
  requirements.txt
  .env.example
  sipoc_app/
    __init__.py            # app factory, registra blueprints, cria tabelas
    config.py               # lê SECRET_KEY e DATABASE_URL do ambiente
    extensions.py            # db, login_manager, csrf
    models.py                # User, Empresa, Area, Sipoc, SipocItem
    auth.py                  # login / registro / logout
    empresas.py               # CRUD de empresas
    areas.py                   # CRUD de áreas
    sipoc.py                    # CRUD de SIPOC + relatório + API de áreas por empresa
    dashboard.py                 # indicadores
    templates/                    # HTML (Jinja2 + Bootstrap)
    static/css/style.css           # identidade visual
```

## Colocando em produção (nuvem)

O app já está pronto para deploy — ele lê `SECRET_KEY` e `DATABASE_URL` do ambiente e usa
`gunicorn` como servidor de produção (incluído no requirements.txt).

**Opção recomendada para começar sem custo: Render.com**

1. Suba este projeto para um repositório Git (GitHub/GitLab).
2. No Render, crie um **Web Service** apontando para o repositório.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn run:app`
3. Crie um banco **PostgreSQL** gratuito no Render (ou use Supabase/Neon) e copie a
   "Connection String".
4. Em "Environment" do Web Service, defina:
   - `SECRET_KEY`: uma string aleatória longa
   - `DATABASE_URL`: a connection string do Postgres (o app converte `postgres://` para
     `postgresql://` automaticamente)
5. Deploy. Na primeira execução as tabelas são criadas automaticamente.

Railway, Fly.io ou um VPS próprio (com Nginx + gunicorn) funcionam da mesma forma — o único
requisito é definir `SECRET_KEY` e `DATABASE_URL` como variáveis de ambiente.

## Limitações desta versão (MVP) e próximos passos sugeridos

- Todos os usuários têm o mesmo nível de acesso (sem perfis admin/gestor/visualizador). Se
  precisar de permissões diferenciadas no futuro, dá para adicionar um campo `role` em
  `User` e checar antes das ações de exclusão, por exemplo.
- `db.create_all()` cria tabelas automaticamente, mas não gerencia migrações. Para evoluir o
  schema em produção sem perder dados, vale adicionar `Flask-Migrate` (Alembic).
- O relatório é gerado como página HTML otimizada para impressão (o usuário salva como PDF
  pelo navegador). Se precisar de PDF gerado no servidor (para anexar em e-mail
  automaticamente, por exemplo), dá para adicionar `WeasyPrint`.
- Sem envio de e-mail (recuperação de senha, convites). Pode ser adicionado com Flask-Mail.
