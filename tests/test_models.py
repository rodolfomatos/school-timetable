"""Testes unitários para o modelo de domínio."""

from timetable.models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    RelacaoCasamento,
    RelacaoFilho,
    Sala,
    Slot,
    Turma,
)


def test_slot_igualdade_e_hash():
    s1 = Slot(dia="segunda", hora=1)
    s2 = Slot(dia="segunda", hora=1)
    s3 = Slot(dia="terca", hora=1)
    assert s1 == s2
    assert hash(s1) == hash(s2)
    assert s1 != s3


def test_professor_esta_disponivel():
    prof = Professor(
        identificador="p1",
        nome="Prof. X",
        disponibilidade=frozenset({Slot(dia="segunda", hora=1)}),
    )
    assert prof.esta_disponivel(Slot(dia="segunda", hora=1)) is True
    assert prof.esta_disponivel(Slot(dia="terca", hora=1)) is False


def test_sala_disponibilidade_vazia_significa_sempre_disponivel():
    sala = Sala(identificador="s1", capacidade=30)
    assert sala.disponivel_no_dia("qualquer_dia") is True


def test_horario_adicionar_e_consultas():
    h = Horario()
    aula = Aula(
        turma="Turma A",
        disciplina="Matemática",
        professor="p1",
        sala="s1",
        slot=Slot(dia="segunda", hora=1),
    )
    h.adicionar(aula)
    assert h.professor_ocupado_em("p1", Slot(dia="segunda", hora=1)) is True
    assert h.sala_ocupada_em("s1", Slot(dia="segunda", hora=1)) is True
    assert h.turma_ocupada_em("Turma A", Slot(dia="segunda", hora=1)) is True
    assert h.professor_ocupado_em("p1", Slot(dia="segunda", hora=2)) is False


def test_horario_clone():
    h = Horario()
    h.adicionar(
        Aula(
            turma="Turma A",
            disciplina="Matemática",
            professor="p1",
            sala="s1",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    h2 = h.clone()
    assert len(h2.aulas) == 1
    h2.remover(h2.aulas[0])
    assert len(h.aulas) == 1  # original inalterado


def test_relacao_casamento():
    rc = RelacaoCasamento(professor_a="p1", professor_b="p2")
    assert rc.professor_a == "p1"
    assert rc.professor_b == "p2"


def test_relacao_filho():
    rf = RelacaoFilho(
        professor_pai="p1",
        professor_mae="p2",
        identificador_turma_filho="Turma B",
    )
    assert rf.identificador_turma_filho == "Turma B"


def test_disciplina_padrao():
    d = Disciplina(identificador="d1", nome="Matemática", carga_semanal=4)
    assert d.tipo_sala_requerida == "normal"


def test_turma():
    t = Turma(identificador="Turma A", ano=10, numero_alunos=25)
    assert t.ano == 10
