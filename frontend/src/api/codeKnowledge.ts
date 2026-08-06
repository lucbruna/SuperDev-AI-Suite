// Ponte de compatibilidade: o Hub IA (intelligence) importa o client do
// Knowledge Graph como `codeKnowledgeApi`; a implementação canônica vive em
// knowledgeGraph.ts e é consumida por /knowledge-graph. Este re-export mantém
// ambos os nomes funcionando sem duplicar código.
export {
  knowledgeGraphApi as codeKnowledgeApi,
  type KnowledgeScanResult,
  type KnowledgeStatus,
  type KnowledgeSnapshot,
  type KnowledgeFile,
  type KnowledgeLanguages,
  type KnowledgeEntityCounts,
} from "./knowledgeGraph";
