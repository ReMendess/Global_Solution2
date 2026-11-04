import type {
  AlertLevel,
  OccurrenceCategory,
  OccurrenceStatus,
  Priority,
} from '@/types/domain';

const CATEGORY_LABELS: Record<OccurrenceCategory, string> = {
  ILLEGAL_DUMPING: 'Descarte irregular',
  OVERFLOW: 'Transbordamento',
  DAMAGED_CONTAINER: 'Contêiner danificado',
  OTHER: 'Outros',
};

const STATUS_LABELS: Record<OccurrenceStatus, string> = {
  OPEN: 'Aberta',
  CLASSIFIED: 'Classificada',
  PENDING_DISPATCH: 'Aguardando envio',
  DISPATCHED: 'Encaminhada',
  IN_PROGRESS: 'Em atendimento',
  RESOLVED: 'Resolvida',
  REJECTED: 'Rejeitada',
};

const PRIORITY_LABELS: Record<Priority, string> = {
  LOW: 'Baixa',
  MEDIUM: 'Média',
  HIGH: 'Alta',
  CRITICAL: 'Crítica',
};

const ALERT_LABELS: Record<AlertLevel, string> = {
  NORMAL: 'Normal',
  HIGH: 'Alto',
  CRITICAL: 'Crítico',
};

export const categoryLabel = (valor: string): string =>
  CATEGORY_LABELS[valor as OccurrenceCategory] ?? valor;

export const statusLabel = (valor: string): string =>
  STATUS_LABELS[valor as OccurrenceStatus] ?? valor;

export const priorityLabel = (valor: string): string =>
  PRIORITY_LABELS[valor as Priority] ?? valor;

export const alertLabel = (valor: string): string => ALERT_LABELS[valor as AlertLevel] ?? valor;

export const categoryOptions = (): { value: OccurrenceCategory; label: string }[] =>
  (Object.keys(CATEGORY_LABELS) as OccurrenceCategory[]).map((value) => ({
    value,
    label: CATEGORY_LABELS[value],
  }));

export const statusOptions = (): { value: OccurrenceStatus; label: string }[] =>
  (Object.keys(STATUS_LABELS) as OccurrenceStatus[]).map((value) => ({
    value,
    label: STATUS_LABELS[value],
  }));

/** Formata uma data ISO (UTC sem timezone) como `dd/mm/aaaa hh:mm`. */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) {
    return '—';
  }
  const data = new Date(iso.endsWith('Z') ? iso : `${iso}Z`);
  if (Number.isNaN(data.getTime())) {
    return '—';
  }
  const dia = String(data.getDate()).padStart(2, '0');
  const mes = String(data.getMonth() + 1).padStart(2, '0');
  const hora = String(data.getHours()).padStart(2, '0');
  const minuto = String(data.getMinutes()).padStart(2, '0');
  return `${dia}/${mes}/${data.getFullYear()} ${hora}:${minuto}`;
}

/** Converte confiança (0–1) em percentual legível. */
export function formatConfidence(confidence: number | null | undefined): string {
  if (confidence === null || confidence === undefined) {
    return '—';
  }
  return `${Math.round(confidence * 100)}%`;
}

/** Converte horas decimais em texto curto (`1 h 30 min`). */
export function formatHours(hours: number | null | undefined): string {
  if (hours === null || hours === undefined || Number.isNaN(hours)) {
    return '—';
  }
  const totalMinutos = Math.round(hours * 60);
  const h = Math.floor(totalMinutos / 60);
  const m = totalMinutos % 60;
  if (h === 0) {
    return `${m} min`;
  }
  return m === 0 ? `${h} h` : `${h} h ${m} min`;
}

/** Percentual de ocupação limitado ao intervalo 0–100. */
export function formatFillLevel(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '—';
  }
  return `${Math.max(0, Math.min(100, Math.round(value)))}%`;
}