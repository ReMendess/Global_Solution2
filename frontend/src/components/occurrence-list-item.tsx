import { Pressable, StyleSheet, Text, View } from 'react-native';

import { alertColors, colors, priorityColors, radius, spacing, statusColors, typography } from '@/constants/theme';
import { categoryLabel, formatDateTime, priorityLabel, statusLabel } from '@/lib/format';
import type { AlertLevel, Occurrence, OccurrenceStatus, Priority } from '@/types/domain';

import { Badge, ProgressBar } from './badge';

/** Badge de status da ocorrência. */
export function StatusBadge({ status }: { status: OccurrenceStatus }) {
  const cores = statusColors[status] ?? statusColors.OPEN;
  return <Badge label={statusLabel(status)} background={cores.background} textColor={cores.text} />;
}

/** Badge de prioridade. */
export function PriorityBadge({ priority }: { priority: Priority }) {
  const cores = priorityColors[priority] ?? priorityColors.LOW;
  return <Badge label={priorityLabel(priority)} background={cores.background} textColor={cores.text} />;
}

/** Badge de nível de alerta de contêiner. */
export function AlertBadge({ level }: { level: AlertLevel }) {
  const cores = alertColors[level] ?? alertColors.NORMAL;
  return <Badge label={level} background={cores.background} textColor={cores.text} />;
}

/** Item da lista administrativa de ocorrências. */
export function OccurrenceListItem({
  occurrence,
  onPress,
}: {
  occurrence: Occurrence;
  onPress: () => void;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`Ocorrência ${occurrence.protocol}`}
      onPress={onPress}
      style={({ pressed }) => [styles.item, pressed ? styles.itemPressed : null]}
    >
      <View style={styles.itemHeader}>
        <Text style={styles.protocol}>{occurrence.protocol}</Text>
        <StatusBadge status={occurrence.status} />
      </View>
      <Text style={styles.itemTitle}>
        {categoryLabel(occurrence.category)} · {occurrence.neighborhood}
      </Text>
      {occurrence.description ? (
        <Text style={styles.itemDescription} numberOfLines={2}>
          {occurrence.description}
        </Text>
      ) : null}
      <View style={styles.itemFooter}>
        <PriorityBadge priority={occurrence.priority} />
        {occurrence.needs_human_review ? (
          <Badge
            label="Revisão humana"
            background={colors.warningSoft}
            textColor={colors.warning}
          />
        ) : null}
        <Text style={styles.date}>{formatDateTime(occurrence.created_at)}</Text>
      </View>
    </Pressable>
  );
}

/** Cartão resumido de contêiner com barra de ocupação. */
export function ContainerCard({
  code,
  neighborhood,
  fillLevel,
  alertLevel,
  lastReading,
  onPress,
}: {
  code: string;
  neighborhood: string;
  fillLevel: number;
  alertLevel: AlertLevel;
  lastReading: string | null;
  onPress: () => void;
}) {
  const cores = alertColors[alertLevel] ?? alertColors.NORMAL;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`Contêiner ${code}`}
      onPress={onPress}
      style={({ pressed }) => [styles.item, pressed ? styles.itemPressed : null]}
    >
      <View style={styles.itemHeader}>
        <Text style={styles.protocol}>{code}</Text>
        <AlertBadge level={alertLevel} />
      </View>
      <Text style={styles.itemTitle}>{neighborhood}</Text>
      <ProgressBar value={fillLevel} color={cores.text} />
      <View style={styles.itemFooter}>
        <Text style={styles.date}>Ocupação {Math.round(fillLevel)}%</Text>
        <Text style={styles.date}>Última leitura: {formatDateTime(lastReading)}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  item: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  itemPressed: {
    opacity: 0.88,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  protocol: {
    fontSize: typography.caption,
    fontWeight: '800',
    color: colors.primary,
    letterSpacing: 0.4,
  },
  itemTitle: {
    fontSize: typography.subheading,
    fontWeight: '700',
    color: colors.text,
  },
  itemDescription: {
    fontSize: typography.body,
    color: colors.textMuted,
    lineHeight: 21,
  },
  itemFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  date: {
    fontSize: typography.caption,
    color: colors.textMuted,
    marginLeft: 'auto',
  },
});