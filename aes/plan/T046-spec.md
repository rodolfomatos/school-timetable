# AES Plan Spec — T046 Suporte a Subgrupos de Turma

## 1. Sumário Executivo
Adicionar suporte a subgrupos de turma para permitir divisões de aulas (ex: música em regime articulado — parte teórica, parte prática).

## 2. Modelo de Dados
### Nova entidade: Subgrupo
- identificador: str
- turma_pai: str (referência à turma)
- nome: str (ex: "Grupo A", "Grupo B", "Subgrupo 1")
- numero_alunos: int

### Aula atualizada
- Novo campo opcional: `subgrupo_id: Optional[str] = None`
- Quando `subgrupo_id` está presente, a aula é apenas para esse subgrupo da turma

## 3. Restrições Afetadas
### H03 (turma não tem duas aulas no mesmo slot)
- Alterada para: `(turma_id, subgrupo_id, slot)` não pode ter duplicatas
- Duas aulas da mesma turma podem ocorrer no mesmo slot se forem de subgrupos diferentes

### H01 (professor não dá duas aulas no mesmo slot)
- Não muda (já verifica por professor independente de turma/subgrupo)

### H02 (sala não alberga duas aulas no mesmo slot)
- Não muda (já verifica por sala independente de turma/subgrupo)

## 4. CP-SAT
- Variáveis incluem `subgrupo_id` quando aplicável
- Restrição de cobertura: cada sessão de subgrupo tem exatamente uma atribuição

## 5. Testes
- Teste: duas aulas da mesma turma em subgrupos diferentes no mesmo slot são permitidas
- Teste: duas aulas do mesmo subgrupo no mesmo slot são proibidas
- Teste: seed gera aulas com subgrupos

## Fase atual
Plan → Build.
