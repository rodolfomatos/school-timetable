"""Testes baseados em propriedades (Hypothesis) para restrições críticas.

Estes testes geram entradas aleatórias e verificam que propriedades
importantes são sempre satisfeitas, independentemente da entrada.
"""

from __future__ import annotations

from hypothesis import given, strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

from timetable.constraints import ContextoRestricoes, verificar_hard
from timetable.models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    Sala,
    Slot,
    Turma,
)
from timetable.ui import mover_aula, trocar_aulas
from timetable.objective import avaliar


# ---------------------------------------------------------------------------
# Estratégias de geração de dados
# ---------------------------------------------------------------------------

@st.composite
def _slot_estrategia(draw):
    """Gera um Slot aleatório."""

    dia = draw(st.sampled_from(["segunda", "terca", "quarta", "quinta", "sexta"]))
    hora = draw(st.integers(min_value=1, max_value=8))
    return Slot(dia=dia, hora=hora)


@st.composite
def _professor_estrategia(draw):
    """Gera um Professor aleatório."""

    return Professor(
        identificador=draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_characters="abcdefghijklmnopqrstuvwxyz0123456789"))),
        nome=draw(st.text(min_size=1, max_size=20)),
        carga_maxima_semanal=draw(st.integers(min_value=10, max_value=30)),
        carga_minima_semanal=draw(st.integers(min_value=2, max_value=10)),
    )


@st.composite
def _sala_estrategia(draw):
    """Gera uma Sala aleatória."""

    return Sala(
        identificador=draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_characters="abcdefghijklmnopqrstuvwxyz0123456789"))),
        capacidade=draw(st.integers(min_value=20, max_value=40)),
    )


@st.composite
def _turma_estrategia(draw):
    """Gera uma Turma aleatória."""

    return Turma(
        identificador=draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_characters="abcdefghijklmnopqrstuvwxyz0123456789"))),
        ano=draw(st.integers(min_value=7, max_value=12)),
        numero_alunos=draw(st.integers(min_value=20, max_value=35)),
    )


@st.composite
def _disciplina_estrategia(draw):
    """Gera uma Disciplina aleatória."""

    return Disciplina(
        identificador=draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_characters="abcdefghijklmnopqrstuvwxyz0123456789"))),
        nome=draw.st.text(min_size=1, max_size=20),
        carga_semanal=draw(st.integers(min_value=1, max_value=6)),
    )


# ---------------------------------------------------------------------------
# Propriedade P1: Slots imutáveis são respeitados
# ---------------------------------------------------------------------------


@given(
    num_aulas=st.integers(min_value=1, max_value=10),
    num_imutaveis=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=100, deadline=None)
def test_slots_imutaveis_sao_respeitados_por_mover(num_aulas, num_imutaveis):
    """Mover uma aula nunca altera um slot imutável."""

    # Cria slots e aulas
    slots = [Slot(dia="segunda", hora=h) for h in range(1, 6)]
    slots_imutaveis = frozenset(slots[:num_imutaveis])

    horario = Horario(slots_imutaveis=slots_imutaveis)
    for i in range(num_aulas):
        slot = slots[i % len(slots)]
        horario.adicionar(
            Aula(
                turma=f"t{i % 3}",
                disciplina="d1",
                professor="p1",
                sala="s1",
                slot=slot,
            )
        )

    # Tenta mover cada aula mutável para cada slot
    for aula in list(horario.aulas):
        if horario.slot_e_imutavel(aula.slot):
            continue
        for novo_slot in slots:
            if horario.slot_e_imutavel(novo_slot):
                continue
            resultado = mover_aula(horario, aula, novo_slot)

            # Verifica que aulas em slots imutáveis não mudaram
            for a in resultado.aulas:
                if horario.slot_e_imutavel(a.slot):
                    assert a in horario.aulas, (
                        f"Aula em slot imutável {a.slot} foi alterada: {a}"
                    )


@given(
    num_aulas=st.integers(min_value=2, max_value=10),
    num_imutaveis=st.integers(min_value=0, max_value=3),
)
@settings(max_examples=100, deadline=None)
def test_slots_imutaveis_sao_respeitados_por_trocar(num_aulas, num_imutaveis):
    """Trocar aulas nunca altera um slot imutável."""

    slots = [Slot(dia="segunda", hora=h) for h in range(1, 6)]
    slots_imutaveis = frozenset(slots[:num_imutaveis])

    horario = Horario(slots_imutaveis=slots_imutaveis)
    for i in range(num_aulas):
        slot = slots[i % len(slots)]
        horario.adicionar(
            Aula(
                turma=f"t{i % 3}",
                disciplina="d1",
                professor=f"p{i % 2}",
                sala="s1",
                slot=slot,
            )
        )

    aulas = list(horario.aulas)
    for i in range(len(aulas)):
        for j in range(i + 1, len(aulas)):
            a1, a2 = aulas[i], aulas[j]
            if horario.slot_e_imutavel(a1.slot) or horario.slot_e_imutavel(a2.slot):
                continue
            resultado = trocar_aulas(horario, a1, a2)

            # Verifica que aulas em slots imutáveis não mudaram
            for a in resultado.aulas:
                if horario.slot_e_imutavel(a.slot):
                    assert a in horario.aulas, (
                        f"Aula em slot imutável {a.slot} foi alterada por troca: {a}"
                    )


