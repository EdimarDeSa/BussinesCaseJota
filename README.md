# BussinesCaseJota
Bussines case para vaga de Desenvolvedor Backend na Jota

## Indices
- [BussinesCaseJota](#bussinescasejota)
  - [Indices](#indices)
  - [Descrição doBusiness Case](#descrição-dobusiness-case)
    - [Features](#features)
    - [API stack](#api-stack)
  - [Instalação e Execução em desenvolvimento](#instalação-e-execução-em-desenvolvimento)
  - [Instalação e Execução em produção](#instalação-e-execução-em-produção)
  - [Melhorias e sugestões](#melhorias-e-sugestões)

## Descrição doBusiness Case
Documentação oficial: [Google Doc](https://docs.google.com/document/d/1wHMVlLk6EfZcal1_PXjIADvGhna3oeX9JL3YKgsak7s/edit?tab=t.0#heading=h.twayzqjr36gk)

### Features
- CRUD para usuários (Admin, Editor, Leitor)
- Gerenciamento de Leitor por tipo de plano contratado (JOTA Info, JOTA Pro)
- CRUD para notícias
  - Campos obrigatórios:
    - Título
    - Subtítulo
    - Imagem (upload)
    - Conteúdo
    - Data de publicação
    - Autor
    - Status
  - Permitir o agendamento de publicações de notícias (Data de publicação)
  - Gerenciamento de status de notícias (Rascunho/Publicada)
    - Rascunho: Notícia salva por um editor, mas ainda não publicada.
    - Publicada: Notícia disponível para leitura.
  - Definir se uma notícia será acessível a todos os leitores ou restrita a clientes PRO (É notícia JOTA Pro?)
  - Categorizar notícias dentro das verticais (Poder, Tributos, Saúde, Energia e Trabalhista)
  - Definir a relação do cliente com o plano x Vertical para notícias restritas a clientes PRO
- Autenticação e Perfis de Usuários
  - Implementar autenticação baseada em JWT para controle de acesso
  - End points:
    - Login
    - Logout
    - Refresh token
  - Perfis de Usuários:
    - Admin: Acesso total (criação, edição, exclusão e gerenciamento de usuários).
    - Editor: Pode criar, editar e excluir apenas suas próprias notícias.
    - Leitor: Pode visualizar apenas notícias publicadas, conforme o plano contratado.
  - Permissão de acordo com plano contratado
    - JOTA Info: Pode acessar notícias abertas para todos os usuários.
    - JOTA PRO: Tem acesso a conteúdos exclusivos de acordo com as verticais disponíveis no plano.
    - Cada notícia tem uma  ou mais verticais associadas e pode ou não ser acessível a todos os leitores.
- Banco de Dados
  - Utilização de PostgreSQL ou MySQL.
  - Conhecimento básico em bancos NoSQL não obrigatório (Dieferencial).
- Arquitetura e Processamento Assíncrono
  - Implementar fila de processamento para tarefas demoradas (ex.: envio de e-mails de notificação).
  - Utilizar arquitetura orientada a eventos para escalabilidade e desacoplamento dos serviços.
  - Conhecimento em microsserviços não obrigatório (Diferencial).
- Testes Automatizados e CI/CD
  - Implementar testes unitários e de integração (pytest ou unittest) para garantir confiabilidade.
  - Configurar um pipeline CI/CD com GitHub Actions para execução automática dos testes e deploy.
  - Experiência com metodologias ágeis e integração/entrega contínua não obrigatória (Diferencial).
- Infraestrutura e Deploy
  - Criar Dockerfile e Docker Compose para facilitar o deploy.

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

## Instalação e Execução em produção

## Melhorias e sugestões
- Melhorias de armazenamento
  - Definir um armazenamento externo para imagens
  - Definir tamanho máximo de arquivos de imagens
  - Definir tamaho E tipo do conteúdo de notícias (Ex.: HTML, RICHTEXT, etc.)
  - Definir um armazenamento externo para conteúdo de notícias