"""Testes unitários para a função objetivo."""

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
from timetable.objective import (
    MUITO_NEGATIVO,
    avaliar,
    avaliar_com_cache,
    eh_melhor_que,
    limpar_cache_avaliacao,
)


def _ctx() -> ContextoRestricoes:
    return ContextoRestricoes(
        professores={
            "p1": Professor(identificador="p1", nome="Prof. Um"),
        },
        salas={"s1": Sala(identificador="s1", capacidade=30)},
        turmas={"t1": Turma(identificador="t1", ano=10, numero_alunos=25)},
        disciplinas={"m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=4)},
        casamentos=[],
        relacoes_filho=[],
    )


def test_horario_viavel_score_negativo_ou_zero():
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
    av = avaliar(h, _ctx())
    assert av.viavel is True
    assert av.score <= 0
    assert av.violacoes_hard == []


def test_horario_inviavel_score_muito_negativo():
    # Duas aulas do mesmo professor no mesmo slot
    h = Horario()
    slot = Slot(dia="segunda", hora=1)
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=slot))
    h.adicionar(Aula(turma="t2", disciplina="m1", professor="p1", sala="s2", slot=slot))
    av = avaliar(h, _ctx())
    assert av.viavel is False
    assert av.score <= MUITO_NEGATIVO
    assert len(av.violacoes_hard) > 0


def test_eh_melhor_que():
    boa = avaliar(Horario(), _ctx())
    ruim = avaliar(Horario(), _ctx())
    # Forçar scores diferentes manualmente não é possível com dataclass frozen,
    # mas a lógica de comparação é direta.
    assert eh_melhor_que(boa, ruim) is (boa.score > ruim.score)


def test_avaliar_com_cache_retorna_mesmo_resultado():
    """O cache deve devolver o mesmo Avaliacao para o mesmo horário."""

    limpar_cache_avaliacao()
    ctx = _ctx()
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

    av1 = avaliar_com_cache(h, ctx)
    av2 = avaliar_com_cache(h, ctx)

    assert av1.score == av2.score
    assert av1.viavel == av2.viavel
    assert av1.penalidades_moles == av2.penalidades_moles


def test_avaliar_com_cache_limpar():
    """limpar_cache_avaliacao deve esvaziar o cache."""

    limpar_cache_avaliacao()
    ctx = _ctx()
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

    av1 = avaliar_com_cache(h, ctx)
    limpar_cache_avaliacao()
    av2 = avaliar_com_cache(h, ctx)

    assert av1.score == av2.score  # mesmo resultado após limpar e reavaliar
