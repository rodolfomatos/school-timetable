"""Testes para a interface de ajustamento manual (UI)."""

import json
import tempfile
from pathlib import Path

import pytest

from timetable.constraints import ContextoRestricoes
from timetable.models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    Sala,
    Slot,
    Turma,
)
from timetable.ui import (
    exportar_json,
    gerar_grade,
    importar_json,
    listar_aulas_imutaveis,
    listar_aulas_mutaveis,
    mover_aula,
    remover_aula,
    trocar_aulas,
    validar_apos_movimento,
)


def _ctx() -> ContextoRestricoes:
    return ContextoRestricoes(
        professores={
            "p1": Professor(identificador="p1", nome="Prof. Um"),
            "p2": Professor(identificador="p2", nome="Prof. Dois"),
        },
        salas={
            "s1": Sala(identificador="s1", capacidade=30),
            "s2": Sala(identificador="s2", capacidade=30),
        },
        turmas={
            "t1": Turma(identificador="t1", ano=10, numero_alunos=25),
            "t2": Turma(identificador="t2", ano=10, numero_alunos=25),
        },
        disciplinas={
            "m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=1),
            "p1": Disciplina(identificador="p1", nome="Português", carga_semanal=1),
        },
        casamentos=[],
        relacoes_filho=[],
    )


def _horario_com_imutavel() -> Horario:
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1",
            disciplina="m1",
            professor="p1",
            sala="s1",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    h.adicionar(
        Aula(
            turma="t2",
            disciplina="p1",
            professor="p2",
            sala="s2",
            slot=Slot(dia="segunda", hora=2),
        )
    )
    h.slots_imutaveis = frozenset({Slot(dia="segunda", hora=1)})
    return h


def test_exportar_importar_json_integridade():
    """Exportar e importar deve preservar aulas e slots imutáveis."""

    h = _horario_com_imutavel()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        caminho = f.name

    try:
        exportar_json(h, caminho)
        h2 = importar_json(caminho)

        assert len(h2.aulas) == len(h.aulas)
        assert h2.slots_imutaveis == h.slots_imutaveis
        for a1, a2 in zip(sorted(h.aulas, key=str), sorted(h2.aulas, key=str)):
            assert a1.turma == a2.turma
            assert a1.disciplina == a2.disciplina
            assert a1.professor == a2.professor
            assert a1.sala == a2.sala
            assert a1.slot == a2.slot
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_gerar_grade_indexa_por_turma_e_slot():
    """A grade deve indexar aulas por (turma, slot)."""

    h = _horario_com_imutavel()
    grade = gerar_grade(h)

    chave = ("t1", Slot(dia="segunda", hora=1))
    assert chave in grade
    assert grade[chave].professor == "p1"
    assert len(grade) == 2


def test_mover_aula_respeita_slot_imutavel_origem():
    """Não deve mover uma aula cujo slot de origem é imutável."""

    h = _horario_com_imutavel()
    aula_imutavel = listar_aulas_imutaveis(h)[0]

    resultado = mover_aula(h, aula_imutavel, Slot(dia="terca", hora=1))

    # Deve ser uma cópia inalterada
    assert len(resultado.aulas) == 2
    assert resultado.aulas[0].slot == Slot(dia="segunda", hora=1)


def test_mover_aula_respeita_slot_imutavel_destino():
    """Não deve mover uma aula para um slot de destino imutável."""

    h = _horario_com_imutavel()
    aula_mutavel = listar_aulas_mutaveis(h)[0]

    resultado = mover_aula(
        h,
        aula_mutavel,
        Slot(dia="segunda", hora=1),  # slot imutável
    )

    assert len(resultado.aulas) == 2
    # A aula mutável deve permanecer no mesmo slot
    mutaveis_no_resultado = [a for a in resultado.aulas if not resultado.slot_e_imutavel(a.slot)]
    assert len(mutaveis_no_resultado) == 1
    assert mutaveis_no_resultado[0].slot == aula_mutavel.slot


def test_mover_aula_mutavel_funciona():
    """Deve mover uma aula mutável para um novo slot."""

    h = _horario_com_imutavel()
    aula_mutavel = listar_aulas_mutaveis(h)[0]
    novo_slot = Slot(dia="terca", hora=3)

    resultado = mover_aula(h, aula_mutavel, novo_slot)

    assert len(resultado.aulas) == 2
    aula_movida = [a for a in resultado.aulas if a.turma == aula_mutavel.turma][0]
    assert aula_movida.slot == novo_slot


