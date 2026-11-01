"""Testes unitários para a função objetivo, cache e avaliação incremental."""

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
    avaliar_incremental,
    eh_melhor_que,
    estatisticas_cache,
    limpar_cache_avaliacao,
)


def _ctx() -> ContextoRestricoes:
    return ContextoRestricoes(
        professores={
            "p1": Professor(
                identificador="p1",
                nome="Prof. Um",
                carga_minima_semanal=0,  # evitar S07
            ),
        },
        salas={"s1": Sala(identificador="s1", capacidade=30)},
        turmas={"t1": Turma(identificador="t1", ano=10, numero_alunos=25)},
        disciplinas={"m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=4)},
        casamentos=[],
        relacoes_filho=[],
    )


def _ctx_diferente() -> ContextoRestricoes:
    """Contexto com professor diferente (dia de folga), mesmo resto."""
    return ContextoRestricoes(
        professores={
            "p1": Professor(
                identificador="p1",
                nome="Prof. Um",
                dia_folga_preferido="segunda",
                carga_minima_semanal=0,  # evitar S07
            ),
        },
        salas={"s1": Sala(identificador="s1", capacidade=30)},
        turmas={"t1": Turma(identificador="t1", ano=10, numero_alunos=25)},
        disciplinas={"m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=4)},
        casamentos=[],
        relacoes_filho=[],
    )


def _horario_base() -> Horario:
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
    return h


def test_horario_viavel_score_negativo_ou_zero():
    h = _horario_base()
    av = avaliar(h, _ctx())
    assert av.viavel is True
    assert av.score <= 0
    assert av.violacoes_hard == []


def test_horario_inviavel_score_muito_negativo():
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
    assert eh_melhor_que(boa, ruim) is (boa.score > ruim.score)


def test_avaliar_com_cache_retorna_mesmo_resultado():
    """O cache deve devolver o mesmo Avaliacao para o mesmo horário."""
    limpar_cache_avaliacao()
    ctx = _ctx()
    h = _horario_base()

    av1 = avaliar_com_cache(h, ctx)
    av2 = avaliar_com_cache(h, ctx)

    assert av1.score == av2.score
    assert av1.viavel == av2.viavel
    assert av1.penalidades_moles == av2.penalidades_moles


def test_avaliar_com_cache_limpar():
    """limpar_cache_avaliacao deve esvaziar o cache."""
    limpar_cache_avaliacao()
    ctx = _ctx()
    h = _horario_base()

    av1 = avaliar_com_cache(h, ctx)
    limpar_cache_avaliacao()
    av2 = avaliar_com_cache(h, ctx)

    assert av1.score == av2.score


def test_cache_chave_inclui_contexto():
    """Mesmo horário em contextos diferentes não deve partilhar cache."""
    limpar_cache_avaliacao()
    h = _horario_base()

    # Contexto 1: sem dia de folga -> sem penalidade S01
    ctx1 = _ctx()
    av1 = avaliar_com_cache(h, ctx1)
    stats1 = estatisticas_cache()
    assert stats1["hits"] == 0
    assert stats1["misses"] == 1

    # Contexto 2: com dia de folga -> penalidade S01 (10)
    ctx2 = _ctx_diferente()
    av2 = avaliar_com_cache(h, ctx2)
    stats2 = estatisticas_cache()
    assert stats2["hits"] == 0
    assert stats2["misses"] == 2  # ambas miss, chaves diferentes

    # Scores devem ser diferentes (ctx2 tem penalidade S01)
    assert av1.score != av2.score
    assert av2.score == av1.score - 10  # penalidade S01 = 10


def test_cache_estatisticas():
    """estatisticas_cache deve reportar hits, misses, evictions."""
    limpar_cache_avaliacao()
    ctx = _ctx()
    h = _horario_base()

    stats = estatisticas_cache()
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["size"] == 0

    avaliar_com_cache(h, ctx)
    stats = estatisticas_cache()
    assert stats["misses"] == 1
    assert stats["hits"] == 0
    assert stats["size"] == 1

    avaliar_com_cache(h, ctx)  # hit
    stats = estatisticas_cache()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 0.5


def test_cache_lru_eviction():
    """Cache deve evict entradas antigas quando atinge MAX_CACHE_SIZE."""
    from timetable.objective import _MAX_CACHE_SIZE
    limpar_cache_avaliacao()
    ctx = _ctx()

    # Preencher cache até o limite
    for i in range(_MAX_CACHE_SIZE + 10):
        h = Horario()
        h.adicionar(
            Aula(
                turma=f"t{i}",
                disciplina="m1",
                professor="p1",
                sala="s1",
                slot=Slot(dia="segunda", hora=1),
            )
        )
        avaliar_com_cache(h, ctx)

    stats = estatisticas_cache()
    assert stats["size"] == _MAX_CACHE_SIZE
    assert stats["evictions"] == 10


def test_avaliar_incremental_sem_base_faz_completa():
    """Sem avaliacao_base, avaliar_incremental deve fazer avaliação completa."""
    limpar_cache_avaliacao()
    ctx = _ctx()
    h = _horario_base()

    # Move: remove aula antiga, adiciona nova no slot diferente
    aula_antiga = h.aulas[0]
    aula_nova = Aula(
        turma="t1", disciplina="m1", professor="p1", sala="s1",
        slot=Slot(dia="segunda", hora=2)
    )

    av = avaliar_incremental(h, ctx, [aula_antiga], [aula_nova])
    # Deve ser viável e ter score calculado
    assert av.viavel is True
    assert av.score <= 0


def test_avaliar_incremental_preserva_viavel():
    """Movimento válido deve preservar viabilidade."""
    limpar_cache_avaliacao()
    ctx = _ctx()
    h = _horario_base()
    av_base = avaliar(h, ctx)
    assert av_base.viavel

    aula_antiga = h.aulas[0]
    aula_nova = Aula(
        turma="t1", disciplina="m1", professor="p1", sala="s1",
        slot=Slot(dia="terca", hora=1)
    )

    av = avaliar_incremental(h, ctx, [aula_antiga], [aula_nova], av_base)
    assert av.viavel is True
    # Score deve mudar (mesmo horário, sem penalidades)
    assert av.score == av_base.score


def test_avaliar_incremental_detecta_h01():
    """Movimento que causa H01 deve tornar inviável."""
    limpar_cache_avaliacao()
    ctx = _ctx()
    # Contexto com 2 turmas, mesmo professor
    ctx.turmas["t2"] = Turma(identificador="t2", ano=10, numero_alunos=25)
    ctx.salas["s2"] = Sala(identificador="s2", capacidade=30)

    h = Horario()
    slot = Slot(dia="segunda", hora=1)
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=slot))
    h.adicionar(Aula(turma="t2", disciplina="m1", professor="p1", sala="s2", slot=slot))
    av_base = avaliar(h, ctx)
    assert not av_base.viavel  # já inviável

    # Mesmo se base já inviável, incremental deve retornar inviável
    aula_antiga = h.aulas[0]
    aula_nova = Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="terca", hora=1))
    av = avaliar_incremental(h, ctx, [aula_antiga], [aula_nova], av_base)
    assert av.viavel is False


