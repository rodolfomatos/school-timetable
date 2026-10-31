"""Testes da camada de domínio canónica (T051)."""

from __future__ import annotations


from timetable.domain import (
    Diagnostico,
    EntradaCurricular,
    ProblemInstance,
    construir_problema,
)
from timetable.models import (
    Disciplina,
    Professor,
    Sala,
    Slot,
    Subgrupo,
    Turma,
)


def _professor(id_: str, **kwargs) -> Professor:
    return Professor(identificador=id_, nome=f"Prof. {id_}", **kwargs)


def _turma(id_: str, alunos: int = 25, **kwargs) -> Turma:
    return Turma(identificador=id_, ano=1, numero_alunos=alunos, **kwargs)


def _disciplina(id_: str, carga: int = 2, tipo: str = "normal", **kwargs) -> Disciplina:
    return Disciplina(identificador=id_, nome=f"Disc. {id_}", carga_semanal=carga, tipo_sala_requerida=tipo, **kwargs)


def _sala(id_: str, cap: int = 30, tipo: str = "normal", **kwargs) -> Sala:
    return Sala(identificador=id_, capacidade=cap, tipo=tipo, **kwargs)


def test_construir_problema_sucesso_sem_diagnosticos() -> None:
    """Currículo válido produz instância sem erros."""

    profs = {
        "P1": _professor("P1", qualificacoes={"D1"}, qualificacoes_definidas=True),
        "P2": _professor("P2", qualificacoes={"D2"}, qualificacoes_definidas=True),
    }
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1"), "D2": _disciplina("D2")}

    curriculo = [
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",)),
        EntradaCurricular("T1", "D2", professores_elegiveis=("P2",)),
    ]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    assert not prob.tem_erros
    assert len(prob.sessoes) == 4  # 2 disciplinas × 2 aulas/semana
    assert all(s.professores_elegiveis for s in prob.sessoes)


def test_construir_problema_sem_professor_elegivel() -> None:
    """Disciplina sem docente qualificado gera ERROR."""

    profs = {"P1": _professor("P1", qualificacoes={"D1"}, qualificacoes_definidas=True)}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D2": _disciplina("D2")}  # P1 não qualificado

    curriculo = [EntradaCurricular("T1", "D2", professores_elegiveis=("P1",))]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    assert prob.tem_erros
    assert any(d.codigo == "SEM_PROFESSOR_ELEGIVEL" for d in prob.diagnosticos)


def test_construir_problema_sem_sala_compativel() -> None:
    """Sala de tipo errado ou capacidade insuficiente gera ERROR."""

    profs = {"P1": _professor("P1", qualificacoes={"D1"}, qualificacoes_definidas=True)}
    salas = {"S1": _sala("S1", cap=10, tipo="laboratorio")}  # cap < 25, tipo != normal
    turmas = {"T1": _turma("T1", alunos=25)}
    disciplinas = {"D1": _disciplina("D1", tipo="normal")}

    curriculo = [EntradaCurricular("T1", "D1", professores_elegiveis=("P1",))]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    assert prob.tem_erros
    assert any(d.codigo == "SEM_SALA_COMPATIVEL" for d in prob.diagnosticos)


def test_construir_problema_turma_inexistente() -> None:
    """Turma referida no currículo mas inexistente gera ERROR."""

    profs = {"P1": _professor("P1", qualificacoes={"D1"}, qualificacoes_definidas=True)}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1")}

    curriculo = [EntradaCurricular("T_INEXISTENTE", "D1", professores_elegiveis=("P1",))]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    assert prob.tem_erros
    assert any(d.codigo == "TURMA_INEXISTENTE" for d in prob.diagnosticos)


def test_construir_problema_disciplina_inexistente() -> None:
    """Disciplina referida no currículo mas inexistente gera ERROR."""

    profs = {"P1": _professor("P1", qualificacoes={"D1"}, qualificacoes_definidas=True)}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1")}

    curriculo = [EntradaCurricular("T1", "D_INEXISTENTE", professores_elegiveis=("P1",))]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    assert prob.tem_erros
    assert any(d.codigo == "DISCIPLINA_INEXISTENTE" for d in prob.diagnosticos)


