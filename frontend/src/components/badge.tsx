import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, typography } from '@/constants/theme';

interface BadgeProps {
  label: string;
  background?: string;
  textColor?: string;
  /** Rótulo acessível; por padrão usa o próprio texto. */
  accessibilityLabel?: string;
}

/** Etiqueta compacta usada para status, prioridade e alertas. */
export function Badge({ label, background, textColor, accessibilityLabel }: BadgeProps) {
  return (
    <View
      accessibilityLabel={accessibilityLabel ?? label}
      style={[styles.badge, { backgroundColor: background ?? colors.surfaceMuted }]}
    >
      <Text style={[styles.text, { color: textColor ?? colors.textMuted }]}>{label}</Text>
    </View>
  );
}

/** Barra horizontal simples para representar ocupação (0–100%). */
export function ProgressBar({
  value,
  color = colors.primary,
  trackColor = colors.surfaceMuted,
}: {
  value: number;
  color?: string;
  trackColor?: string;
}) {
  const percentual = Math.max(0, Math.min(100, value));
  return (
    <View style={[styles.track, { backgroundColor: trackColor }]}>
      <View style={[styles.fill, { width: `${percentual}%`, backgroundColor: color }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: spacing.sm + 2,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    alignSelf: 'flex-start',
  },
  text: {
    fontSize: typography.caption - 1,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
  track: {
    height: 8,
    borderRadius: radius.pill,
    overflow: 'hidden',
    width: '100%',
  },
  fill: {
    height: '100%',
    borderRadius: radius.pill,
  },
});