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


## Prévia e presets no editor

O painel mostra uma prévia CSS aproximada do enquadramento enquanto os controles são ajustados. Os presets Aberto, Plano médio, Close-up e Cinematográfico preenchem os mesmos três parâmetros de escala e deslocamento. Aplicar um preset não salva automaticamente: o usuário ainda precisa acionar **Salvar enquadramento**.

A prévia do navegador não substitui o recorte calculado pelo renderizador PIL, pois a proporção e as dimensões reais da imagem determinam a área de corte final. O backend continua sendo a referência para o resultado exportado.
