# school-timetable

Gerador de horários escolares em Python, baseado em práticas de engenharia AES e na literatura de automated timetabling.

## O problema
O horário escolar é **NP-hard** (redução direta da coloração de grafos). Não existe uma única classe de problema que sirva para todas as escolas. A literatura (ITC 2002/2003/2007, surveys de Burke, Schaerf, Ceschia et al., Tan et al. 2021) mostra que:

- Metaheurísticas de busca local (**Tabu Search**, **Simulated Annealing**) batem algoritmos genéticos puros.
- A função objetivo deve ser **aditiva** (soma de penalidades), nunca um produto multiplicativo de pesos gigantes.
- Um **seed parcial imutável** (~30% dos slots) reduz drasticamente o espaço de busca.
- O horário final requer **ajuste manual** por parte da escola.

## Estrutura
```
aes/              # Artefatos do sistema AES (plan, build, verify, review, learn, tickets, metrics, shadow)
src/timetable/    # Código fonte Python
tests/            # Testes unitários e de integração
data/             # Dados de exemplo e fixtures
docs/             # Documentação técnica
```

## Começar
```bash
make setup      # cria venv e instala dependências
make test       # executa testes
make lint       # executa linter
make tree       # lista ficheiros do projeto
```

## Interface de Linha de Comando (CLI)

A CLI permite gerar, validar e fazer benchmark de horários sem escrever código Python:

```bash
# Gerar um horário (Simulated Annealing, padrão)
python scripts/cli.py generate --input data/sample_school.json --output horario.json --solver sa --tempo 60

# Gerar com Tabu Search
python scripts/cli.py generate --input data/real_school.json --output horario.json --solver ts --tempo 60

# Gerar com CP-SAT (requer ortools)
python scripts/cli.py generate --input data/sample_school.json --output horario.json --solver cpsat --tempo 60

# Validar um horário contra restrições duras
python scripts/cli.py validate --input horario.json

# Executar benchmark comparativo
python scripts/cli.py benchmark --input data/real_school.json --tempo 30
```

## Estrutura
```
aes/              # Artefatos do sistema AES (plan, build, verify, review, learn, tickets, metrics, shadow)
src/timetable/    # Código fonte Python
scripts/          # Scripts utilitários (cli.py, benchmark_real.py)
tests/            # Testes unitários e de integração
data/             # Dados de exemplo e fixtures
docs/             # Documentação técnica
```

## Documentação
- `docs/literature_review.md` — papers e referências
- `docs/architecture.md` — arquitetura de software
- `docs/constraints.md` — catálogo de restrições duras e moles
- `docs/QUALITY_GATES.md` — quality gates do projeto
- `aes/kanban.md` — quadro de tickets AES