def test_avaliar_incremental_delta_score():
    """Delta de score deve bater com avaliação completa."""
    limpar_cache_avaliacao()
    ctx = _ctx_diferente()  # com dia de folga segunda
    h = _horario_base()
    av_base = avaliar(h, ctx)

    # Move aula de segunda (dia de folga) para terça
    aula_antiga = h.aulas[0]
    aula_nova = Aula(
        turma="t1", disciplina="m1", professor="p1", sala="s1",
        slot=Slot(dia="terca", hora=1)
    )

    av_inc = avaliar_incremental(h, ctx, [aula_antiga], [aula_nova], av_base)

    # Avaliação completa do novo horário
    h_novo = Horario()
    h_novo.adicionar(aula_nova)
    av_full = avaliar(h_novo, ctx)

    # Scores devem bater (diferença <= 1 por arredondamentos)
    assert abs(av_inc.score - av_full.score) <= 1


def test_avaliar_incremental_s01_dia_folga():
    """Teste específico S01: mover de dia de folga para dia normal."""
    limpar_cache_avaliacao()
    ctx = _ctx_diferente()  # dia_folga_preferido = "segunda"
    h = _horario_base()  # aula na segunda
    av_base = avaliar(h, ctx)
    assert av_base.penalidades_moles == 10  # S01

    # Move para terça (não é dia de folga)
    aula_antiga = h.aulas[0]
    aula_nova = Aula(
        turma="t1", disciplina="m1", professor="p1", sala="s1",
        slot=Slot(dia="terca", hora=1)
    )

    av_inc = avaliar_incremental(h, ctx, [aula_antiga], [aula_nova], av_base)
    assert av_inc.penalidades_moles == 0  # S01 removida
    assert av_inc.score == av_base.score + 10


def test_avaliar_incremental_s02_prefere_manha():
    """Teste S02: mover de manhã para tarde penaliza."""
    limpar_cache_avaliacao()
    ctx = ContextoRestricoes(
        professores={
            "p1": Professor(
                identificador="p1", nome="Prof. Um", prefere_manha=True, carga_minima_semanal=0
            ),
        },
        salas={"s1": Sala(identificador="s1", capacidade=30)},
        turmas={"t1": Turma(identificador="t1", ano=10, numero_alunos=25)},
        disciplinas={"m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=4)},
        casamentos=[],
        relacoes_filho=[],
    )
    h = Horario()
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=10)))
    av_base = avaliar(h, ctx)
    assert av_base.penalidades_moles == 0

    # Move para tarde (hora 14)
    aula_antiga = h.aulas[0]
    aula_nova = Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=14))

    av_inc = avaliar_incremental(h, ctx, [aula_antiga], [aula_nova], av_base)
    assert av_inc.penalidades_moles == 8  # S02
    assert av_inc.score == av_base.score - 8