def test_construir_problema_curriculo_vazio() -> None:
    """Currículo vazio gera ERROR."""

    profs = {"P1": _professor("P1")}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1")}

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=[],
    )

    assert prob.tem_erros
    assert any(d.codigo == "CURRICULO_VAZIO" for d in prob.diagnosticos)


def test_construir_problema_subgrupo_invalido() -> None:
    """Subgrupo que não pertence à turma gera ERROR."""

    profs = {"P1": _professor("P1", qualificacoes={"D1"}, qualificacoes_definidas=True)}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1")}
    subgrupos = {"SG1": Subgrupo(identificador="SG1", turma_pai="OUTRA", nome="G1", numero_alunos=10)}

    curriculo = [
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",), subgrupo_id="SG1")
    ]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
        subgrupos=subgrupos,
    )

    assert prob.tem_erros
    assert any(d.codigo == "SUBGRUPO_INVALIDO" for d in prob.diagnosticos)


def test_construir_problema_indisponibilidades_aplicadas() -> None:
    """Indisponibilidades persistidas e adicionais são subtraídas da disponibilidade."""

    slots = [Slot(dia="segunda", hora=8), Slot(dia="segunda", hora=9)]
    profs = {
        "P1": _professor(
            "P1",
            qualificacoes={"D1"},
            qualificacoes_definidas=True,
            disponibilidade=frozenset(slots),
        )
    }
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1")}

    curriculo = [EntradaCurricular("T1", "D1", professores_elegiveis=("P1",))]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
        indisponibilidades={"P1": [Slot(dia="segunda", hora=8)]},
    )

    assert not prob.tem_erros
    assert len(prob.professores["P1"].disponibilidade) == 1
    assert Slot(dia="segunda", hora=9) in prob.professores["P1"].disponibilidade


def test_construir_problema_qualificacoes_nao_definidas_legacy() -> None:
    """Sem qualificações definidas, assume-se todas (compatibilidade)."""

    profs = {"P1": _professor("P1")}  # sem qualificacoes_definidas
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1")}

    curriculo = [EntradaCurricular("T1", "D1")]  # sem professores_elegiveis

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    # Warning, não error - compatibilidade legada
    assert not prob.tem_erros
    assert any(d.codigo == "DISPONIBILIDADE_NAO_ESPECIFICADA" for d in prob.diagnosticos)
    assert "P1" in prob.sessoes[0].professores_elegiveis


def test_construir_problema_curriculo_duplicado() -> None:
    """Duplicata de relação curricular gera ERROR."""

    profs = {"P1": _professor("P1", qualificacoes={"D1"}, qualificacoes_definidas=True)}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disciplina("D1")}

    curriculo = [
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",)),
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",)),
    ]

    prob = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    assert prob.tem_erros
    assert any(d.codigo == "CURRICULO_DUPLICADO" for d in prob.diagnosticos)


def test_problema_para_contexto_preserva_dados() -> None:
    """``para_contexto`` devolve ContextoRestricoes com todos os campos."""

    prob = ProblemInstance(
        professores={"P1": _professor("P1")},
        salas={"S1": _sala("S1")},
        turmas={"T1": _turma("T1")},
        disciplinas={"D1": _disciplina("D1")},
        diagnosticos=[],
    )
    ctx = prob.para_contexto()
    assert ctx.professores["P1"].identificador == "P1"
    assert ctx.salas["S1"].identificador == "S1"
    assert ctx.turmas["T1"].identificador == "T1"
    assert ctx.disciplinas["D1"].identificador == "D1"
    assert ctx.sessoes_requeridas == []


def test_diagnostico_dict_serializavel() -> None:
    """``diagnosticos_dict`` é JSON-serializável."""

    prob = ProblemInstance(
        professores={},
        salas={},
        turmas={},
        disciplinas={},
        diagnosticos=[Diagnostico("COD", "ERROR", "msg", ("e1",))],
    )
    d = prob.diagnosticos_dict()
    assert d[0]["codigo"] == "COD"
    assert d[0]["severidade"] == "ERROR"
    assert d[0]["entidades"] == ["e1"]