# DARKSTUDIO — auditoria de capacidade dos provedores de imagem e vídeo

Data da auditoria: 2026-11-23  
Branch: `darkstudio/media-engine-audit`

## Resultado executivo

O contrato de identidade de personagem e o fluxo de aprovação de assets já existem, mas **não existe ainda uma ponte que transporte as imagens aprovadas até o gerador de imagem**. Os prompts do diretor visual incluem descrição textual e IDs aprovados; isso não equivale a enviar os bytes da imagem ao modelo.

A próxima integração deve ser explícita por provedor. Não se deve enviar um parâmetro genérico como `reference_image` a adaptadores que não o implementam, nem marcar uma cena como visualmente consistente apenas porque um ID foi aprovado.

## Matriz observada no código

| Componente | Capacidade verificada | O que não comprova |
|---|---|---|
| `ai_image_generator/generators/*` | Os 14 geradores de estilo usam `generators/_renderer.py` e `media/style_scenes.py` para renderização procedural em PNG. | Não executam Stable Diffusion/SDXL e não recebem imagem de referência. O nome/modelo padrão `stable_diffusion_xl` é metadado, não prova de inferência. |
| `ai_image_generator/providers/local_diffusion.py` | Adaptador AUTOMATIC1111 compatível: `txt2img` para texto e `img2img` com `init_images` em base64 para edição condicionada por imagem. | Não está ligado ao factory dos 14 geradores nem ao endpoint `/images/generate`. |
| `api/routes/generation.py` — `POST /images/generate` | Recebe prompt, estilo, largura e altura e chama `get_image_engine().generate`. | Não recebe job, personagem ou asset ID; atualmente segue o factory procedural. |
| `ComfyUIVideoProvider` | Faz upload de um arquivo de imagem para ComfyUI, injeta nome de imagem e prompts em workflow API-format configurado, e baixa saída MP4. | É um fluxo image-to-video, não um gerador de imagem de personagem. O mapeamento depende do workflow do usuário e não implementa automaticamente múltiplas referências por personagem. |
| `ImageToVideoEngine` | Anima pixels da imagem com movimentos de câmera determinísticos; opção ComfyUI executa workflow generativo configurado. | Movimento de câmera não é geração de novos quadros semanticamente consistentes. |
| `character_identity.py` + `visual_assets.py` | Valida asset no projeto, tipo/MIME, arquivo existente e aprovação humana; revalida antes do plano visual. | Não transmite imagem ao modelo e não valida identidade por pixels. |

## Evidência de código

- `generators/_renderer.py`: chama `style_scenes.scene_for_style(...)` e `render_still(...)`.
- `local_diffusion.py`: `generate_scene_image` envia JSON a `/sdapi/v1/txt2img`; `edit_image` envia `init_images` a `/sdapi/v1/img2img`.
- `image_engine.py`: chama `get_generator(generator).generate(...)`; não seleciona `local_diffusion`.
- `generation.py`: `ImageGenerateRequest` não tem campo de referência.
- `comfyui_video_provider.py`: `generate(image_path=...)` faz upload da imagem e mapeia uma entrada de imagem no workflow configurado.

## Decisão técnica para a ponte de referência

1. Resolver somente `approved_reference_asset_ids` do personagem e confirmar novamente projeto, registro, arquivo, MIME e tamanho.
2. Ler os bytes do arquivo aprovado no servidor; nunca aceitar caminho local enviado pelo cliente.
3. Fazer a ponte por capacidades declaradas pelo adaptador:
   - AUTOMATIC1111 `img2img`: suporta uma imagem inicial via `init_images`; isso é edição/condicionamento, não treinamento ou garantia de identidade.
   - ComfyUI: suporta apenas o workflow específico cujo mapeamento de entrada de imagem foi configurado e validado.
   - Geradores procedurais atuais: não suportam referência; devem responder com capacidade ausente, sem fallback que finja condicionamento.
4. Registrar no resultado: provedor, operação, IDs efetivamente transmitidos, quantidade/tamanho de bytes, estado de envio e limitações.
5. Criar testes com servidor/provider fake que capture os bytes e confirme que correspondem ao asset aprovado. Testar também asset rejeitado, removido, de outro projeto, arquivo inválido, limite de tamanho e provider sem suporte.
6. Separar claramente três estados: `reference_approved`, `reference_transmitted` e `identity_visually_reviewed`. Um estado nunca implica o seguinte.

## Limites de desempenho e qualidade

- A configuração do adaptador não prova que AUTOMATIC1111 ou ComfyUI estejam ativos.
- Uma operação `img2img` pode alterar características do personagem conforme denoising/modelo/prompt; não garante identidade idêntica entre cenas.
- Similaridade por hash perceptual detecta duplicatas aproximadas, não identidade semântica de rosto, cabelo ou roupa.
- A validação de identidade visual exige avaliação de imagem/visão apropriada e revisão humana; não está implementada nesta etapa.
- Não foi executada geração real contra AUTOMATIC1111 ou ComfyUI nesta auditoria.

## Ponte implementada nesta etapa

Foi criado o método `edit_image_bytes` no adaptador AUTOMATIC1111 compatível. Ele valida MIME e conteúdo real PNG/JPEG/WebP, limita a referência a 12 MiB, codifica os bytes em base64 e envia `init_images` ao endpoint `/sdapi/v1/img2img`.

A rota `POST /jobs/{job_id}/character-identities/{character_id}/references/{asset_id}/generate`:

- exige job concluído e sem bloqueio de render;
- aceita somente um asset que esteja aprovado e continue disponível no registro do mesmo projeto;
- lê os bytes do arquivo do servidor, sem aceitar caminho fornecido pelo cliente;
- limita o tamanho antes do envio;
- chama o adaptador AUTOMATIC1111 em thread de trabalho;
- informa `reference_transmitted`, ID do asset, bytes enviados e provedor;
- mantém `pixel_identity_verified=false`, pois img2img não garante identidade visual.

A ponte é específica ao AUTOMATIC1111. Geradores procedurais e workflows ComfyUI não são selecionados implicitamente por essa rota. Se o serviço local não estiver ativo ou falhar, a rota retorna erro de provedor em vez de simular sucesso.

## Critério de aceite da próxima implementação

A ponte só poderá ser considerada funcional quando um teste automatizado demonstrar que o provedor configurado recebeu os bytes exatos de uma referência aprovada do mesmo projeto e que nenhum byte de referências pendentes/rejeitadas/removidas foi enviado. O CI precisa passar no head que contém essa implementação.
