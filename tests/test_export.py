"""Testes para o módulo de exportação (CSV/iCal)."""

import csv
import io
import tempfile
from pathlib import Path

from timetable.export import exportar, exportar_csv, exportar_ical
from timetable.models import Aula, Horario, Slot


def _horario_exemplo() -> Horario:
    """Cria um horário de exemplo para testes de exportação."""

    h = Horario()
    h.adicionar(
        Aula(
            turma="t01",
            disciplina="Matemática",
            professor="p01",
            sala="s01",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    h.adicionar(
        Aula(
            turma="t02",
            disciplina="Português",
            professor="p02",
            sala="s02",
            slot=Slot(dia="terca", hora=2),
        )
    )
    h.adicionar(
        Aula(
            turma="t01",
            disciplina="Inglês",
            professor="p03",
            sala="s01",
            slot=Slot(dia="quarta", hora=3),
        )
    )
    return h


def test_exportar_csv_gera_colunas_corretas():
    """O CSV deve ter as colunas corretas."""

    h = _horario_exemplo()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        caminho = f.name

    try:
        exportar_csv(h, caminho)
        conteudo = Path(caminho).read_text(encoding="utf-8")
        linhas = conteudo.strip().split("\n")
        assert linhas[0] == "turma,disciplina,professor,sala,dia,hora,data"
        assert len(linhas) == 4  # cabeçalho + 3 aulas
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_exportar_csv_conteudo():
    """O CSV deve conter os dados corretos das aulas."""

    h = _horario_exemplo()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        caminho = f.name

    try:
        exportar_csv(h, caminho)
        conteudo = Path(caminho).read_text(encoding="utf-8")
        assert "t01,Matemática,p01,s01,segunda,1" in conteudo
        assert "t02,Português,p02,s02,terca,2" in conteudo
        assert "t01,Inglês,p03,s01,quarta,3" in conteudo
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_exportar_ical_gera_cabecalho():
    """O iCal deve ter cabeçalho VCALENDAR."""

    h = _horario_exemplo()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ics", delete=False, encoding="utf-8"
    ) as f:
        caminho = f.name

    try:
        exportar_ical(h, caminho)
        conteudo = Path(caminho).read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in conteudo
        assert "END:VCALENDAR" in conteudo
        assert "VERSION:2.0" in conteudo
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_exportar_ical_gera_eventos():
    """O iCal deve conter eventos VEVENT para cada aula."""

    h = _horario_exemplo()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ics", delete=False, encoding="utf-8"
    ) as f:
        caminho = f.name

    try:
        exportar_ical(h, caminho)
        conteudo = Path(caminho).read_text(encoding="utf-8")
        assert conteudo.count("BEGIN:VEVENT") == 3
        assert conteudo.count("END:VEVENT") == 3
        assert "SUMMARY:Matemática" in conteudo
        assert "SUMMARY:Português" in conteudo
        assert "SUMMARY:Inglês" in conteudo
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_exportar_formato_csv():
    """A função exportar com formato='csv' deve gerar CSV válido."""

    h = _horario_exemplo()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        caminho = f.name

    try:
        exportar(h, caminho, formato="csv")
        conteudo = Path(caminho).read_text(encoding="utf-8")
        assert "turma,disciplina,professor,sala,dia,hora,data" in conteudo
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_exportar_formato_ical():
    """A função exportar com formato='ical' deve gerar iCal válido."""

    h = _horario_exemplo()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ics", delete=False, encoding="utf-8"
    ) as f:
        caminho = f.name

    try:
        exportar(h, caminho, formato="ical")
        conteudo = Path(caminho).read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in conteudo
        assert "BEGIN:VEVENT" in conteudo
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_exportar_formato_invalido_levanta_erro():
    """A função exportar deve levantar ValueError para formato inválido."""

    h = _horario_exemplo()
    try:
        exportar(h, "/tmp/teste.xyz", formato="xml")
        assert False, "Deveria ter levantado ValueError"
    except ValueError:
        pass


def test_exportar_csv_ordena_por_dia_e_hora():
    """O CSV deve ordenar aulas por dia da semana e hora."""

    h = Horario()
    h.adicionar(
        Aula(
            turma="t01",
            disciplina="D",
            professor="p01",
            sala="s01",
            slot=Slot(dia="quarta", hora=2),
        )
    )
    h.adicionar(
        Aula(
            turma="t01",
            disciplina="A",
            professor="p01",
            sala="s01",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    h.adicionar(
        Aula(
            turma="t01",
            disciplina="B",
            professor="p01",
            sala="s01",
            slot=Slot(dia="terca", hora=3),
        )
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        caminho = f.name

    try:
        exportar_csv(h, caminho)
        conteudo = Path(caminho).read_text(encoding="utf-8")
        linhas = conteudo.strip().split("\n")
        # Primeira linha de dados deve ser segunda-feira
        assert "segunda" in linhas[1]
        assert "terca" in linhas[2]
        assert "quarta" in linhas[3]
    finally:
        Path(caminho).unlink(missing_ok=True)
