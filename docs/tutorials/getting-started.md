# Primeiros Passos

## Pré-requisitos

- Python 3.10+
- Node.js 18+
- Docker (opcional)

## Instalação

### Usando pip

```bash
pip install superdev-cli
```

### Usando npm

```bash
npm install -g superdev-cli
```

## Verificar Instalação

```bash
superdev --version
superdev doctor
```

## Login

```bash
superdev login
# Digite seu email e senha
```

## Crie Seu Primeiro Projeto

```bash
superdev init meu-projeto --template fastapi
cd meu-projeto
superdev dev
```

Visite http://localhost:8000 para ver sua API funcionando.
