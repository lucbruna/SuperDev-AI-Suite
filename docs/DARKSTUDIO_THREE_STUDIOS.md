# DARKSTUDIO — três estúdios de produção

O catálogo agora expõe três contratos visuais independentes:

| Estúdio | Direção visual | Uso principal |
|---|---|---|
| Whymentary | Explainer 2D, fundo branco, contornos tipo marcador e cores chapadas | Explicações didáticas |
| Documentário Histórico | Ilustração cinematográfica, profundidade, luz atmosférica e materiais de época | História e documentários |
| Felt & Clay | Stop motion artesanal, fibras de lã, formas arredondadas e iluminação quente | Dark Health e personagens recorrentes |

## Continuidade de personagens

Mia e Leo continuam com as identidades aprovadas e podem ser selecionados também no estúdio Felt & Clay. O catálogo reaproveita as mesmas descrições de identidade, em vez de criar versões independentes com nomes iguais.

## Catálogo de objetos

O estúdio Felt & Clay pode reutilizar os objetos didáticos existentes, mas a renderização continua sujeita às capacidades reais do SceneCanvas. A disponibilidade de um perfil não significa que todos os objetos tenham sido redesenhados em materiais de feltro.

## Contratos de API

- `GET /api/v1/video-studio/studios` lista os três perfis.
- `GET /api/v1/video-studio/studios/felt_clay` retorna o contrato visual Felt & Clay.
- `GET /api/v1/video-studio/studios/library/characters?studio_id=felt_clay` retorna Mia e Leo com o estúdio associado.
- `POST /api/v1/video-studio/videos/generate` aceita `studio_id="felt_clay"`.

A seleção do perfil configura paleta, fundo, ruído, gradação, texto e defaults de câmera. O modo de geração de imagem continua dependendo do provedor instalado/configurado; o perfil não equivale a um modelo de difusão.
