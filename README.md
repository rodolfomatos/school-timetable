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

## Documentação
- `docs/literature_review.md` — papers e referências
- `docs/architecture.md` — arquitetura de software
- `docs/constraints.md` — catálogo de restrições duras e moles
- `docs/QUALITY_GATES.md` — quality gates do projeto
- `aes/kanban.md` — quadro de tickets AES
