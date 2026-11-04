import { Link } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Badge } from '@/components/badge';
import { Button } from '@/components/button';
import { Card, InfoRow } from '@/components/card';
import { OccurrenceForm } from '@/components/occurrence-form';
import { PriorityBadge, StatusBadge } from '@/components/occurrence-list-item';
import { Screen } from '@/components/screen';
import { colors, radius, spacing, typography } from '@/constants/theme';
import { categoryLabel, formatConfidence, formatDateTime } from '@/lib/format';
import type { OccurrenceDetail } from '@/types/domain';

/** Tela de registro de ocorrência pelo cidadão. */
export default function RegistrarScreen() {
  const [resultado, setResultado] = useState<OccurrenceDetail | null>(null);

  if (resultado) {
    return (
      <Screen
        title="Ocorrência registrada"
        subtitle="Guarde o protocolo abaixo para acompanhar o atendimento."
      >
        <Card title="Protocolo">
          <Text accessibilityRole="header" style={styles.protocol}>
            {resultado.protocol}
          </Text>
          <View style={styles.badges}>
            <StatusBadge status={resultado.status} />
            <PriorityBadge priority={resultado.priority} />
            <Badge label={categoryLabel(resultado.category)} />
          </View>
          <InfoRow label="Bairro" value={resultado.neighborhood} />
          <InfoRow label="Registrado em" value={formatDateTime(resultado.created_at)} />
          <InfoRow
            label="Classificação da IA"
            value={
              resultado.model_label
                ? `${resultado.model_label} (${formatConfidence(resultado.confidence)})`
                : 'Aguardando modelo treinado (FASE 3)'
            }
          />
          {resultado.needs_human_review ? (
            <Badge
              label="Marcada para revisão humana"
              background={colors.warningSoft}
              textColor={colors.warning}
            />
          ) : null}
        </Card>

        <Card title="Histórico" subtitle="Transições registradas pela plataforma">
          {resultado.status_history.map((item) => (
            <InfoRow
              key={item.id}
              label={formatDateTime(item.created_at)}
              value={`${item.from_status ?? '—'} → ${item.to_status}`}
            />
          ))}
        </Card>

        <View style={styles.actions}>
          <Link href="/consultar" style={styles.linkButton}>
            <Text style={styles.linkButtonLabel}>Consultar protocolo</Text>
          </Link>
          <Button
            label="Registrar outra ocorrência"
            variant="secondary"
            onPress={() => setResultado(null)}
          />
        </View>
      </Screen>
    );
  }

  return (
    <Screen
      title="Registrar ocorrência"
      subtitle="Descreva o problema e, se possível, envie uma foto do local."
    >
      <OccurrenceForm onCreated={setResultado} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  protocol: {
    fontSize: 30,
    fontWeight: '800',
    color: colors.primary,
    letterSpacing: 1,
  },
  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  actions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
    alignItems: 'center',
  },
  linkButton: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    textDecorationLine: 'none',
  },
  linkButtonLabel: {
    color: colors.primary,
    fontWeight: '700',
    fontSize: typography.body,
  },
});