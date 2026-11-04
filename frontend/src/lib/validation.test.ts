import {
  isFormValid,
  isValidProtocol,
  normalizeProtocol,
  parseCoordinate,
  validateOccurrenceForm,
} from '@/lib/validation';

describe('validateOccurrenceForm', () => {
  const base = { neighborhood: 'Pinheiros', address: '', description: '', reportedCategory: 'OVERFLOW' as const };

  it('aceita um formulário válido', () => {
    const erros = validateOccurrenceForm(base);

    expect(isFormValid(erros)).toBe(true);
  });

  it('exige bairro com pelo menos 3 caracteres', () => {
    const erros = validateOccurrenceForm({ ...base, neighborhood: 'Pi' });

    expect(erros.neighborhood).toMatch(/pelo menos 3/);
    expect(isFormValid(erros)).toBe(false);
  });

  it('ignora espaços ao redor do bairro', () => {
    const erros = validateOccurrenceForm({ ...base, neighborhood: '   Pinheiros   ' });

    expect(erros.neighborhood).toBeUndefined();
  });

  it('limita o endereço a 255 caracteres', () => {
    const erros = validateOccurrenceForm({ ...base, address: 'a'.repeat(256) });

    expect(erros.address).toMatch(/255/);
  });

  it('limita a descrição a 1000 caracteres', () => {
    const erros = validateOccurrenceForm({ ...base, description: 'a'.repeat(1001) });

    expect(erros.description).toMatch(/1000/);
  });
});

describe('protocolo', () => {
  it('normaliza para maiúsculas e remove espaços', () => {
    expect(normalizeProtocol('  cl-2026-000123 ')).toBe('CL-2026-000123');
  });

  it('valida o formato CL-<ano>-<número>', () => {
    expect(isValidProtocol('CL-2026-000123')).toBe(true);
    expect(isValidProtocol('cl-2026-1')).toBe(true);
    expect(isValidProtocol('2026-000123')).toBe(false);
    expect(isValidProtocol('CL-26-1')).toBe(false);
  });
});

describe('parseCoordinate', () => {
  it('devolve undefined para campo vazio', () => {
    expect(parseCoordinate('   ')).toBeUndefined();
  });

  it('aceita vírgula como separador decimal', () => {
    expect(parseCoordinate('-23,5678')).toBeCloseTo(-23.5678, 4);
  });

  it('devolve NaN para texto inválido', () => {
    expect(Number.isNaN(parseCoordinate('abc'))).toBe(true);
  });
});