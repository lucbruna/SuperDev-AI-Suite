# DARKSTUDIO — critérios de aceite para direção visual e ativos de cena

- [ ] Toda cena com conteúdo textual recebe um briefing visual específico.
- [ ] Cena sem conteúdo suficiente exige revisão manual.
- [ ] Enquadramento manual bloqueado permanece intacto.
- [ ] Enquadramentos automáticos variam ao longo do storyboard.
- [ ] Repetições textuais são sinalizadas sem afirmar duplicidade visual por pixels.
- [ ] Candidatos pendentes não alteram a imagem ativa.
- [ ] Descartar candidato não altera imagem ativa nem clipe existente.
- [ ] Aprovar candidato valida caminho, existência e tamanho do arquivo.
- [ ] Aprovar candidato registra a imagem substituída no histórico.
- [ ] Aprovar candidato marca somente o clipe da cena afetada como obsoleto.
- [ ] A persistência do novo registro é executada pelo endpoint chamador.
- [ ] Testes unitários passam no CI antes de considerar o lote validado.

## Fora do escopo deste lote

- Geração real de imagens.
- Reconhecimento de objetos/personagens por visão computacional.
- Persistência SQLite direta no serviço.
- Integração dos endpoints FastAPI.
- Componente de interface para galeria, comparação e aprovação.
- Renderização automática do clipe após aprovação.
