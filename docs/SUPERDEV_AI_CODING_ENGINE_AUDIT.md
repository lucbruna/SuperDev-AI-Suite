# SuperDev AI Coding Engine — auditoria de integração

**Data:** 2026-11-24  
**Repositório:** `lucbruna/SuperDev-AI-Suite`  
**Referência analisada:** branch `darkstudio/media-engine-audit` e estrutura pública de `main`  
**Status:** auditoria estática inicial; integração funcional ainda não implementada neste documento.

## 1. Decisão arquitetural

O AI Coding IDE (`saboracaiteria/AI-Coding-IDE`) deve ser tratado como referência de produto, não como dependência. Seu repositório público contém essencialmente página de apresentação e documentação; não expõe o código Android necessário para validar ou reutilizar o compilador, o agente JEV ou os motores anunciados.

O SuperDev deve continuar sendo o ambiente principal no Windows. Android pode ser um cliente remoto futuro. Não há motivo para transportar um compilador Android on-device para o núcleo Windows do SuperDev.

## 2. Componentes já encontrados no SuperDev

| Capacidade | Evidência no repositório | Avaliação inicial |
|---|---|---|
| Editor de código | `frontend/src/components/editor/MonacoEditor.tsx` e `frontend/src/editor/MonacoEditor.tsx` | Existem duas implementações com o mesmo propósito; uma usa textarea com realce artesanal, a outra carrega Monaco por CDN. |
| Dependência Monaco | `frontend/package.json` declara `@monaco-editor/react` | A dependência está disponível, mas os componentes inspecionados não a utilizam. |
| Estado de editor | `frontend/src/stores/editorStore.ts` | Zustand já guarda abas, conteúdo, preferências de fonte, minimapa e quebra de linha. |
| Terminal visual | `frontend/src/terminal/Terminal.tsx` | A interface chama `/api/v1/runtime/execute`; requer teste de ponta a ponta e revisão de autorização. |
| Runtime de shell | `backend/runtime/shell_runtime.py` | Usa `sandbox_manager`, limites de execução e limpeza do sandbox. É o caminho preferível para execução controlada. |
| Terminal de agente | `ai/tools/terminal/terminal_executor.py` | Usa `create_subprocess_shell`; revisar permissões, diretório permitido, ambiente e isolamento antes de expor a agentes. |
| Provedor Ollama | `ai/providers/ollama/ollama_provider.py` | Integração HTTP assíncrona e listagem de modelos já existem. |
| Orquestração | `agent_orchestration/` e `ai/agents/` | Há subsistemas extensos e sobrepostos; escolher um ponto de entrada canônico antes de adicionar outro agente. |
| Workspace | `backend/workspace/`, `ai/tools/filesystem/` e `frontend/src/workspace/WorkspaceView.tsx` | Serviços de workspace existem; a visualização inspecionada ainda é um placeholder estático. |
| Compilação | `code/compilation/compiler.py` e `backend/runtime/` | Há base de compilação/runtime; mapear linguagens, execução e testes antes de criar outro motor. |
| 3D | `frontend/package.json` | Não declara Three.js; verificar se existe outro módulo 3D isolado antes de introduzir dependência. |

## 3. Riscos e lacunas que precisam ser tratados

1. **Editor duplicado:** consolidar em um componente oficial baseado em `@monaco-editor/react`; remover o carregamento de CDN e o editor simulado somente após mapear todos os imports.
2. **Sincronização de conteúdo:** o componente deve preservar o modelo do editor entre renders e sincronizar alterações externas sem recriar a instância.
3. **Workspace real:** ligar árvore de arquivos, abas e conteúdo às APIs de workspace; não manter diretórios e arquivos demonstrativos hardcoded.
4. **Execução segura:** comandos enviados pela interface devem passar pelo runtime isolado. O executor de ferramentas baseado em shell precisa de revisão específica de permissões e isolamento antes de uso autônomo.
5. **Agente canônico:** integrar o editor ao orquestrador existente com permissões explícitas, aprovações para ações destrutivas, logs e limites. Não duplicar o sistema com um agente JEV fictício.
6. **Ollama:** expor estado de conexão, modelos realmente instalados e erros explícitos; não apresentar modelos de fallback como se estivessem instalados.
7. **Build/test:** usar o pipeline já existente e validar artefatos reais; não prometer compilação em tempo fixo.

## 4. Arquitetura alvo

```text
SuperDev AI Workspace
├── Project Explorer / Workspace API
├── Monaco Editor (@monaco-editor/react)
├── Tabs + Diff + Save / Autosave
├── AI Coding Agent
│   ├── Planner / Orchestrator existente
│   ├── Contexto de arquivos e busca
│   ├── Patch preview + aprovação
│   └── Test runner / resultado
├── Terminal
│   └── backend runtime sandbox (sem shell livre por padrão)
├── Git panel
├── Build & Test panel
└── Model Gateway
    └── Ollama + provedores já suportados
```

## 5. Plano incremental

### Fase A — consolidar o que existe
- Mapear imports dos dois componentes chamados MonacoEditor.
- Padronizar em `@monaco-editor/react`.
- Ligar o editor ao `editorStore` e ao workspace real.
- Adicionar testes de montagem, mudança de conteúdo, read-only e troca de linguagem.

### Fase B — fluxo de edição assistida
- Criar contrato de API para contexto, proposta de patch e diff.
- Exigir aprovação antes de aplicar patch em arquivos.
- Registrar arquivo, hash anterior, patch aplicado e resultado dos testes.

### Fase C — execução controlada
- Usar o runtime sandbox existente.
- Aplicar limites de tempo, tamanho, diretório e ambiente.
- Bloquear comandos destrutivos e acesso fora do workspace por padrão.

### Fase D — orquestração e provedores
- Integrar ao orquestrador existente, sem criar um segundo agente paralelo.
- Ligar Ollama e provedores remotos através do gateway atual.
- Exibir disponibilidade real, custo quando aplicável e falhas do provedor.

### Fase E — Git, build e validação
- Exibir diff, branch e estado Git.
- Executar testes e builds em tarefas isoladas.
- Só marcar uma alteração como concluída quando os testes correspondentes passarem.

## 6. Critérios de aceite

- Um projeto real pode ser aberto e seus arquivos listados pela API.
- Monaco real edita e salva arquivo sem perder conteúdo durante re-render.
- Alterações da IA aparecem como diff antes de serem aplicadas.
- Execução ocorre no sandbox e retorna stdout, stderr, exit code e duração.
- Ações destrutivas exigem confirmação explícita.
- Ollama informa modelos instalados, sem falsos fallbacks.
- Testes frontend, backend e build de produção passam no CI.
- Nenhum módulo existente do DARKSTUDIO é substituído ou quebrado por esta integração.

## 7. Limites desta auditoria

Esta é uma inspeção estática do código público e dos arquivos indicados. Não foi executado o aplicativo em Windows, não foi iniciado Ollama, não foi executado comando real no sandbox e não foi feita auditoria dinâmica de segurança. Os testes do CI devem ser usados como evidência de execução, sem extrapolar o que eles cobrem.
