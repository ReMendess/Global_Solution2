import {
  alertLabel,
  categoryLabel,
  formatConfidence,
  formatDateTime,
  formatFillLevel,
  formatHours,
  priorityLabel,
  statusLabel,
} from '@/lib/format';

describe('rótulos em português', () => {
  it('traduz categorias', () => {
    expect(categoryLabel('ILLEGAL_DUMPING')).toBe('Descarte irregular');
    expect(categoryLabel('OVERFLOW')).toBe('Transbordamento');
    expect(categoryLabel('DAMAGED_CONTAINER')).toBe('Contêiner danificado');
    expect(categoryLabel('OTHER')).toBe('Outros');
  });

  it('traduz status', () => {
    expect(statusLabel('PENDING_DISPATCH')).toBe('Aguardando envio');
    expect(statusLabel('RESOLVED')).toBe('Resolvida');
  });

  it('traduz prioridades e alertas', () => {
    expect(priorityLabel('CRITICAL')).toBe('Crítica');
    expect(alertLabel('HIGH')).toBe('Alto');
  });

  it('mantém valores desconhecidos sem quebrar', () => {
    expect(categoryLabel('NOVO_VALOR')).toBe('NOVO_VALOR');
    expect(statusLabel('')).toBe('');
  });
});

describe('formatDateTime', () => {
  it('formata data ISO UTC como dd/mm/aaaa hh:mm', () => {
    expect(formatDateTime('2026-11-04T12:30:00')).toMatch(/^04\/11\/2026 \d{2}:\d{2}$/);
  });

  it('devolve travessão para valor ausente ou inválido', () => {
    expect(formatDateTime(null)).toBe('—');
    expect(formatDateTime(undefined)).toBe('—');
    expect(formatDateTime('data-invalida')).toBe('—');
  });
});

describe('formatação numérica', () => {
  it('converte confiança em percentual', () => {
    expect(formatConfidence(0.917)).toBe('92%');
    expect(formatConfidence(null)).toBe('—');
  });

  it('converte horas decimais em texto', () => {
    expect(formatHours(1.5)).toBe('1 h 30 min');
    expect(formatHours(2)).toBe('2 h');
    expect(formatHours(0.5)).toBe('30 min');
    expect(formatHours(null)).toBe('—');
  });

  it('limita o percentual de ocupação entre 0 e 100', () => {
    expect(formatFillLevel(93.5)).toBe('94%');
    expect(formatFillLevel(150)).toBe('100%');
    expect(formatFillLevel(-10)).toBe('0%');
  });
});