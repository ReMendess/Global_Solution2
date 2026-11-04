import type { ReactNode } from 'react';
import { StyleSheet, Text, View, type ViewStyle } from 'react-native';

import { colors, radius, spacing, typography } from '@/constants/theme';

interface CardProps {
  children: ReactNode;
  style?: ViewStyle;
  /** Título opcional exibido no topo do cartão. */
  title?: string;
  subtitle?: string;
  footer?: ReactNode;
}

/** Cartão branco com borda suave, base visual de todo o app. */
export function Card({ children, style, title, subtitle, footer }: CardProps) {
  return (
    <View style={[styles.card, style]}>
      {title ? (
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
      ) : null}
      {children}
      {footer ? <View style={styles.footer}>{footer}</View> : null}
    </View>
  );
}

/** Linha rótulo/valor usada em detalhes. */
export function InfoRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      {typeof value === 'string' || typeof value === 'number' ? (
        <Text style={styles.infoValue}>{value}</Text>
      ) : (
        <View>{value}</View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.md,
  },
  header: {
    gap: spacing.xs,
  },
  title: {
    fontSize: typography.subheading,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: typography.caption,
    color: colors.textMuted,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.md,
    marginTop: spacing.xs,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.md,
  },
  infoLabel: {
    fontSize: typography.caption,
    color: colors.textMuted,
    flexShrink: 1,
  },
  infoValue: {
    fontSize: typography.body,
    color: colors.text,
    fontWeight: '600',
    flexShrink: 1,
    textAlign: 'right',
  },
});