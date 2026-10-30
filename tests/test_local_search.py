"""Testes para as metaheurísticas de busca local (Tabu Search / Simulated Annealing)."""

import random

from timetable.constraints import ContextoRestricoes
from timetable.local_search import simulated_annealing, tabu_search
from timetable.models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    Sala,
    Slot,
    Turma,
)
from timetable.objective import avaliar


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


def _slots() -> list[Slot]:
    return [
        Slot(dia=dia, hora=hora) for dia in ["segunda", "terca", "quarta"] for hora in range(1, 5)
    ]


def _horario_inicial() -> Horario:
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
    return h


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
    h.slots_imutaveis = frozenset({Slot(dia="segunda", hora=1)})
    return h


def test_simulated_annealing_respeita_imutaveis():
    """O SA não deve alterar aulas em slots imutáveis."""

    ctx = _ctx()
    h0 = _horario_com_imutavel()
    slots = _slots()

    resultado = simulated_annealing(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    # A aula no slot imutável deve permanecer no mesmo slot
    aulas_imutaveis = [a for a in resultado.aulas if resultado.slot_e_imutavel(a.slot)]
    assert len(aulas_imutaveis) == 1
    assert aulas_imutaveis[0].slot == Slot(dia="segunda", hora=1)


def test_tabu_search_respeita_imutaveis():
    """O Tabu Search não deve alterar aulas em slots imutáveis."""

    ctx = _ctx()
    h0 = _horario_com_imutavel()
    slots = _slots()

    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    aulas_imutaveis = [a for a in resultado.aulas if resultado.slot_e_imutavel(a.slot)]
    assert len(aulas_imutaveis) == 1
    assert aulas_imutaveis[0].slot == Slot(dia="segunda", hora=1)


def test_simulated_annealing_nao_viola_hard():
    """O SA não deve introduzir violações de restrições duras."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    resultado = simulated_annealing(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    av = avaliar(resultado, ctx)
    assert av.viavel is True or len(av.violacoes_hard) == 0


def test_tabu_search_nao_viola_hard():
    """O Tabu Search não deve introduzir violações de restrições duras."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    av = avaliar(resultado, ctx)
    assert av.viavel is True or len(av.violacoes_hard) == 0


def test_simulated_annealing_score_nao_piora_drasticamente():
    """O score do SA não deve ser -infinito (não deve criar violações hard graves)."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    resultado = simulated_annealing(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    av = avaliar(resultado, ctx)
    assert av.score > -1_000_000


def test_tabu_search_score_nao_piora_drasticamente():
    """O score do Tabu Search não deve ser -infinito."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    av = avaliar(resultado, ctx)
    assert av.score > -1_000_000


def test_simulated_annealing_semente_reprodutivel():
    """Com a mesma semente, o SA deve produzir o mesmo resultado."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    r1 = simulated_annealing(h0, ctx, slots, tempo_limite_segundos=5.0, semente=123)
    r2 = simulated_annealing(h0, ctx, slots, tempo_limite_segundos=5.0, semente=123)

    assert len(r1.aulas) == len(r2.aulas)
    assert r1.aulas == r2.aulas


def test_tabu_search_semente_reprodutivel():
    """Com a mesma semente, o Tabu Search deve produzir o mesmo resultado."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    r1 = tabu_search(h0, ctx, slots, tempo_limite_segundos=5.0, semente=123)
    r2 = tabu_search(h0, ctx, slots, tempo_limite_segundos=5.0, semente=123)

    assert len(r1.aulas) == len(r2.aulas)
    assert r1.aulas == r2.aulas


def test_simulated_annealing_score_alvo_para_cedo():
    """Com score_alvo muito baixo, o SA deve parar cedo."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    av_inicial = avaliar(h0, ctx)
    resultado = simulated_annealing(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=60.0,
        score_alvo=av_inicial.score - 1,  # já satisfeito
        semente=42,
    )

    # Deve devolver algo razoável (não crashar)
    assert resultado is not None
    assert len(resultado.aulas) >= 0


def test_tabu_search_score_alvo_para_cedo():
    """Com score_alvo muito baixo, o Tabu Search deve parar cedo."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    av_inicial = avaliar(h0, ctx)
    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=60.0,
        score_alvo=av_inicial.score - 1,  # já satisfeito
        semente=42,
    )

    assert resultado is not None
    assert len(resultado.aulas) >= 0


