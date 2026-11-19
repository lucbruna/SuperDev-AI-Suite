# DARKSTUDIO — ciclo de vida dos candidatos de imagem

## Fluxo previsto

1. Gerar uma ou mais imagens candidatas para uma cena.
2. Guardar cada resultado como `pending_approval`, sem substituir a imagem ativa.
3. Exibir candidatos no editor para comparação.
4. Permitir descartar sem alterar a cena.
5. Ao aprovar, validar o caminho dentro da pasta de imagens do DARKSTUDIO, aplicar a imagem e registrar a anterior no histórico.
6. Marcar o clipe da cena como `stale`, pois a imagem aprovada ainda precisa ser renderizada novamente.

## Serviço

`scene_visual_asset_workflow.py` fornece funções sem dependência de FastAPI:

- `stage_scene_image_candidate`: adiciona candidato pendente, com limite configurável e proteção contra IDs duplicados.
- `list_scene_image_candidates`: retorna cópias dos metadados.
- `discard_scene_image_candidate`: remove somente o candidato.
- `approve_scene_image_candidate`: valida arquivo, aplica imagem, preserva histórico e invalida o clipe correspondente.

As operações devolvem um novo registro e não modificam o objeto original recebido. O chamador deve persistir o registro atualizado no armazenamento do job.

## Segurança e consistência

- Aprovação exige job concluído e ausência de bloqueio de render.
- Arquivo candidato deve existir, ter bytes e estar dentro do diretório de imagens permitido.
- Aprovação não declara o MP4 atualizado: o clipe é marcado como obsoleto.
- O histórico registra o caminho da imagem substituída.
- O serviço não remove arquivos físicos, evitando apagar uma imagem que possa estar sendo usada em outro lugar.

## Estado de integração

O serviço e os testes estão adicionados como camada reutilizável. Os endpoints existentes ainda mantêm sua lógica própria; a próxima integração deve substituir essa duplicação pelos helpers e manter os contratos HTTP atuais. Nenhuma UI nova é declarada neste lote.
