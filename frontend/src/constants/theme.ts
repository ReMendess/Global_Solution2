import type { AlertLevel, OccurrenceStatus, Priority } from '@/types/domain';

/** Paleta e medidas compartilhadas por todas as telas (tema claro). */
export const colors = {
  background: '#e1f1d9',
  surface: '#FFFFFF',
  surfaceMuted: '#EDF2EA',
  border: '#DCE3D9',
  primary: '#1F7A4D',
  primaryDark: '#155C39',
  primarySoft: '#E3F1E8',
  accent: '#2F6FED',
  accentSoft: '#E6EEFD',
  text: '#15211A',
  textMuted: '#5C6B60',
  textInverse: '#FFFFFF',
  danger: '#B3261E',
  dangerSoft: '#FBE7E5',
  warning: '#B26A00',
  warningSoft: '#FDF0DC',
  success: '#1F7A4D',
  successSoft: '#E3F1E8',
  neutral: '#5C6B60',
  neutralSoft: '#EDF2EA',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 18,
  pill: 999,
} as const;

export const typography = {
  title: 26,
  heading: 20,
  subheading: 17,
  body: 15,
  caption: 13,
} as const;

/** Largura máxima do conteúdo em telas grandes (desktop/web). */
export const CONTENT_MAX_WIDTH = 1120;

/** Breakpoint a partir do qual o layout passa a usar múltiplas colunas. */
export const WIDE_BREAKPOINT = 900;

export function isWide(width: number): boolean {
  return width >= WIDE_BREAKPOINT;
}

export const statusColors: Record<OccurrenceStatus, { background: string; text: string }> = {
  OPEN: { background: colors.neutralSoft, text: colors.neutral },
  CLASSIFIED: { background: colors.accentSoft, text: colors.accent },
  PENDING_DISPATCH: { background: colors.warningSoft, text: colors.warning },
  DISPATCHED: { background: colors.primarySoft, text: colors.primary },
  IN_PROGRESS: { background: colors.accentSoft, text: colors.accent },
  RESOLVED: { background: colors.successSoft, text: colors.success },
  REJECTED: { background: colors.dangerSoft, text: colors.danger },
};

export const priorityColors: Record<Priority, { background: string; text: string }> = {
  LOW: { background: colors.neutralSoft, text: colors.neutral },
  MEDIUM: { background: colors.accentSoft, text: colors.accent },
  HIGH: { background: colors.warningSoft, text: colors.warning },
  CRITICAL: { background: colors.dangerSoft, text: colors.danger },
};

export const alertColors: Record<AlertLevel, { background: string; text: string }> = {
  NORMAL: { background: colors.successSoft, text: colors.success },
  HIGH: { background: colors.warningSoft, text: colors.warning },
  CRITICAL: { background: colors.dangerSoft, text: colors.danger },
};