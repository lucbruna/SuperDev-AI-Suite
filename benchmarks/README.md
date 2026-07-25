# Benchmarks do SuperDev

Scripts de benchmark para medir performance dos módulos críticos.

## Executar

```bash
# Benchmark completo
python benchmarks/run_all.py

# Benchmark específico
python benchmarks/ai_router_benchmark.py
python benchmarks/workflow_benchmark.py
python benchmarks/sandbox_benchmark.py
```

## Métricas

| Métrica | Descrição |
|---------|-----------|
| Latência | Tempo de resposta em ms |
| Throughput | Requisições por segundo |
| Uso de memória | MB utilizados |
| CPU | % de utilização |