# ---------------------------------------------------------------------------
# Propriedade P2: Nenhuma violação dura piora com movimentos válidos
# ---------------------------------------------------------------------------


@given(
    num_aulas=st.integers(min_value=1, max_value=8),
)
@settings(max_examples=100, deadline=None)
def test_mover_com_validar_rejeita_novas_violacoes(num_aulas):
    """mover_aula com validar=True rejeita movimentos que criam violações duras."""

    ctx = ContextoRestricoes(
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
        },
        disciplinas={
            "d1": Disciplina(identificador="d1", nome="Matemática", carga_semanal=4),
        },
        casamentos=[],
        relacoes_filho=[],
    )

    slots = [Slot(dia="segunda", hora=h) for h in range(1, 6)]
    horario = Horario()

    for i in range(num_aulas):
        horario.adicionar(
            Aula(
                turma="t1",
                disciplina="d1",
                professor=f"p{i % 2 + 1}",
                sala=f"s{i % 2 + 1}",
                slot=slots[i % len(slots)],
            )
        )

    # Conta violações antes
    violacoes_antes = verificar_hard(horario, ctx)

    # Tenta mover cada aula com validar=True
    for aula in list(horario.aulas):
        for novo_slot in slots:
            if novo_slot == aula.slot:
                continue
            resultado = mover_aula(horario, aula, novo_slot, validar=True, ctx=ctx)

            # Conta violações depois
            violacoes_depois = verificar_hard(resultado, ctx)

            # Com validar=True, não deve haver MAIS violações do que antes
            assert len(violacoes_depois) <= len(violacoes_antes), (
                f"mover_aula com validar=True introduziu novas violações duras: "
                f"antes={len(violacoes_antes)}, depois={len(violacoes_depois)}, "
                f"depois={violacoes_depois}"
            )


# ---------------------------------------------------------------------------
# Propriedade P3: Score é consistente (determinístico)
# ---------------------------------------------------------------------------


@given(
    num_aulas=st.integers(min_value=0, max_value=10),
)
@settings(max_examples=100, deadline=None)
def test_score_eh_deterministico(num_aulas):
    """Avaliar o mesmo horário duas vezes produz o mesmo score."""

    ctx = ContextoRestricoes(
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
            "d1": Disciplina(identificador="d1", nome="Matemática", carga_semanal=4),
            "d2": Disciplina(identificador="d2", nome="Português", carga_semanal=4),
        },
        casamentos=[],
        relacoes_filho=[],
    )

    slots = [Slot(dia="segunda", hora=h) for h in range(1, 5)]
    horario = Horario()

    for i in range(num_aulas):
        horario.adicionar(
            Aula(
                turma=f"t{i % 2 + 1}",
                disciplina=f"d{i % 2 + 1}",
                professor=f"p{i % 2 + 1}",
                sala=f"s{i % 2 + 1}",
                slot=slots[i % len(slots)],
            )
        )

    av1 = avaliar(horario, ctx)
    av2 = avaliar(horario, ctx)

    assert av1.score == av2.score
    assert av1.viavel == av2.viavel
    assert av1.penalidades_moles == av2.penalidades_moles
    assert av1.violacoes_hard == av2.violacoes_hard


# ---------------------------------------------------------------------------
# Máquina de estado: propriedades invariantes
# ---------------------------------------------------------------------------


class MaquinaHorario(RuleBasedStateMachine):
    """Máquina de estado que testa propriedades invariantes de um horário."""

    def __init__(self):
        super().__init__()
        self.horario = Horario()
        self.ctx = ContextoRestricoes(
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
            },
            disciplinas={
                "d1": Disciplina(identificador="d1", nome="Matemática", carga_semanal=4),
            },
            casamentos=[],
            relacoes_filho=[],
        )
        self.slots = [Slot(dia="segunda", hora=h) for h in range(1, 4)]

    @rule(
        dia=st.sampled_from(["segunda", "terca", "quarta"]),
        hora=st.integers(min_value=1, max_value=3),
    )
    def adicionar_aula(self, dia, hora):
        """Adiciona uma aula aleatória ao horário (sem duplicar slot)."""

        slot = Slot(dia=dia, hora=hora)
        # Só adiciona se o slot ainda não está ocupado
        if not self.horario.professor_ocupado_em("p1", slot):
            self.horario.adicionar(
                Aula(
                    turma="t1",
                    disciplina="d1",
                    professor="p1",
                    sala="s1",
                    slot=slot,
                )
            )

    @rule()
    def nao_introduz_violacoes_duras(self):
        """Invariante: nunca deve haver violações duras com contexto vazio."""

        ctx_vazio = ContextoRestricoes(
            professores={},
            salas={},
            turmas={},
            disciplinas={},
            casamentos=[],
            relacoes_filho=[],
        )
        violacoes = verificar_hard(self.horario, ctx_vazio)
        assert len(violacoes) == 0, f"Violações duras inesperadas: {violacoes}"


TesteMaquinaHorario = MaquinaHorario.TestCase
