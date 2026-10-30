# AES Plan Spec — T033 Env Credentials

## 1. Sumário Executivo
Remover credenciais reais do `.env.example` e garantir que `.env` não é commitado.

## 2. Mudanças
- `docker/.env.example`: apenas placeholders
- `.gitignore`: garantir que `.env` está listado
- `README.md`: documentar variáveis obrigatórias

## 5. Critérios de Aceitação
- `.env.example` sem valores reais
- `.env` no `.gitignore`
- README atualizado
