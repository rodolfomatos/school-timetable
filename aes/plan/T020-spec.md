# AES Plan Spec — T020 Exportação iCal/CSV

## 1. Sumário Executivo
Implementar exportação de horários para CSV e iCal (.ics) para integração com sistemas escolares existentes.

## 2. Formatos
### CSV
Colunas: turma, disciplina, professor, sala, dia, hora, semana

### iCal (.ics)
Cada aula é um evento VEVENT com:
- DTSTART/DTEND: data e hora da aula
- SUMMARY: disciplina
- DESCRIPTION: professor e sala
- LOCATION: sala
- UID: identificador único

## 3. Interface
- `exportar_csv(horario, caminho)` — escreve CSV
- `exportar_ical(horario, caminho)` — escreve .ics
- CLI: `python scripts/cli.py exportar --input horario.json --output saida.csv --formato csv`

## 4. Testes
- Teste de exportação CSV (verifica colunas e conteúdo)
- Teste de exportação iCal (verifica cabeçalho e eventos)

## Fase atual
Plan → Build.
