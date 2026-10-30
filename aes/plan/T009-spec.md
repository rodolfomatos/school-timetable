# AES Plan Spec — T009 Revisão Hostil

## 1. Sumário Executivo
Conduzir uma revisão hostil (peer review) sobre todo o código e documentação do projeto, produzindo findings BLOCKER/MAJOR/MINOR com condições de fechamento verificáveis.

## 2. Áreas de Revisão
- **Correção**: restrições duras/moles implementadas corretamente? CP-SAT modelado corretamente? Metaheurística respeita slots imutáveis?
- **Simplicidade**: código desnecessário? complexidade aciclírmatica elevada?
- **Manutenibilidade**: nomes de variáveis, documentação, tipos, consistência.
- **Segurança**: validação de entrada JSON, importação de ficheiros.
- **Performance**: avaliação incremental, tamanho da lista tabu, número de vizinhos.

## 3. Saída Esperada
Ficheiro `aes/shadow/SD-REVIEW-001.md` com:
- Lista de findings (severidade, evidência, descrição, condição de fechamento)
- Veredito geral: APROVADO / APROVADO COM CONDIÇÕES / REJEITADO

## 4. Critérios de Fechamento
- BLOCKER: deve ser corrigido antes de avançar para Learn.
- MAJOR: deve ser corrigido ou ter plano de mitigação antes de avançar.
- MINOR: deve ser documentado e pode ser adiado para backlog.

## 5. Fase atual
Plan → Review.
