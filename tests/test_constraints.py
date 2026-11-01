"""Testes unitários para restrições duras e moles."""

from timetable.constraints import (
    ContextoRestricoes,
    PenalidadeMole,
    calcular_penalidades_moles,
    verificar_hard,
)
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


def _ctx_padrao() -> ContextoRestricoes:
    profs = {
        "p1": Professor(identificador="p1", nome="Prof. Um"),
        "p2": Professor(identificador="p2", nome="Prof. Dois"),
    }
    salas = {"s1": Sala(identificador="s1", capacidade=30)}
    turmas = {"t1": Turma(identificador="t1", ano=10, numero_alunos=25)}
    discs = {"m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=4)}
    return ContextoRestricoes(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=discs,
        casamentos=[],
        relacoes_filho=[],
    )


def test_viavel_sem_violacoes():
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
    violacoes = verificar_hard(h, _ctx_padrao())
    assert violacoes == []


def test_h01_professor_duplicado():
    h = Horario()
    slot = Slot(dia="segunda", hora=1)
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=slot))
    h.adicionar(Aula(turma="t2", disciplina="m1", professor="p1", sala="s2", slot=slot))
    violacoes = verificar_hard(h, _ctx_padrao())
    assert any("H01" in v for v in violacoes)


def test_h02_sala_duplicada():
    h = Horario()
    slot = Slot(dia="segunda", hora=1)
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=slot))
    h.adicionar(Aula(turma="t2", disciplina="m1", professor="p2", sala="s1", slot=slot))
    violacoes = verificar_hard(h, _ctx_padrao())
    assert any("H02" in v for v in violacoes)


def test_h03_turma_duplicada():
    h = Horario()
    slot = Slot(dia="segunda", hora=1)
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=slot))
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p2", sala="s2", slot=slot))
    violacoes = verificar_hard(h, _ctx_padrao())
    assert any("H03" in v for v in violacoes)


def test_h07_casados_mesma_turma():
    ctx = _ctx_padrao()
    ctx.casamentos = [RelacaoCasamento(professor_a="p1", professor_b="p2")]
    # Precisamos de turma t2 no contexto
    ctx.turmas["t2"] = Turma(identificador="t2", ano=10, numero_alunos=25)
    h = Horario()
    slot = Slot(dia="segunda", hora=1)
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=slot))
    h.adicionar(Aula(turma="t1", disciplina="m1", professor="p2", sala="s2", slot=slot))
    violacoes = verificar_hard(h, ctx)
    assert any("H07" in v for v in violacoes)


def test_h08_filho_na_turma_dos_pais():
    ctx = _ctx_padrao()
    ctx.relacoes_filho = [
        RelacaoFilho(
            professor_pai="p1",
            professor_mae="p2",
            identificador_turma_filho="t1",
        )
    ]
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
    violacoes = verificar_hard(h, ctx)
    assert any("H08" in v for v in violacoes)


def test_penalidades_moles_vazio_quando_sem_aulas():
    penalidades = calcular_penalidades_moles(Horario(), _ctx_padrao())
    assert penalidades == []


def test_penalidade_tipo():
    p = PenalidadeMole(id_restricao="S01", descricao="teste", valor=10)
    assert p.valor == 10


# --- S04: disciplinas não espalhadas pela semana ---


def test_s04_todas_aulas_num_unico_dia():
    """S04: turma com todas as aulas de uma disciplina num único dia (>=2 aulas)."""

    ctx = _ctx_padrao()
    ctx.turmas["t2"] = Turma(identificador="t2", ano=10, numero_alunos=25)
    h = Horario()
    # Duas aulas de Matemática para t1, ambas na segunda-feira
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=2)
        )
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S04" for p in penalidades)


def test_s04_aulas_espalhadas_sem_penalidade():
    """S04: aulas espalhadas por múltiplos dias não penalizam."""

    ctx = _ctx_padrao()
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="terca", hora=1))
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S04" for p in penalidades)


# --- S05: padrão A-B-C-A ---


def test_s05_padrao_interrompido():
    """S05: padrão A-B-C-A (mesma disciplina interrompida por duas outras)."""

    ctx = _ctx_padrao()
    ctx.disciplinas["p1"] = Disciplina(identificador="p1", nome="Português", carga_semanal=1)
    ctx.disciplinas["i1"] = Disciplina(identificador="i1", nome="Inglês", carga_semanal=1)
    h = Horario()
    # Segunda-feira: Matemática (1h), Português (2h), Inglês (3h), Matemática (4h) → padrão A-B-C-A
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="p1", professor="p2", sala="s2", slot=Slot(dia="segunda", hora=2)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="i1", professor="p3", sala="s3", slot=Slot(dia="segunda", hora=3)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=4)
        )
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S05" for p in penalidades)


def test_s05_sem_padrao_interrompido():
    """S05: sem padrão A-B-A não penaliza."""

    ctx = _ctx_padrao()
    ctx.disciplinas["p1"] = Disciplina(identificador="p1", nome="Português", carga_semanal=1)
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=2)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="p1", professor="p2", sala="s2", slot=Slot(dia="segunda", hora=3)
        )
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S05" for p in penalidades)


# --- S06: falta de duas horas consecutivas para avaliação ---


def test_s06_sem_bloco_consecutivo():
    """S06: professor com carga >= 4 e sem bloco de 2h consecutivas."""

    ctx = _ctx_padrao()
    ctx.professores["p1"] = Professor(
        identificador="p1", nome="Prof. Um", carga_maxima_semanal=30, carga_minima_semanal=4
    )
    h = Horario()
    # Duas aulas não consecutivas na mesma dia
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=3)
        )
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S06" for p in penalidades)


def test_s06_com_bloco_consecutivo():
    """S06: professor com bloco de 2h consecutivas não penaliza."""

    ctx = _ctx_padrao()
    ctx.professores["p1"] = Professor(
        identificador="p1", nome="Prof. Um", carga_maxima_semanal=30, carga_minima_semanal=4
    )
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=2)
        )
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S06" for p in penalidades)


# --- S07: carga horária fora dos limites ---


def test_s07_carga_abaixo_minimo():
    """S07: professor com menos aulas que o mínimo."""

    ctx = _ctx_padrao()
    ctx.professores["p1"] = Professor(
        identificador="p1", nome="Prof. Um", carga_maxima_semanal=30, carga_minima_semanal=10
    )
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S07" for p in penalidades)


def test_s07_carga_acima_maximo():
    """S07: professor com mais aulas que o máximo."""

    ctx = _ctx_padrao()
    ctx.professores["p1"] = Professor(
        identificador="p1", nome="Prof. Um", carga_maxima_semanal=2, carga_minima_semanal=1
    )
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=2)
        )
    )
    h.adicionar(
        Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="terca", hora=1))
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S07" for p in penalidades)


def test_s07_carga_dentro_limites():
    """S07: carga dentro dos limites não penaliza."""

    ctx = _ctx_padrao()
    ctx.professores["p1"] = Professor(
        identificador="p1", nome="Prof. Um", carga_maxima_semanal=10, carga_minima_semanal=2
    )
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="segunda", hora=1)
        )
    )
    h.adicionar(
        Aula(turma="t1", disciplina="m1", professor="p1", sala="s1", slot=Slot(dia="terca", hora=1))
    )
    penalidades = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S07" for p in penalidades)
