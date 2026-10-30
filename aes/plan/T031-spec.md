# AES Plan Spec — T031 XSS Sanitization

## 1. Sumário Executivo
Adicionar sanitização de entrada para prevenir XSS refletido em formulários de contestação e indisponibilidade.

## 2. Mudanças no Frontend
- Instalar `dompurify`
- Sanitizar `reason` e `justification` antes de exibir em `Disputes.tsx` e `TeacherCalendar.tsx`

## 3. Mudanças no Backend
- Adicionar validação nos schemas Pydantic para rejeitar tags HTML em campos de texto livre

## 4. Testes
- Teste de que `<script>` é bloqueado ou sanitizado

## 5. Critérios de Aceitação
- `dompurify` instalado e usado
- Backend rejeita HTML em campos de texto
- Testes passam
