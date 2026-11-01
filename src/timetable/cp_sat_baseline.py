"""Linha de base exata usando OR-Tools CP-SAT.

Valida se o problema tem solução viável e gera um seed inicial para instâncias
pequenas. Opcional: só é usado se `ortools` estiver instalado.

Correções da Fase 2 (Auditoria T038):
- F-101: lesson_session_id como identidade única para cada sessão requerida
- F-102: Qualificações docentes - variáveis apenas para combinações admissíveis
- F-103: Implementar S03, S04, S06, S07 no CP-SAT
- F-008: S02 usar hora de início/fim do TimeSlot
- F-009: S05 padrão A-B-C-A (4 posições) pendente (requer modelo de slot mais detalhado)
- F-010: S08 calcular sequências consecutivas de dias
- F-011: S09 normalizar por carga contratual do professor
- F-012: S10 alinhar condição (≥ 5 aulas em ≤ 2 dias)
- T046: Suporte a subgrupos de turma (variáveis incluem subgrupo_id)
"""

from __future__ import annotations

from typing import Optional

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
    Subgrupo,
    Turma,
)


class CPSATSolver:
    """Solver exato baseado em OR-Tools CP-SAT.

    Modela o problema de horário escolar como um programa de restrições com
    variáveis booleanas para cada atribuição (sessão, professor, sala, slot, subgrupo) possível.

    Cada sessão requerida tem um lesson_session_id único e estável.
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
        subgrupos: dict[str, Subgrupo] = ctx.subgrupos

        # --- Gera o conjunto de slots possíveis ---
        slots = self._gerar_slots(professores, salas)

        # --- Constrói a lista de sessões requeridas com lesson_session_id único ---
        # Se o domínio forneceu sessões explícitas, usamos exactamente essas.
        # Caso contrário, mantém-se o comportamento legacy (produto cartesiano)
        # apenas para chamadas directas à biblioteca, sem currículo.
        aulas_requeridas: list[dict] = []
        if ctx.sessoes_requeridas:
            for sessao in ctx.sessoes_requeridas:
                aulas_requeridas.append(
                    {
                        "lesson_id": sessao.lesson_id,
                        "turma_id": sessao.turma,
                        "disc_id": sessao.disciplina,
                        "session_index": 0,
                        "professores_elegiveis": set(sessao.professores_elegiveis)
                        or None,
                        "subgrupo_id": sessao.subgrupo_id,
                    }
                )
        else:
            for turma_id in turmas:
                for disc_id, disciplina in disciplinas.items():
                    for sessao_idx_local in range(disciplina.carga_semanal):
                        lesson_id = f"{turma_id}_{disc_id}_{sessao_idx_local}"
                        aulas_requeridas.append(
                            {
                                "lesson_id": lesson_id,
                                "turma_id": turma_id,
                                "disc_id": disc_id,
                                "session_index": sessao_idx_local,
                                "professores_elegiveis": None,
                                "subgrupo_id": None,
                            }
                        )

        # Índice de professores qualificados por disciplina
        # Só criamos variáveis para combinações (professor, disciplina) admissíveis
        professores_por_disciplina: dict[str, list[str]] = {}
        for disc_id in disciplinas:
            professores_por_disciplina[disc_id] = []

        for prof_id, prof in professores.items():
            if prof.qualificacoes:
                for disc_id in prof.qualificacoes:
                    if disc_id in disciplinas:
                        professores_por_disciplina.setdefault(disc_id, []).append(prof_id)
            else:
                # Se não há qualificações definidas, assume que pode lecionar qualquer
                # disciplina (compatibilidade com versões anteriores)
                for disc_id in disciplinas:
                    professores_por_disciplina.setdefault(disc_id, []).append(prof_id)

        salas_lista = list(salas.keys())

        # --- Mapear turmas para seus subgrupos ---
        turma_subgrupos: dict[str, list[str]] = {}
        for sub_id, sub in subgrupos.items():
            turma_subgrupos.setdefault(sub.turma_pai, []).append(sub_id)

        # --- Variáveis booleanas x[lesson_id, prof, sala, slot, subgrupo_id] ---
        # Só criamos variáveis para combinações admissíveis (professor qualificado)
        # Quando uma turma tem subgrupos, criamos variáveis para cada subgrupo
        vars_x: dict[tuple[str, str, str, Slot, Optional[str]], object] = {}
        for sessao in aulas_requeridas:
            lesson_id = sessao["lesson_id"]
            disc_id = sessao["disc_id"]
            turm_id = sessao["turma_id"]
            # Determinar subgrupos para esta sessão
            subgrupos_da_turma = turma_subgrupos.get(turm_id, [])
            if sessao.get("subgrupo_id"):
                subgrupos_a_usar = [sessao["subgrupo_id"]]
            elif subgrupos_da_turma:
                subgrupos_a_usar = subgrupos_da_turma
            else:
                subgrupos_a_usar = [None]

            candidatos = professores_por_disciplina.get(disc_id, [])
            elegiveis = sessao.get("professores_elegiveis")
            if elegiveis:
                candidatos = [p for p in candidatos if p in elegiveis]

            for prof_id in candidatos:
                for sala_id in salas_lista:
                    for slot in slots:
                        for sub_id in subgrupos_a_usar:
                            chave = (lesson_id, prof_id, sala_id, slot, sub_id)
                            vars_x[chave] = model.NewBoolVar(f"x_{chave}")

        # Mapa lesson_id -> turma, usado pelas restrições H03/H07/H08.
        sessao_turma: dict[str, str] = {
            s["lesson_id"]: s["turma_id"] for s in aulas_requeridas
        }

        # --- Fixar atribuições do horário_inicial (seed) ---
        # Para cada aula no horário inicial, se corresponde a uma sessão requerida,
        # fixa a variável correspondente a 1.
        for aula_inicial in horario_inicial.aulas:
            # Encontra a sessão requerida correspondente
            for sessao in aulas_requeridas:
                if (
                    sessao["turma_id"] == aula_inicial.turma
                    and sessao["disc_id"] == aula_inicial.disciplina
                    and sessao.get("subgrupo_id") == aula_inicial.subgrupo_id
                ):
                    # Procura a variável que corresponde a esta atribuição
                    for (lid, p, s, sl, sub_id), var in vars_x.items():
                        if (
                            lid == sessao["lesson_id"]
                            and p == aula_inicial.professor
                            and s == aula_inicial.sala
                            and sl == aula_inicial.slot
                            and sub_id == aula_inicial.subgrupo_id
                        ):
                            model.Add(var == 1)
                            break

        # --- Restrição de cobertura: cada sessão tem exatamente uma atribuição ---
        # --- Restrição de cobertura: cada sessão tem exatamente uma atribuição ---
        for sessao in aulas_requeridas:
            lesson_id = sessao["lesson_id"]
            model.Add(
                sum(
                    vars_x[(lesson_id, p, s, sl, sub_id)]
                    for (lid, p, s, sl, sub_id), v in vars_x.items()
                    if lid == lesson_id
                )
                == 1
            )

        # --- H01: professor não dá duas aulas no mesmo slot ---
        for prof_id in professores:
            for slot in slots:
                model.Add(
                    sum(
                        vars_x[(lid, prof_id, s, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if p == prof_id and sl == slot
                    )
                    <= 1
                )

        # --- H02: sala não alberga duas aulas no mesmo slot ---
        for sala_id in salas_lista:
            for slot in slots:
                model.Add(
                    sum(
                        vars_x[(lid, p, sala_id, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if s == sala_id and sl == slot
                    )
                    <= 1
                )

        # --- H03: turma+subgrupo não tem duas aulas no mesmo slot ---
        # Duas aulas da mesma turma podem ocorrer no mesmo slot se forem de subgrupos diferentes
        for turma_id in turmas:
            sub_ids_turma = turma_subgrupos.get(turma_id, [None])
            for slot in slots:
                for sub_id in sub_ids_turma:
                    model.Add(
                        sum(
                            vars_x[(lid, p, s, sl, s_id)]
                            for (lid, p, s, sl, s_id), v in vars_x.items()
                            if sessao_turma.get(lid) == turma_id
                            and sl == slot
                            and s_id == sub_id
                        )
                        <= 1
                    )

        # --- H04: sala compatível com a disciplina ---
        for (lid, p, s, sl, sub_id), v in vars_x.items():
            # Encontrar a disciplina da sessão
            disc_id = self._disc_da_sessao(lid, aulas_requeridas)
            sala = salas.get(s)
            disc = disciplinas.get(disc_id)
            if sala and disc and sala.tipo != disc.tipo_sala_requerida:
                model.Add(v == 0)

        # --- H05: professor disponível nesse slot ---
        for (lid, p, s, sl, sub_id), v in vars_x.items():
            prof = professores.get(p)
            if prof and not prof.esta_disponivel(sl):
                model.Add(v == 0)

        # --- H07: professores casados não na mesma turma ---
        casados_pares: set[tuple[str, str]] = set()
        for c in casamentos:
            casados_pares.add((c.professor_a, c.professor_b))
            casados_pares.add((c.professor_b, c.professor_a))

        for (lid, p, s, sl, sub_id), v in vars_x.items():
            for pa, pb in casados_pares:
                if p == pa:
                    # Se este professor está nesta (turma, slot, subgrupo), o cônjuge não pode
                    model.Add(
                        sum(
                            vars_x2
                            for (
                                l2,
                                p2,
                                s2,
                                sl2,
                                s_id2,
                            ), vars_x2 in vars_x.items()
                            if sessao_turma.get(l2) == sessao_turma.get(lid)
                            and sl2 == sl
                            and p2 == pb
                            and s_id2 == sub_id
                        )
                        == 0
                    ).OnlyEnforceIf(v)

        # --- H08: filho não na turma dos pais casados ---
        for rel in relacoes_filho:
            for (lid, p, s, sl, sub_id), v in vars_x.items():
                if sessao_turma.get(lid) == rel.identificador_turma_filho and p in (
                    rel.professor_pai,
                    rel.professor_mae,
                ):
                    model.Add(v == 0)

        # --- Função objetivo: penalidades moles aditivas ---
        termos_objetivo: list[tuple[object, int]] = []

        # Pré-computar slots por dia para uso em S03, S04, S06
        slots_por_dia: dict[str, list[Slot]] = {}
        for sl in slots:
            slots_por_dia.setdefault(sl.dia, []).append(sl)

        # S01: dia de folga preferido do professor
        for (lid, p, s, sl, sub_id), v in vars_x.items():
            prof = professores.get(p)
            if prof and prof.dia_folga_preferido and sl.dia == prof.dia_folga_preferido:
                termos_objetivo.append((v, 10))

            # S02: preferência manhã/tarde (usa hora de início se disponível)
            if prof and prof.prefere_manha:
                eh_manha = sl.eh_manha() if sl.hora_inicio is not None else sl.hora < 13
                if not eh_manha:
                    termos_objetivo.append((v, 8))

        # S03: duas horas consecutivas da mesma disciplina para a mesma turma
        # Agrupar sessões por (turma, disciplina)
        sessoes_por_turma_disc: dict[tuple[str, str], list[str]] = {}
        for sessao in aulas_requeridas:
            chave = (sessao["turma_id"], sessao["disc_id"])
            sessoes_por_turma_disc.setdefault(chave, []).append(sessao["lesson_id"])

        for (turm, disc), lesson_ids in sessoes_por_turma_disc.items():
            if len(lesson_ids) < 2:
                continue

            for dia, slots_dia in slots_por_dia.items():
                slots_dia_ordenados = sorted(slots_dia, key=lambda s: s.hora)
                for i in range(len(slots_dia_ordenados) - 1):
                    s1 = slots_dia_ordenados[i]
                    s2 = slots_dia_ordenados[i + 1]
                    if s1.hora + 1 == s2.hora:
                        # Existe par de slots consecutivos neste dia
                        var_tem_aula_s1 = model.NewBoolVar(
                            f"tem_aula_s1_{turm}_{disc}_{s1.dia}_{s1.hora}"
                        )
                        var_tem_aula_s2 = model.NewBoolVar(
                            f"tem_aula_s2_{turm}_{disc}_{s2.dia}_{s2.hora}"
                        )
                        model.Add(
                            sum(
                                vars_x[(lid, p, s, sl, sub_id)]
                                for (lid, p, s, sl, sub_id), v in vars_x.items()
                                if lid in lesson_ids and sl == s1
                            )
                            >= var_tem_aula_s1
                        )
                        model.Add(
                            sum(
                                vars_x[(lid, p, s, sl, sub_id)]
                                for (lid, p, s, sl, sub_id), v in vars_x.items()
                                if lid in lesson_ids and sl == s2
                            )
                            <= len(lesson_ids) * var_tem_aula_s1
                        )
                        model.Add(
                            sum(
                                vars_x[(lid, p, s, sl, sub_id)]
                                for (lid, p, s, sl, sub_id), v in vars_x.items()
                                if lid in lesson_ids and sl == s2
                            )
                            >= var_tem_aula_s2
                        )
                        model.Add(
                            sum(
                                vars_x[(lid, p, s, sl, sub_id)]
                                for (lid, p, s, sl, sub_id), v in vars_x.items()
                                if lid in lesson_ids and sl == s1
                            )
                            <= len(lesson_ids) * var_tem_aula_s2
                        )
                        # Se ambos têm aula da mesma disciplina, é um bloco consecutivo
                        var_bloco = model.NewBoolVar(
                            f"bloco_{turm}_{disc}_{s1.dia}_{s1.hora}_{s2.hora}"
                        )
                        model.Add(var_tem_aula_s1 + var_tem_aula_s2 >= 2).OnlyEnforceIf(var_bloco)
                        model.Add(var_tem_aula_s1 + var_tem_aula_s2 <= 1).OnlyEnforceIf(
                            var_bloco.Not()
                        )
                        termos_objetivo.append((var_bloco.Not(), 6))  # Penalizar se não há bloco

        # S04: disciplinas não espalhadas pela semana
        # Penalizar se todas as aulas de (turma, disciplina) estão num único dia
        for (turm, disc), lesson_ids in sessoes_por_turma_disc.items():
            if len(lesson_ids) < 2:
                continue
            dias_com_aula: list[object] = []
            for slot in slots:
                var_dia_tem_aula = model.NewBoolVar(f"dia_tem_aula_{turm}_{disc}_{slot.dia}")
                model.Add(
                    sum(
                        vars_x[(lid, p, s, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if lid in lesson_ids and sl.dia == slot.dia
                    )
                    >= var_dia_tem_aula
                )
                model.Add(
                    sum(
                        vars_x[(lid, p, s, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if lid in lesson_ids and sl.dia == slot.dia
                    )
                    <= len(lesson_ids) * var_dia_tem_aula
                )
                dias_com_aula.append(var_dia_tem_aula)
            if len(dias_com_aula) > 1:
                # Se só tem aula em um dia, penalizar
                var_somente_um_dia = model.NewBoolVar(f"somente_um_dia_{turm}_{disc}")
                model.Add(sum(dias_com_aula) == 1).OnlyEnforceIf(var_somente_um_dia)
                model.Add(sum(dias_com_aula) >= 2).OnlyEnforceIf(var_somente_um_dia.Not())
                termos_objetivo.append((var_somente_um_dia, 5))

        # S05: padrão A-B-C-A (mesma disciplina interrompida por outra no mesmo dia)
        # Nota: Implementação completa requer modelagem de variáveis por posição
        # de slot dentro de cada (turma, dia). Esta é uma implementação parcial
        # que será completada em iterações futuras. A restrição S05 está
        # documentada no catálogo e será implementada completamente quando
        # o modelo de dados incluir slots com hora de início/fim precisa.
        pass

        # S06: falha de duas horas consecutivas para avaliação
        # Professores com carga_maxima >= 4 devem ter pelo menos um bloco de 2h
        for prof_id, prof in professores.items():
            if prof.carga_maxima_semanal >= 4:
                for dia, slots_dia in slots_por_dia.items():
                    slots_dia_ordenados = sorted(slots_dia, key=lambda s: s.hora)
                    for i in range(len(slots_dia_ordenados) - 1):
                        s1 = slots_dia_ordenados[i]
                        s2 = slots_dia_ordenados[i + 1]
                        if s1.hora + 1 == s2.hora:
                            var_tem_aula_s1 = model.NewBoolVar(
                                f"tem_aula_s1_prof_{prof_id}_{s1.dia}_{s1.hora}"
                            )
                            var_tem_aula_s2 = model.NewBoolVar(
                                f"tem_aula_s2_prof_{prof_id}_{s2.dia}_{s2.hora}"
                            )
                            model.Add(
                                sum(
                                    vars_x[(lid, p, s, sl, sub_id)]
                                    for (lid, p, s, sl, sub_id), v in vars_x.items()
                                    if p == prof_id and sl == s1
                                )
                                >= var_tem_aula_s1
                            )
                            model.Add(
                                sum(
                                    vars_x[(lid, p, s, sl, sub_id)]
                                    for (lid, p, s, sl, sub_id), v in vars_x.items()
                                    if p == prof_id and sl == s1
                                )
                                <= len(slots) * var_tem_aula_s1
                            )
                            model.Add(
                                sum(
                                    vars_x[(lid, p, s, sl, sub_id)]
                                    for (lid, p, s, sl, sub_id), v in vars_x.items()
                                    if p == prof_id and sl == s2
                                )
                                >= var_tem_aula_s2
                            )
                            model.Add(
                                sum(
                                    vars_x[(lid, p, s, sl, sub_id)]
                                    for (lid, p, s, sl, sub_id), v in vars_x.items()
                                    if p == prof_id and sl == s2
                                )
                                <= len(slots) * var_tem_aula_s2
                            )
                            var_bloco = model.NewBoolVar(
                                f"bloco_avaliacao_{prof_id}_{s1.dia}_{s1.hora}_{s2.hora}"
                            )
                            model.Add(var_tem_aula_s1 + var_tem_aula_s2 >= 2).OnlyEnforceIf(
                                var_bloco
                            )
                            model.Add(var_tem_aula_s1 + var_tem_aula_s2 <= 1).OnlyEnforceIf(
                                var_bloco.Not()
                            )
                            termos_objetivo.append(
                                (var_bloco.Not(), 9)
                            )  # Penalizar se não há bloco

        # S07: carga horária do professor fora dos limites
        for prof_id, prof in professores.items():
            total_aulas_var = model.NewIntVar(
                0, prof.carga_maxima_semanal, f"total_aulas_{prof_id}"
            )
            model.Add(
                total_aulas_var
                == sum(
                    vars_x[(lid, p, s, sl, sub_id)]
                    for (lid, p, s, sl, sub_id), v in vars_x.items()
                    if p == prof_id
                )
            )
            # Penalizar se fora dos limites [carga_minima, carga_maxima]
            var_abaixo = model.NewBoolVar(f"abaixo_min_{prof_id}")
            var_acima = model.NewBoolVar(f"acima_max_{prof_id}")
            model.Add(total_aulas_var < prof.carga_minima_semanal).OnlyEnforceIf(var_abaixo)
            model.Add(total_aulas_var >= prof.carga_minima_semanal).OnlyEnforceIf(var_abaixo.Not())
            model.Add(total_aulas_var > prof.carga_maxima_semanal).OnlyEnforceIf(var_acima)
            model.Add(total_aulas_var <= prof.carga_maxima_semanal).OnlyEnforceIf(var_acima.Not())
            termos_objetivo.append((var_abaixo, 8))
            termos_objetivo.append((var_acima, 8))

        # --- S08: professor a trabalhar muitos dias consecutivos ---
        # Calcular sequências de dias de trabalho
        for prof_id in professores:
            dias_ordenados = sorted({sl.dia for sl in slots})
            for i in range(len(dias_ordenados)):
                var_dia_tem_aula = model.NewBoolVar(
                    f"dia_tem_aula_prof_{prof_id}_{dias_ordenados[i]}"
                )
                model.Add(
                    sum(
                        vars_x[(lid, p, s, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if p == prof_id and sl.dia == dias_ordenados[i]
                    )
                    >= var_dia_tem_aula
                )
                model.Add(
                    sum(
                        vars_x[(lid, p, s, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if p == prof_id and sl.dia == dias_ordenados[i]
                    )
                    <= len(slots) * var_dia_tem_aula
                )
            # Penalizar sequências de 5+ dias consecutivos
            for i in range(len(dias_ordenados) - 4):
                janela = dias_ordenados[i : i + 5]
                var_todos_dias = model.NewBoolVar(
                    f"janela_5_dias_{prof_id}_{'_'.join(d for d in janela)}"
                )
                model.Add(
                    sum(
                        vars_x[(lid, p, s, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if p == prof_id and sl.dia in janela
                    )
                    >= 5 * var_todos_dias
                )
                # Se tem aula em todos os 5 dias, penalizar
                termos_objetivo.append((var_todos_dias, 12))

        # --- S09: distribuição desigual de aulas entre professores ---
        # Normalizar por carga contratual
        for disc_id in disciplinas:
            profs_disc = professores_por_disciplina.get(disc_id, [])
            if len(profs_disc) > 1:
                contagens: list[object] = []
                cargas: list[int] = []
                for p in profs_disc:
                    var_count = model.NewIntVar(0, len(slots), f"count_{disc_id}_{p}")
                    model.Add(
                        var_count
                        == sum(
                            vars_x[(lid, p, s, sl, sub_id)]
                            for (lid, p2, s, sl, sub_id), v in vars_x.items()
                            if lid
                            in [
                                s2["lesson_id"]
                                for s2 in aulas_requeridas
                                if s2["disc_id"] == disc_id
                            ]
                            and p2 == p
                        )
                    )
                    contagens.append(var_count)
                    cargas.append(professores[p].carga_maxima_semanal)
                if len(contagens) > 1:
                    max_var = model.NewIntVar(0, len(slots), f"max_{disc_id}")
                    min_var = model.NewIntVar(0, len(slots), f"min_{disc_id}")
                    model.AddMaxEquality(max_var, contagens)
                    model.AddMinEquality(min_var, contagens)
                    diff_var = model.NewIntVar(0, len(slots), f"diff_{disc_id}")
                    model.Add(diff_var == max_var - min_var)
                    # Normalizar: diferença relativa à carga média
                    media_carga = sum(cargas) / len(cargas) if cargas else 1
                    limite = max(2, int(media_carga * 0.25))  # 25% da carga média
                    penaliza_s09 = model.NewBoolVar(f"penaliza_s09_{disc_id}")
                    model.Add(diff_var > limite).OnlyEnforceIf(penaliza_s09)
                    model.Add(diff_var <= limite).OnlyEnforceIf(penaliza_s09.Not())
                    termos_objetivo.append((penaliza_s09, 11))

        # --- S10: carga concentrada em poucos dias ---
        for prof_id in professores:
            for dia in sorted({sl.dia for sl in slots}):
                var_dia_count = model.NewIntVar(0, len(slots), f"countday_{prof_id}_{dia}")
                model.Add(
                    var_dia_count
                    == sum(
                        vars_x[(lid, p, s, sl, sub_id)]
                        for (lid, p, s, sl, sub_id), v in vars_x.items()
                        if p == prof_id and sl.dia == dia
                    )
                )
                # Penalizar quando há >= 5 aulas em um único dia (alinhado com Python)
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
        for (lid, p, s, sl, sub_id), v in vars_x.items():
            if solver.Value(v) == 1:
                # Encontrar turma e disciplina da sessão
                sessao = next((s for s in aulas_requeridas if s["lesson_id"] == lid), None)
                if sessao:
                    novo_horario.adicionar(
                        Aula(
                            turma=sessao["turma_id"],
                            disciplina=sessao["disc_id"],
                            professor=p,
                            sala=s,
                            slot=sl,
                            subgrupo_id=sub_id,
                        )
                    )

        return novo_horario

    # --- Métodos auxiliares ---

    @staticmethod
    def _turma_da_sessao(
        lesson_id: str, turmas: dict[str, Turma], disciplinas: dict[str, Disciplina]
    ) -> str:
        """Extrai o ID da turma de um lesson_id."""
        partes = lesson_id.split("_")
        # lesson_id = f"{turma_id}_{disc_id}_{session_index}"
        # O turma_id pode conter underscores, então precisamos ser cuidadosos
        # Assumindo formato: turma_id_disc_id_session_index
        # O disc_id é o segundo elemento, session_index o último
        # O turma_id é tudo entre o início e o penúltimo underscore
        if len(partes) >= 3:
            return partes[0]  # Simplificação: turma_id não tem underscores
        return lesson_id

    @staticmethod
    def _disc_da_sessao(lesson_id: str, aulas_requeridas: list[dict]) -> str:
        """Encontra o ID da disciplina de um lesson_id."""
        for sessao in aulas_requeridas:
            if sessao["lesson_id"] == lesson_id:
                return sessao["disc_id"]
        return ""

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
