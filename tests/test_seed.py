"""Testes para o módulo de seed."""

from timetable.models import Horario, Slot
from timetable.seed import gerar_seed_parcial, marcar_como_imutavel


def test_gerar_seed_preenche_aproximadamente_30_porcento():
    slots = [Slot(dia="segunda", hora=h) for h in range(1, 11)]
    h = Horario()
    resultado = gerar_seed_parcial(h, slots, taxa_preenchimento=0.30, semente=42)
    # 10 slots * 0.30 = 3 (arredondado para baixo, min 1)
    assert 1 <= len(resultado.aulas) <= 5


def test_marcar_como_imutavel_retorna_frozenset():
    slots = [Slot(dia="segunda", hora=1), Slot(dia="terca", hora=2)]
    imutaveis = marcar_como_imutavel(slots)
    assert isinstance(imutaveis, frozenset)
    assert Slot(dia="segunda", hora=1) in imutaveis
