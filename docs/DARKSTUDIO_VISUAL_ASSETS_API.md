# DARKSTUDIO — API de planejamento visual e candidatos

A API é registrada sob o prefixo `/visual-assets`.

## Rotas

### `POST /visual-assets/jobs/{job_id}/visual-plan`

Corpo opcional:

```json
{
  "studio_id": "historical_documentary",
  "apply_suggestions": false
}
```

- `apply_suggestions=false`: calcula uma prévia sem persistir alterações.
- `apply_suggestions=true`: salva o briefing em `scene_visual_plan` e em cada cena, além de preencher `visual_prompt_suggestion` somente quando o prompt atual está vazio ou genérico.
- Não troca imagens, não chama provedor de geração e não inicia render.
- Exige job concluído. A aplicação é bloqueada durante operações de render.

### `GET /visual-assets/jobs/{job_id}/visual-plan`

Retorna o último plano persistido ou `exists=false`.

### `GET /visual-assets/jobs/{job_id}/scenes/{scene_index}/image-candidates`

Retorna candidatos da cena ordenados por correspondência lexical dos metadados. A resposta não expõe caminhos absolutos locais. O score não representa análise semântica nem qualidade da imagem.

## Integração do painel

O painel pode usar o POST para gerar prévia, apresentar briefings por cena e solicitar aplicação explícita. Em seguida, usa o GET de candidatos para preencher a galeria de comparação. A aprovação e o descarte continuam usando os endpoints de candidato já existentes em `/videos/jobs/...`.

## Limites deste incremento

- Nenhum componente de interface foi adicionado neste lote.
- A geração de candidatos continua usando os provedores já existentes.
- A aplicação de briefings não gera imagem automaticamente.
- Os testes unitários foram criados, mas ainda precisam ser executados no ambiente do projeto.
