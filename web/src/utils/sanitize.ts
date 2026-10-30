import DOMPurify from "dompurify";

/**
 * Sanitiza uma string HTML para prevenir XSS.
 * Deve ser usado em qualquer conteúdo gerado pelo utilizador antes de exibir.
 */
export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true, svg: false, mathMl: false } });
}

/**
 * Sanitiza texto simples (remove qualquer tag HTML).
 */
export function sanitizeText(text: string): string {
  return DOMPurify.sanitize(text, { USE_PROFILES: { html: false, svg: false, mathMl: false } });
}
