# Referência da API SuperDev

URL Base: `http://localhost:8000`

## Autenticação

Todas as requisições da API requerem uma chave API ou token JWT:

```bash
curl -H "Authorization: Bearer sk-..." http://localhost:8000/api/v1/users/me
```

## Endpoints

### Autenticação
- `POST /api/v1/auth/login` - Login com email/senha
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Atualizar token

### Usuários
- `GET /api/v1/users/me` - Usuário atual
- `GET /api/v1/users` - Listar usuários
- `GET /api/v1/users/:id` - Obter usuário

### Projetos
- `GET /api/v1/projects` - Listar projetos
- `POST /api/v1/projects` - Criar projeto
- `GET /api/v1/projects/:id` - Obter projeto
- `PATCH /api/v1/projects/:id` - Atualizar projeto
- `DELETE /api/v1/projects/:id` - Excluir projeto

### Agentes
- `GET /api/v1/agents` - Listar agentes
- `GET /api/v1/agents/:id` - Obter agente
- `POST /api/v1/agents/:id/start` - Iniciar agente
- `POST /api/v1/agents/:id/stop` - Parar agente

### Workflows
- `GET /api/v1/workflows` - Listar workflows
- `POST /api/v1/workflows` - Criar workflow
- `GET /api/v1/workflows/:id` - Obter workflow
- `POST /api/v1/workflows/:id/run` - Executar workflow
- `DELETE /api/v1/workflows/:id` - Excluir workflow

### Chat
- `POST /api/v1/chat` - Enviar mensagem de chat
- `POST /api/v1/chat/embeddings` - Gerar embeddings
- `GET /api/v1/chat/conversations` - Listar conversas

### Provedores
- `GET /api/v1/providers` - Listar provedores
- `POST /api/v1/providers/:id/enable` - Habilitar provedor
- `POST /api/v1/providers/:id/disable` - Desabilitar provedor

### Plugins
- `GET /api/v1/plugins` - Listar plugins
- `POST /api/v1/plugins/:id/install` - Instalar plugin
- `DELETE /api/v1/plugins/:id` - Desinstalar plugin

## Limitação de Taxa

As requisições da API são limitadas por chave API:
- 100 requisições/minuto (plano gratuito)
- 1000 requisições/minuto (plano profissional)

Cabeçalhos de limite de taxa:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Requisição inválida |
| 401 | Não autorizado |
| 403 | Proibido |
| 404 | Não encontrado |
| 422 | Erro de validação |
| 429 | Limite de taxa excedido |
| 500 | Erro interno do servidor |
