"""Exportação de horários para CSV e iCal (.ics).

Permite integrar horários gerados com sistemas escolares existentes
(Calendário Google, Outlook, Excel, Apple Calendar, etc.).
"""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path

from .models import Horario, Slot

# Mapeamento de dias da semana para números (segunda=0)
DIAS_SEMANA = {
    "segunda": 0,
    "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sabado": 5,
    "domingo": 6,
}


def _data_para_slot(slot: Slot, semana_inicial: str = "2026-09-07") -> datetime:
    """Converte um Slot em um datetime para a data correta da semana."""

    dia_semana = DIAS_SEMANA.get(slot.dia, 0)
    data_base = datetime.strptime(semana_inicial, "%Y-%m-%d")
    # Encontra a primeira ocorrência do dia da semana a partir de data_base
    dias_para_adicionar = (dia_semana - data_base.weekday()) % 7
    data_aula = data_base + timedelta(days=dias_para_adicionar)
    return data_aula.replace(hour=slot.hora, minute=0, second=0, microsecond=0)


def exportar_csv(horario: Horario, caminho: str | Path, semana_inicial: str = "2026-09-07") -> None:
    """Exporta o horário para CSV.

    Colunas: turma, disciplina, professor, sala, dia, hora, data
    """

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["turma", "disciplina", "professor", "sala", "dia", "hora", "data"])
        for aula in sorted(
            horario.aulas,
            key=lambda a: (DIAS_SEMANA.get(a.slot.dia, 0), a.slot.hora, a.turma),
        ):
            data = _data_para_slot(aula.slot, semana_inicial).strftime("%Y-%m-%d")
            writer.writerow(
                [
                    aula.turma,
                    aula.disciplina,
                    aula.professor,
                    aula.sala,
                    aula.slot.dia,
                    aula.slot.hora,
                    data,
                ]
            )


def exportar_ical(
    horario: Horario,
    caminho: str | Path,
    semana_inicial: str = "2026-09-07",
    nome_escola: str = "Escola",
) -> None:
    """Exporta o horário para iCal (.ics).

    Cada aula torna-se um evento VEVENT com DTSTART/DTEND, SUMMARY,
    DESCRIPTION, LOCATION e UID.
    """

    linhas: list[str] = []
    linhas.append("BEGIN:VCALENDAR")
    linhas.append("VERSION:2.0")
    linhas.append("PRODID:-//school-timetable//Horário Escolar//PT")
    linhas.append("CALSCALE:GREGORIAN")
    linhas.append("METHOD:PUBLISH")
    linhas.append(f"X-WR-CALNAME:Horário — {nome_escola}")
    linhas.append("X-WR-TIMEZONE:Europe/Lisbon")
    linhas.append("")

    for i, aula in enumerate(
        sorted(
            horario.aulas,
            key=lambda a: (DIAS_SEMANA.get(a.slot.dia, 0), a.slot.hora, a.turma),
        )
    ):
        inicio = _data_para_slot(aula.slot, semana_inicial)
        fim = inicio + timedelta(hours=1)

        linhas.append("BEGIN:VEVENT")
        linhas.append(f"UID:{aula.turma}-{aula.disciplina}-{i}@school-timetable.local")
        linhas.append(f"DTSTAMP:{inicio.strftime('%Y%m%dT%H%M%SZ')}")
        linhas.append(f"DTSTART:{inicio.strftime('%Y%m%dT%H%M%S')}")
        linhas.append(f"DTEND:{fim.strftime('%Y%m%dT%H%M%S')}")
        linhas.append(f"SUMMARY:{aula.disciplina}")
        linhas.append(
            f"DESCRIPTION:Professor: {aula.professor}\\nSala: {aula.sala}\\nTurma: {aula.turma}"
        )
        linhas.append(f"LOCATION:{aula.sala}")
        linhas.append("END:VEVENT")
        linhas.append("")

    linhas.append("END:VCALENDAR")
    linhas.append("")

    Path(caminho).write_text("\r\n".join(linhas), encoding="utf-8")


def exportar(
    horario: Horario,
    caminho: str | Path,
    formato: str = "csv",
    semana_inicial: str = "2026-09-07",
    nome_escola: str = "Escola",
) -> None:
    """Exporta o horário no formato especificado.

    Args:
        horario: O horário a exportar.
        caminho: Caminho do ficheiro de saída.
        formato: "csv" ou "ical".
        semana_inicial: Data da primeira segunda-feira do ano letivo.
        nome_escola: Nome da escola (usado no iCal).
    """

    if formato.lower() == "csv":
        exportar_csv(horario, caminho, semana_inicial)
    elif formato.lower() in ("ical", "ics"):
        exportar_ical(horario, caminho, semana_inicial, nome_escola)
    else:
        raise ValueError(f"Formato desconhecido: {formato}. Use 'csv' ou 'ical'.")
