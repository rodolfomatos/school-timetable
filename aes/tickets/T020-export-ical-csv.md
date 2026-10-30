# Ticket T020 — Exportação iCal/CSV

## Contexto
Horários gerados precisam ser exportados para formatos usados por sistemas escolares existentes (Calendário Google, Outlook, Excel, etc.). Atualmente o projeto só exporta JSON próprio.

## Objetivo
Implementar exportação de horários para:
1. **CSV** — formato tabular simples (turma, disciplina, professor, sala, dia, hora)
2. **iCal (.ics)** — formato de calendário padrão (pode ser importado no Google Calendar, Outlook, Apple Calendar)

## Critérios de Aceitação
1. `src/timetable/export.py` implementado com funções `exportar_csv` e `exportar_ical`
2. Teste de exportação CSV com dados de exemplo
3. Teste de exportação iCal com dados de exemplo
4. CLI atualizada com subcomando `exportar` (ou integrado no generate)
5. `make test` passa, `make lint` passa

## Fase atual
Plan → Build.
