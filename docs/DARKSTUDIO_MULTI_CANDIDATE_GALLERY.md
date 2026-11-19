# DARKSTUDIO — galeria de alternativas por cena

## Entregue nesta etapa

- A API de candidatos mantém várias alternativas por cena, com limite de oito candidatas pendentes por cena.
- A galeria do editor consulta a listagem sanitizada de candidatos e apresenta cada alternativa separadamente, lado a lado com a imagem ativa.
- Cada alternativa pode ser aprovada ou descartada individualmente; descartar uma opção não altera a imagem ativa.
- A aprovação valida o caminho dentro da pasta de imagens do DARKSTUDIO, rejeita arquivo vazio, preserva o caminho anterior no histórico e marca somente o clipe da cena afetada como desatualizado.
- A API bloqueia aprovação e descarte durante renderização, reconstrução de clipes ou regeneração em lote.
- O editor atualiza a galeria e a lista de imagens após cada ação, sem perder as outras alternativas pendentes.

## Limites explícitos

- A pontuação exibida pela galeria é compatibilidade textual dos metadados; não é reconhecimento semântico dos pixels.
- A aprovação da imagem não inicia automaticamente geração de vídeo. Para jobs VidGrid, a cena aprovada fica marcada para reconstrução seletiva do clipe de 10 segundos; o MP4 completo ainda exige renderização final.
- A geração de imagens depende do provedor configurado no backend. Esta etapa não instala modelos nem garante que um provedor esteja disponível.

## Validação

- Testes unitários adicionados para aprovação, histórico, invalidação seletiva, caminho inseguro e bloqueio de descarte durante render.
- A execução dos testes e o build do frontend precisam ser confirmados pelo CI do repositório; não considerar a integração validada apenas pela presença dos arquivos.


## Upload manual por cena

Endpoint: `POST /api/v1/video-studio/videos/jobs/{job_id}/scenes/{scene_index}/image-upload`

- Multipart field: `file`.
- Formatos aceitos: PNG, JPEG e WebP; o servidor valida o conteúdo real e normaliza para PNG.
- Limite: 20 MB; mínimo de 64 px por lado, máximo de 7680 px por lado e 40 megapixels.
- O upload cria uma candidata `user_upload`; não substitui a imagem ativa.
- A imagem aparece na galeria e só passa a valer depois da aprovação explícita.
- A aprovação atualiza a imagem ativa, registra o histórico e marca apenas o clipe da cena como desatualizado.
- O upload não inicia renderização nem altera narração ou clipes de outras cenas.

## Instrução em lote no editor

O campo "Instrução adicional para todas as cenas selecionadas" é anexado ao prompt individual de cada cena. Assim, a composição principal e a descrição narrativa continuam específicas, enquanto uma direção comum (por exemplo, iluminação ou paleta) pode ser aplicada em uma única operação. A geração em lote continua criando candidatas para revisão, sem substituir imagens automaticamente.

## Segurança e validação

Os uploads não confiam no nome/extensão do arquivo: o servidor verifica o MIME informado e decodifica a imagem, rejeita payloads inválidos e limita tamanho/dimensões. O arquivo normalizado fica dentro do diretório de imagens do job. Testes unitários cobrem upload válido, rejeição de MIME e conteúdo inválido.
