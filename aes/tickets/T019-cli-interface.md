# Ticket T019 — Interface de Linha de Comando (CLI)

## Contexto
O projeto atualmente é uma biblioteca Python sem interface de linha de comando. Para ser usável por não-programadores (diretores, secretários escolares), é necessário uma CLI simples que permita carregar um dataset, gerar um horário e exportar o resultado.

## Objetivo
Implementar `scripts/cli.py` com:
1. `generate` — carrega um dataset JSON, executa o solver (Tabu Search ou SA), exporta o horário para JSON
2. `validate` — carrega um horário JSON e verifica restrições duras
3. `benchmark` — executa o benchmark com dados reais e reporta métricas

## Critérios de Aceitação
1. `scripts/cli.py` implementado com subcomandos generate/validate/benchmark
2. `python scripts/cli.py generate --help` funciona
3. `python scripts/cli.py generate --input data/sample_school.json --output saida.json` gera um horário válido
4. `python scripts/cli.py validate --input saida.json` verifica restrições duras
5. `make test` passa, `make lint` passa
6. CLI está documentada no README.md

## Fase atual
Plan → Build.
