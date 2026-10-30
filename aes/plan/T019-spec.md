# AES Plan Spec — T019 CLI

## 1. Sumário Executivo
Implementar uma interface de linha de comando (CLI) para tornar o solver usável por não-programadores.

## 2. Subcomandos
### generate
- Argumentos: --input (dataset JSON), --output (horário JSON), --solver (sa|ts|cpsat), --tempo (segundos)
- Carrega dataset, executa solver, exporta resultado

### validate
- Argumentos: --input (horário JSON)
- Carrega horário, verifica restrições duras, reporta violações

### benchmark
- Argumentos: --input (dataset JSON), --tempo (segundos)
- Executa todos os solvers e reporta métricas comparativas

## 3. Saída
Todos os subcomandos imprimem saída legível para o utilizador e (quando aplicável) escrevem ficheiros JSON.

## 4. Testes
- Teste de CLI generate com dataset pequeno
- Teste de CLI validate com horário válido e inválido
- Teste de ajuda (--help)

## Fase atual
Plan → Build.
