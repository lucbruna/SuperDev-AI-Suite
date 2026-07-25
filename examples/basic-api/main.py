"""Exemplo: API REST básica com FastAPI."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SuperDev - Exemplo API Básica")

items: dict[str, dict] = {}


class Item(BaseModel):
    nome: str
    descricao: str = ""
    preco: float = 0.0


@app.get("/")
def raiz():
    return {"mensagem": "API básica do SuperDev", "versao": "1.0.0"}


@app.get("/items")
def listar_items():
    return {"items": list(items.values()), "total": len(items)}


@app.post("/items", status_code=201)
def criar_item(item: Item):
    item_id = f"item_{len(items) + 1}"
    items[item_id] = {"id": item_id, **item.model_dump()}
    return items[item_id]


@app.get("/items/{item_id}")
def obter_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return items[item_id]


@app.put("/items/{item_id}")
def atualizar_item(item_id: str, item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    items[item_id] = {"id": item_id, **item.model_dump()}
    return items[item_id]


@app.delete("/items/{item_id}")
def deletar_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    del items[item_id]
    return {"mensagem": "Item excluído"}


@app.get("/health")
def health():
    return {"status": "saudavel"}