def test_trocar_aulas_respeita_slots_imutaveis():
    """Não deve trocar se qualquer um dos slots for imutável."""

    h = _horario_com_imutavel()
    aula_imutavel = listar_aulas_imutaveis(h)[0]
    aula_mutavel = listar_aulas_mutaveis(h)[0]

    resultado = trocar_aulas(h, aula_imutavel, aula_mutavel)

    # Deve ser inalterado
    assert len(resultado.aulas) == 2
    assert resultado.aulas[0].slot == Slot(dia="segunda", hora=1)
    assert resultado.aulas[1].slot == Slot(dia="segunda", hora=2)


def test_trocar_aulas_mutaveis_funciona():
    """Deve trocar os slots de duas aulas mutáveis."""

    h = Horario()
    h.adicionar(
        Aula(
            turma="t1",
            disciplina="m1",
            professor="p1",
            sala="s1",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    h.adicionar(
        Aula(
            turma="t2",
            disciplina="p1",
            professor="p2",
            sala="s2",
            slot=Slot(dia="segunda", hora=2),
        )
    )
    # Nenhum slot imutável
    h.slots_imutaveis = frozenset()

    a1 = h.aulas[0]
    a2 = h.aulas[1]

    resultado = trocar_aulas(h, a1, a2)

    assert len(resultado.aulas) == 2
    slot_a1_no_resultado = [a.slot for a in resultado.aulas if a.turma == "t1"][0]
    slot_a2_no_resultado = [a.slot for a in resultado.aulas if a.turma == "t2"][0]
    assert slot_a1_no_resultado == Slot(dia="segunda", hora=2)
    assert slot_a2_no_resultado == Slot(dia="segunda", hora=1)


def test_remover_aula_respeita_slot_imutavel():
    """Não deve remover uma aula cujo slot é imutável."""

    h = _horario_com_imutavel()
    aula_imutavel = listar_aulas_imutaveis(h)[0]

    resultado = remover_aula(h, aula_imutavel)

    assert len(resultado.aulas) == 2  # inalterado


def test_remover_aula_mutavel_funciona():
    """Deve remover uma aula mutável."""

    h = _horario_com_imutavel()
    aula_mutavel = listar_aulas_mutaveis(h)[0]

    resultado = remover_aula(h, aula_mutavel)

    assert len(resultado.aulas) == 1
    assert resultado.aulas[0].turma == "t1"  # a imutável permanece


def test_listar_aulas_mutaveis_e_imutaveis():
    """Deve listar corretamente aulas mutáveis e imutáveis."""

    h = _horario_com_imutavel()
    mutaveis = listar_aulas_mutaveis(h)
    imutaveis = listar_aulas_imutaveis(h)

    assert len(mutaveis) == 1
    assert len(imutaveis) == 1
    assert mutaveis[0].slot == Slot(dia="segunda", hora=2)
    assert imutaveis[0].slot == Slot(dia="segunda", hora=1)


def test_validar_apos_movimento_sem_violacoes():
    """A validação após um movimento válido deve retornar lista vazia."""

    h = _horario_com_imutavel()
    ctx = _ctx()
    aula_mutavel = listar_aulas_mutaveis(h)[0]
    novo_slot = Slot(dia="terca", hora=3)

    resultado = mover_aula(h, aula_mutavel, novo_slot)
    violacoes = validar_apos_movimento(resultado, ctx)

    assert violacoes == []


def test_importar_json_estrutura_invalida_retorna_horario_vazio():
    """JSON sem aulas deve retornar horário vazio."""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(json.dumps({"versao": "0.1", "aulas": []}))
        caminho = f.name

    try:
        h = importar_json(caminho)
        assert len(h.aulas) == 0
        assert h.slots_imutaveis == frozenset()
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_importar_json_campo_obrigatorio_em_falta_levanta_erro():
    """JSON com campo obrigatório em falta deve levantar ValueError descritivo."""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(json.dumps({"versao": "0.1", "aulas": [{"turma": "t1"}]}))
        caminho = f.name

    try:
        with pytest.raises(ValueError, match="campo 'disciplina' em falta"):
            importar_json(caminho)
    finally:
        Path(caminho).unlink(missing_ok=True)


def test_importar_json_slot_campo_em_falta_levanta_erro():
    """JSON com campo obrigatório do slot em falta deve levantar ValueError descritivo."""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "versao": "0.1",
                    "aulas": [
                        {
                            "turma": "t1",
                            "disciplina": "m1",
                            "professor": "p1",
                            "sala": "s1",
                            "slot": {"dia": "segunda"},
                        }
                    ],
                }
            )
        )
        caminho = f.name

    try:
        with pytest.raises(ValueError, match="slot.campo 'hora' em falta"):
            importar_json(caminho)
    finally:
        Path(caminho).unlink(missing_ok=True)
