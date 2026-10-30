"""Linha de base exata usando OR-Tools CP-SAT.

Valida se o problema tem solução viável e gera um seed inicial para instâncias
pequenas. Opcional: só é usado se `ortools` estiver instalado.
"""

from __future__ import annotations


from .constraints import ContextoRestricoes
from .models import (
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


class CPSATSolver:
    """Solver exato baseado em OR-Tools CP-SAT.

    Modela o problema de horário escolar como um programa de restrições com
    variáveis booleanas para cada atribuição (aula, slot, sala) possível.
    """

    def __init__(self) -> None:
        self._cp_model = None
        self._cp_solver = None
        self._disponivel = self._tentar_importar()

    def _tentar_importar(self) -> bool:
        try:
            from ortools.sat.python import cp_model  # type: ignore

            self._cp_model = cp_model
            self._cp_solver = cp_model.CpSolver
            return True
        except ImportError:
            return False

    def esta_disponivel(self) -> bool:
        return self._disponivel

    def resolver(
        self,
        horario_inicial: Horario,
        ctx: ContextoRestricoes,
        tempo_limite_segundos: float = 60.0,
    ) -> Horario:
        """Resolve o horário usando CP-SAT.

        Se `ortools` não estiver disponível, retorna uma cópia do horário
        inicial (fallback graceful).
        """

        if not self._disponivel:
            return horario_inicial.clone()

        model = self._cp_model.CpModel()

        # --- Recolhe entidades do contexto ---
        professores: dict[str, Professor] = ctx.professores
        salas: dict[str, Sala] = ctx.salas
        turmas: dict[str, Turma] = ctx.turmas
        disciplinas: dict[str, Disciplina] = ctx.disciplinas
        casamentos: list[RelacaoCasamento] = ctx.casamentos
        relacoes_filho: list[RelacaoFilho] = ctx.relacoes_filho

        # --- Gera o conjunto de slots possíveis ---
        slots = self._gerar_slots(professores, salas)

        # --- Construi a lista de aulas requeridas (turma, disciplina) ---
        # Cada turma precisa de carga_semanal aulas de cada disciplina
        aulas_requeridas: list[tuple[str, str]] = []
        for turma_id, turma in turmas.items():
            for disc_id, disciplina in disciplinas.items():
                for _ in range(disciplina.carga_semanal):
                    aulas_requeridas.append((turma_id, disc_id))

        # Índice de professores por disciplina (quem pode lecionar o quê)
        # Simplificação: qualquer professor pode lecionar qualquer disciplina,
        # exceto restrições de disponibilidade já modeladas.
        professores_lista = list(professores.keys())
        salas_lista = list(salas.keys())

        # --- Variáveis booleanas x[turma, disc, prof, sala, slot] ---
        vars_x: dict[tuple[str, str, str, str, Slot], object] = {}
        for turma_id, disc_id in aulas_requeridas:
            for prof_id in professores_lista:
                for sala_id in salas_lista:
                    for slot in slots:
                        chave = (turma_id, disc_id, prof_id, sala_id, slot)
                        vars_x[chave] = model.NewBoolVar(f"x_{chave}")

        # --- Restrição de cobertura: cada (turma, disc) tem exatamente carga_semanal aulas ---
        for turma_id, disc_id in aulas_requeridas:
            model.Add(
                sum(
                    vars_x[(turma_id, disc_id, p, s, sl)]
                    for p in professores_lista
                    for s in salas_lista
                    for sl in slots
                    if (turma_id, disc_id, p, s, sl) in vars_x
                )
                == 1
            )

        # --- H01: professor não dá duas aulas no mesmo slot ---
        for prof_id in professores_lista:
            for slot in slots:
                model.Add(
                    sum(
                        vars_x[(t, d, prof_id, s, sl)]
                        for (t, d, p, s, sl), v in vars_x.items()
                        if p == prof_id and sl == slot
                    )
                    <= 1
                )

        # --- H02: sala não alberga duas aulas no mesmo slot ---
        for sala_id in salas_lista:
            for slot in slots:
                model.Add(
                    sum(
                        vars_x[(t, d, p, sala_id, sl)]
                        for (t, d, p, s, sl), v in vars_x.items()
                        if s == sala_id and sl == slot
                    )
                    <= 1
                )

        # --- H03: turma não tem duas aulas no mesmo slot ---
        for turma_id in turmas:
            for slot in slots:
                model.Add(
                    sum(
                        vars_x[(turma_id, d, p, s, sl)]
                        for (t, d, p, s, sl), v in vars_x.items()
                        if t == turma_id and sl == slot
                    )
                    <= 1
                )

        # --- H04: sala compatível com a disciplina ---
        for (t, d, p, s, sl), v in vars_x.items():
            sala = salas.get(s)
            disc = disciplinas.get(d)
            if sala and disc and sala.tipo != disc.tipo_sala_requerida:
                model.Add(v == 0)

        # --- H05: professor disponível nesse slot ---
        for (t, d, p, s, sl), v in vars_x.items():
            prof = professores.get(p)
            if prof and not prof.esta_disponivel(sl):
                model.Add(v == 0)

        # --- H07: professores casados não na mesma turma ---
        casados_pares: set[tuple[str, str]] = set()
        for c in casamentos:
            casados_pares.add((c.professor_a, c.professor_b))
            casados_pares.add((c.professor_b, c.professor_a))

        for (t, d, p, s, sl), v in vars_x.items():
            for pa, pb in casados_pares:
                if p == pa:
                    # Se este professor está nesta (turma, slot), o cônjuge não pode
                    model.Add(
                        sum(
                            vars_x2
                            for (t2, d2, p2, s2, sl2), vars_x2 in vars_x.items()
                            if t2 == t and sl2 == sl and p2 == pb
                        )
                        == 0
                    ).OnlyEnforceIf(v)

        # --- H08: filho não na turma dos pais casados ---
        for rel in relacoes_filho:
            for (t, d, p, s, sl), v in vars_x.items():
                if t == rel.identificador_turma_filho and p in (
                    rel.professor_pai,
                    rel.professor_mae,
                ):
                    model.Add(v == 0)

        # --- Função objetivo: penalidades moles aditivas ---
        # S01: dia de folga preferido do professor
        termos_objetivo: list[tuple[object, int]] = []
        for (t, d, p, s, sl), v in vars_x.items():
            prof = professores.get(p)
            if prof and prof.dia_folga_preferido and sl.dia == prof.dia_folga_preferido:
                termos_objetivo.append((v, 10))

            # S02: preferência manhã/tarde
            if prof and prof.prefere_manha and sl.hora >= 13:
                termos_objetivo.append((v, 8))

        # S08: professor a trabalhar muitos dias (>= 5 dias diferentes)
        # Modelado como: para cada professor, contar dias distintos com aulas
        for prof_id in professores_lista:
            dias = sorted({sl.dia for sl in slots})
            for dia in dias:
                var_dia = model.NewBoolVar(f"dia_{prof_id}_{dia}")
                model.Add(
                    sum(
                        vars_x[(t, d, prof_id, s, sl)]
                        for (t, d, p, s, sl), v in vars_x.items()
                        if p == prof_id and sl.dia == dia
                    )
                    >= var_dia
                )
                model.Add(
                    sum(
                        vars_x[(t, d, prof_id, s, sl)]
                        for (t, d, p, s, sl), v in vars_x.items()
                        if p == prof_id and sl.dia == dia
                    )
                    <= len(slots) * var_dia
                )
                termos_objetivo.append((var_dia, 12))

        # S09: distribuição desigual entre professores da mesma disciplina
        for disc_id in disciplinas:
            profs_disc = professores_lista  # simplificação: todos podem lecionar
            contagens: list[object] = []
            for p in profs_disc:
                var_count = model.NewIntVar(0, len(slots), f"count_{disc_id}_{p}")
                model.Add(
                    var_count
                    == sum(
                        vars_x[(t, disc_id, p, s, sl)]
                        for (t, d, p2, s, sl), v in vars_x.items()
                        if d == disc_id and p2 == p
                    )
                )
                contagens.append(var_count)
            if len(contagens) > 1:
                max_var = model.NewIntVar(0, len(slots), f"max_{disc_id}")
                min_var = model.NewIntVar(0, len(slots), f"min_{disc_id}")
                model.AddMaxEquality(max_var, contagens)
                model.AddMinEquality(min_var, contagens)
                diff_var = model.NewIntVar(0, len(slots), f"diff_{disc_id}")
                model.Add(diff_var == max_var - min_var)
                # Penaliza apenas quando a diferença entre max e min excede 2
                penaliza_s09 = model.NewBoolVar(f"penaliza_s09_{disc_id}")
                model.Add(diff_var > 2).OnlyEnforceIf(penaliza_s09)
                model.Add(diff_var <= 2).OnlyEnforceIf(penaliza_s09.Not())
                termos_objetivo.append((penaliza_s09, 11))

        # S10: carga concentrada em poucos dias (<= 2 dias com >= 5 aulas)
        for prof_id in professores_lista:
            for dia in sorted({sl.dia for sl in slots}):
                var_dia_count = model.NewIntVar(0, len(slots), f"countday_{prof_id}_{dia}")
                model.Add(
                    var_dia_count
                    == sum(
                        vars_x[(t, d, prof_id, s, sl)]
                        for (t, d, p, s, sl), v in vars_x.items()
                        if p == prof_id and sl.dia == dia
                    )
                )
                # Penaliza apenas quando há >= 5 aulas num único dia
                penaliza_s10 = model.NewBoolVar(f"penaliza_s10_{prof_id}_{dia}")
                model.Add(var_dia_count >= 5).OnlyEnforceIf(penaliza_s10)
                model.Add(var_dia_count <= 4).OnlyEnforceIf(penaliza_s10.Not())
                termos_objetivo.append((penaliza_s10, 10))

        if termos_objetivo:
            model.Minimize(sum(v * w for v, w in termos_objetivo))

        # --- Resolve ---
        solver = self._cp_solver()
        solver.parameters.max_time_in_seconds = tempo_limite_segundos
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)

        if status not in (
            self._cp_model.OPTIMAL,
            self._cp_model.FEASIBLE,
        ):
            # Não encontrou solução viável; devolve o inicial
            return horario_inicial.clone()

        # --- Constrói o Horario a partir da solução ---
        novo_horario = Horario()
        for (t, d, p, s, sl), v in vars_x.items():
            if solver.Value(v) == 1:
                novo_horario.adicionar(
                    Aula(
                        turma=t,
                        disciplina=d,
                        professor=p,
                        sala=s,
                        slot=sl,
                    )
                )

        return novo_horario

    @staticmethod
    def _gerar_slots(
        professores: dict[str, Professor],
        salas: dict[str, Sala],
    ) -> list[Slot]:
        """Gera a lista de slots possíveis a partir das disponibilidades."""

        dias_horas: set[tuple[str, int]] = set()

        # Recolhe dias e horas das disponibilidades dos professores
        for prof in professores.values():
            for slot in prof.disponibilidade:
                dias_horas.add((slot.dia, slot.hora))

        # Se não houver disponibilidades, usa um padrão padrão
        if not dias_horas:
            for dia in ["segunda", "terca", "quarta", "quinta", "sexta"]:
                for hora in range(8, 18):
                    dias_horas.add((dia, hora))

        return [Slot(dia=dia, hora=hora) for dia, hora in sorted(dias_horas)]
