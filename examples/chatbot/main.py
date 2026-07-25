"""Exemplo: Chatbot com IA usando SuperDev."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="SuperDev - Exemplo Chatbot")


class MensagemChat(BaseModel):
    mensagem: str
    modelo: str = "gpt-4"
    conversa_id: Optional[str] = None


class RespostaChat(BaseModel):
    resposta: str
    modelo: str
    conversa_id: str


conversas: dict[str, list[dict]] = {}


@app.post("/chat", response_model=RespostaChat)
async def chat(msg: MensagemChat):
    conversa_id = msg.conversa_id or "nova_conversa"

    if conversa_id not in conversas:
        conversas[conversa_id] = []

    conversas[conversa_id].append({"role": "usuario", "conteudo": msg.mensagem})

    # Simular resposta da IA (em produção, conectar ao AI Router)
    resposta = f"Olá! Você disse: '{msg.mensagem}'. Como posso ajudar?"

    conversas[conversa_id].append({"role": "assistente", "conteudo": resposta})

    return RespostaChat(
        resposta=resposta,
        modelo=msg.modelo,
        conversa_id=conversa_id,
    )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            dados = await websocket.receive_text()
            resposta = f"Echo: {dados}"
            await websocket.send_json({
                "resposta": resposta,
                "tipo": "mensagem",
            })
    except WebSocketDisconnect:
        pass


@app.get("/conversas/{conversa_id}")
def obter_conversa(conversa_id: str):
    if conversa_id not in conversas:
        return {"erro": "Conversa não encontrada"}
    return {"conversa_id": conversa_id, "mensagens": conversas[conversa_id]}


@app.get("/health")
def health():
    return {"status": "saudavel"}
