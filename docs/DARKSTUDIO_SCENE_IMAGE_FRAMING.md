# DARKSTUDIO — enquadramento de imagem por cena

## Contrato de transformação

Cada cena pode armazenar `background_image_transform`:

- `scale`: zoom de 1.0 a 3.0.
- `offset_x` e `offset_y`: deslocamento normalizado de -1.0 a 1.0 na área excedente do recorte.
- Valores inválidos, infinitos, booleanos e dimensões não positivas são rejeitados.

## Renderização

O `SceneCanvas` aplica o recorte à imagem de fundo antes de desenhar personagens, formas, partículas e texto. Assim, o ajuste não desloca overlays independentes nem altera a resolução final. Os valores padrão preservam o enquadramento central cover já utilizado.

## Limitações

Esta entrega adiciona o motor de enquadramento e seus testes unitários. A API de persistência e os controles visuais do painel ainda precisam ser conectados. Clipes generativos externos já prontos não são transformados retroativamente; precisam ser recriados por um fluxo compatível. Testes adicionados, ainda não executados.
