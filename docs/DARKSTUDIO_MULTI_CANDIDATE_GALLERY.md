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
