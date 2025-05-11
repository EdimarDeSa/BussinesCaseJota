# BussinesCaseJota
Bussines case para vaga de Desenvolvedor Backend na Jota

## Indices
- [BussinesCaseJota](#bussinescasejota)
  - [Indices](#indices)
  - [Descrição doBusiness Case](#descrição-dobusiness-case)
    - [Features](#features)
    - [API stack](#api-stack)
  - [Instalação e Execução em desenvolvimento](#instalação-e-execução-em-desenvolvimento)
    - [Requisitos](#requisitos)
    - [Instalação](#instalação)
  - [Instalação e Execução em produção](#instalação-e-execução-em-produção)
  - [Melhorias e sugestões](#melhorias-e-sugestões)

## Descrição doBusiness Case
Documentação oficial: [Google Doc](https://docs.google.com/document/d/1wHMVlLk6EfZcal1_PXjIADvGhna3oeX9JL3YKgsak7s/edit?tab=t.0#heading=h.twayzqjr36gk)

### Features

| Features | Status |
| -------------------------------------------------------------------------- | :---: |
| CRUD para usuários (Admin, Editor, Leitor) | **OK** |
| Gerenciamento de Leitor por tipo de plano contratado <br> (JOTA Info, JOTA Pro) | **OK** |
| CRUD para notícias | **OK** |
| Gerenciamento de status de notícias (Rascunho/Publicada) | **OK** |
| Permitir o agendamento de publicações de notícias <br> (Data de publicação) | **OK** |
| Definir um plano de acesso (JOTA Info, JOTA Pro) | **OK** |
| Categorizar notícias dentro das verticais <br> (Poder, Tributos, Saúde, Energia e Trabalhista) | **OK** |
| Definir a relação do cliente com o plano x Vertical <br> para notícias restritas a clientes PRO | **OK** |
| Autenticação JWT | **OK**  |
| Banco de Dados (Postgres ou MySQL) | **OK** - Postgres |
| Arquitetura e Processamento Assíncrono | **OK** |
| Testes Automatizados e CI/CD | **OK** |
| Infraestrutura e Deploy | **OK** |
| Processamento assincrono de imagens | **OK** |
| Envio de emails de notificações | **OK** |
| Implementação de Swagger | **OK** |
| Implementação de GitHub Actions | Em desenvolvimento |
| Implementação de testes | **OK** |
| Implementação de Docker | Em desenvolvimento |
| Implementação de Docker Compose | Em desenvolvimento |
| --- | --- |
| **Status global** | **EM REVISÃO** |

### API stack
- Linguagem principal: 
  - Python
- Frameworks: 
  - Django
  - Django Rest Framework
- Database:
  - PostgreSQL
- Processamento e filas:
  - Celery
  - Redis
- Autenticação:
  - JWT
- Arquitetura:
  - Arquitetura orientada a eventos (Event Driven Architecture)
  - Microserviços
- CI/CD, infraestrutura e testes:
  - Docker
  - Docker Compose
  - Git
  - GiutHub
  - GitHub Actions
  - pytest
- Documentação:
  - Swagger
  - README

## Instalação e Execução em desenvolvimento

### Requisitos
- Python 3.11
- Poetry >= 2.1.2
- Docker >= 28.0.4, build b8034c0
- Docker Compose >= v2.34.0

### Instalação
- Baixar o repositório do projeto
```bash
  git clone https://github.com/EdimarDeSa/BussinesCaseJota

  cd BussinesCaseJota
```

- Iniciar o ambiente com o poetry e instalar dependências
```bash
  $(poetry env activate)

  poetry install --no-root
```

- Criar os arquivos .env em cada pasta do projeto
  - ./portal_jota/.env
    - SECRET_KEY
    - DEBUG
    - ALLOWED_HOSTS
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - POSTGRES_HOST
    - POSTGRES_PORT
    - REDIS_HOST
    - REDIS_PORT
    - REDIS_PASSWORD
    - REDIS_USER
    - RABBITMQ_DEFAULT_USER
    - RABBITMQ_DEFAULT_PASS
    - RABBITMQ_HOST
    - RABBITMQ_PORT

  - ./docker/postgres/postgres.env
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB

  - ./docker/redis/redis.env
    - REDIS_PASSWORD
    - REDIS_PORT
    - REDIS_USER

  - ./docker/rabbitmq/rabbitmq.env
    - RABBITMQ_DEFAULT_USER
    - RABBITMQ_DEFAULT_PASS

Sugestão para criação das senhas:
```python
  from django.core.management.utils import get_random_secret_key
  print(get_random_secret_key())

  from secrets import token_urlsafe
  print(token_urlsafe(64))
```

- Iniciar o ambiente com o docker-compose
```bash
  docker compose -f docker/docker-compose.yaml up -d postgres redis rabbitmq
```	
ou para docker compose < 2.0
```bash
  docker-compose -f docker/docker-compose.yaml up -d postgres redis rabbitmq
```	

- Realizar testes
```bash
  cd portal_jota

  python manage.py test
```

- Iniciar webserver
```bash
  python manage.py makemigrations && python manage.py migrate
  python manage.py runserver
```

## Instalação e Execução em produção

## Melhorias e sugestões
- Melhorias de armazenamento
  - Definir um armazenamento externo para imagens
  - Definir tamanho máximo de arquivos de imagens
  - Definir tamaho E tipo do conteúdo de notícias (Ex.: HTML, RICHTEXT, etc.)
  - Definir um armazenamento externo para conteúdo de notícias
- Retorno das notícias
  - Organizar priorizando as noitícias JOTA_PRO + data de publicação
  - Organizar priorizando as noitícias JOTA_INFO + data de publicação
  - Link para sugestão de leituras
  - Reduzir as informações reotrnadas pela listagem de notícias
  - Adicionar tabela para metadados de visualização e compartilhamento
- Acesso e planos
  - Acesso diferenciado para leitores sem cadastro (Atualmente não tem acesso a nenhuma noticia)