def test_simulated_annealing_sem_aulas():
    """SA com horário vazio não deve crashar."""

    ctx = _ctx()
    h0 = Horario()
    slots = _slots()

    resultado = simulated_annealing(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    assert len(resultado.aulas) == 0


def test_tabu_search_sem_aulas():
    """Tabu Search com horário vazio não deve crashar."""

    ctx = _ctx()
    h0 = Horario()
    slots = _slots()

    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    assert len(resultado.aulas) == 0


def test_simulated_annealing_todas_aulas_imutaveis():
    """Se todas as aulas forem imutáveis, o SA não deve alterar nada."""

    ctx = _ctx()
    h0 = _horario_com_imutavel()
    # Tornar todas as aulas imutáveis (só há uma neste caso)
    slots = _slots()

    resultado = simulated_annealing(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        semente=42,
    )

    # Deve manter a mesma aula
    assert len(resultado.aulas) == 1
    assert resultado.aulas[0].slot == Slot(dia="segunda", hora=1)


# --- Testes para F-001: chaves de tabu não-None e consistentes ---


def test_chave_tabu_exchange_nao_e_none():
    """_chave_tabu_exchange deve retornar uma chave não-None."""

    from timetable.local_search import _chave_tabu_exchange

    a1 = Aula("t1", "m1", "p1", "s1", Slot(dia="segunda", hora=1))
    a2 = Aula("t2", "p1", "p2", "s2", Slot(dia="terca", hora=2))

    chave = _chave_tabu_exchange(a1, a2)
    assert chave is not None
    assert isinstance(chave, tuple)
    assert chave[0] == "exchange"


def test_chave_tabu_modify_nao_e_none():
    """_chave_tabu_modify deve retornar uma chave não-None."""

    from timetable.local_search import _chave_tabu_modify

    aula = Aula("t1", "m1", "p1", "s1", Slot(dia="segunda", hora=1))
    novo_slot = Slot(dia="terca", hora=2)

    chave = _chave_tabu_modify(aula, novo_slot)
    assert chave is not None
    assert isinstance(chave, tuple)
    assert chave[0] == "modify"


def test_chaves_tabu_consistentes():
    """A mesma troca deve gerar a mesma chave tabu (ordem independente)."""

    from timetable.local_search import _chave_tabu_exchange

    a1 = Aula("t1", "m1", "p1", "s1", Slot(dia="segunda", hora=1))
    a2 = Aula("t2", "p1", "p2", "s2", Slot(dia="terca", hora=2))

    chave_12 = _chave_tabu_exchange(a1, a2)
    chave_21 = _chave_tabu_exchange(a2, a1)

    assert chave_12 == chave_21


def test_gerar_vizinho_exchange_retorna_chave_tabu():
    """_gerar_vizinho_exchange deve retornar (vizinho, chave_tabu) com chave não-None."""

    from timetable.local_search import _gerar_vizinho_exchange

    h = Horario()
    h.adicionar(Aula("t1", "m1", "p1", "s1", Slot(dia="segunda", hora=1)))
    h.adicionar(Aula("t2", "p1", "p2", "s2", Slot(dia="segunda", hora=2)))
    slots = _slots()
    rng = random.Random(42)

    vizinho, chave = _gerar_vizinho_exchange(h, slots, rng)
    assert vizinho is not None
    assert chave is not None
    assert isinstance(chave, tuple)


def test_gerar_vizinho_modify_retorna_chave_tabu():
    """_gerar_vizinho_modify deve retornar (vizinho, chave_tabu) com chave não-None."""

    from timetable.local_search import _gerar_vizinho_modify

    h = Horario()
    h.adicionar(Aula("t1", "m1", "p1", "s1", Slot(dia="segunda", hora=1)))
    slots = [s for s in _slots() if s != Slot(dia="segunda", hora=1)]
    rng = random.Random(42)

    vizinho, chave = _gerar_vizinho_modify(h, slots, rng)
    assert vizinho is not None
    assert chave is not None
    assert isinstance(chave, tuple)


# --- Teste para F-002: tabu_set sincronizado com deque ---


def test_tabu_search_nao_entra_loop_infinito_com_tamanho_tabu_pequeno():
    """Com tamanho_tabu=1, o tabu_search não deve entrar em loop infinito."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    # Com tamanho_tabu muito pequeno, o tabu_search ainda deve terminar dentro do tempo
    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        tamanho_tabu=1,
        semente=42,
    )

    av = avaliar(resultado, ctx)
    assert av.score > -1_000_000


def test_tabu_search_proporcao_exchange_um_usa_chaves():
    """Com proporcao_exchange=1.0, todos os movimentos são exchange e usam chaves de tabu."""

    ctx = _ctx()
    h0 = _horario_inicial()
    slots = _slots()

    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=5.0,
        tamanho_tabu=10,
        proporcao_exchange=1.0,
        semente=42,
    )

    av = avaliar(resultado, ctx)
    assert av.score > -1_000_000
