# DARKSTUDIO — diretor visual por cena

## Objetivo

Transformar o conteúdo já escrito de cada cena em um briefing visual específico, com enquadramento variado e prompt compatível com o estúdio selecionado. O módulo não cria fatos, não reescreve a narração e não gera imagens por conta própria.

## Estúdios suportados

- `whymentary`: explicador 2D, fundo branco, contornos fortes e cores chapadas.
- `historical_documentary`: documentário histórico ilustrado, profundidade em camadas e materiais/arquitetura de época.
- `felt_clay`: feltro e clay artesanal, fibras táteis e materiais consistentes.

## Funções

- `build_scene_visual_brief(scene, scene_index, studio_id)`: retorna prompt, prompt negativo, enquadramento e status de revisão.
- `plan_scene_visuals(scenes, studio_id)`: planeja todas as cenas, alterna enquadramentos não bloqueados e aponta repetições textuais.
- `rank_visual_candidates(scene, candidates)`: ordena candidatos por sobreposição de palavras-chave nos metadados.

## Regras de direção

1. Uma cena sem narração, descrição ou prompt recebe `needs_storyboard_detail`; não é inventada.
2. Um enquadramento manual com `shot_type_locked=true` é preservado.
3. Enquadramentos automáticos alternam por índice de cena para reduzir repetição.
4. A classificação de candidatos é lexical, não uma avaliação semântica da imagem.
5. O prompt exige fidelidade ao roteiro e proíbe acrescentar fatos históricos não sustentados.

## Limites

O módulo não chama Stable Diffusion, ComfyUI, Ollama ou outro provedor. Não reconhece conteúdo visual dentro dos pixels. A integração com a geração e a interface do editor é uma etapa separada.
