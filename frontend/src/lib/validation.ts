import type { OccurrenceCategory } from '@/types/domain';

export interface OccurrenceFormValues {
  neighborhood: string;
  address: string;
  description: string;
  reportedCategory: OccurrenceCategory;
}

export type OccurrenceFormErrors = Partial<Record<keyof OccurrenceFormValues, string>>;

/**
 * Valida o formulário de registro antes de chamar a API.
 *
 * As mesmas regras do backend são aplicadas aqui (3–120 caracteres para o bairro,
 * 255 para o endereço e 1000 para a descrição) para dar retorno imediato ao cidadão.
 */
export function validateOccurrenceForm(values: OccurrenceFormValues): OccurrenceFormErrors {
  const erros: OccurrenceFormErrors = {};
  const bairro = values.neighborhood.trim();

  if (bairro.length < 3) {
    erros.neighborhood = 'Informe o bairro com pelo menos 3 caracteres.';
  } else if (bairro.length > 120) {
    erros.neighborhood = 'O bairro deve ter no máximo 120 caracteres.';
  }

  if (values.address.trim().length > 255) {
    erros.address = 'O endereço deve ter no máximo 255 caracteres.';
  }

  if (values.description.trim().length > 1000) {
    erros.description = 'A descrição deve ter no máximo 1000 caracteres.';
  }

  return erros;
}

/** Indica se o formulário não possui erros de validação. */
export function isFormValid(errors: OccurrenceFormErrors): boolean {
  return Object.keys(errors).length === 0;
}

/** Normaliza o protocolo digitado pelo cidadão (ex.: "cl-2026-1" → "CL-2026-1"). */
export function normalizeProtocol(value: string): string {
  return value.trim().toUpperCase();
}

/** Um protocolo é considerado plausível quando segue o padrão `CL-<ano>-<número>`. */
export function isValidProtocol(value: string): boolean {
  return /^CL-\d{4}-\d{1,6}$/.test(normalizeProtocol(value));
}

/**
 * Converte texto digitado em coordenada numérica.
 * Devolve `undefined` para campo vazio e `NaN` para texto inválido.
 */
export function parseCoordinate(value: string): number | undefined {
  const texto = value.trim().replace(',', '.');
  if (!texto) {
    return undefined;
  }
  return Number(texto);
}