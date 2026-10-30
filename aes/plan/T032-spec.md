# AES Plan Spec — T032 Rate Limiting

## 1. Sumário Executivo
Adicionar rate limiting ao endpoint do solver para prevenir DoS.

## 2. Mudanças no Backend
- Instalar `slowapi`
- Configurar limite: 5 requisições por minuto por IP para `POST /scheduler/run`
- Retornar 429 quando excedido

## 3. Testes
- Teste de que 6 requisições rápidas resultam em 429

## 4. Critérios de Aceitação
- Rate limit funcionando
- Teste passa
