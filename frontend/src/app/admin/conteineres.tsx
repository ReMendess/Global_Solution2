import { useCallback, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AdminGate } from '@/components/admin-gate';
import { Badge } from '@/components/badge';
import { Card, InfoRow } from '@/components/card';
import { ChoiceChips } from '@/components/choice-chips';
import { ContainerCard } from '@/components/occurrence-list-item';
import { Screen } from '@/components/screen';
import { EmptyState, ErrorState, LoadingState } from '@/components/states';
import { colors, spacing, typography } from '@/constants/theme';
import { useAsync } from '@/hooks/use-async';
import { alertLabel, formatDateTime, formatFillLevel } from '@/lib/format';
import { api } from '@/services/api';
import type { AlertLevel } from '@/types/domain';

const FILTROS_ALERTA = (['NORMAL', 'HIGH', 'CRITICAL'] as const).map((nivel) => ({
  value: nivel as AlertLevel,
  label: alertLabel(nivel),
}));

/** Monitoramento de contêineres e histórico de leituras dos sensores simulados. */
export default function ConteineresScreen() {
  return (
    <Screen
      title="Contêineres"
      subtitle="Ocupação atual e histórico de leituras enviadas pelos sensores simulados."
    >
      <AdminGate>
        <ListaConteineres />
      </AdminGate>
    </Screen>
  );
}

function ListaConteineres() {
  const [nivel, setNivel] = useState<AlertLevel | undefined>();
  const [selecionado, setSelecionado] = useState<string | null>(null);

  const carregar = useCallback(() => api.listContainers({ alertLevel: nivel }), [nivel]);
  const { data, error, loading, reload } = useAsync(carregar, [nivel]);

  const itens = data?.items ?? [];

  return (
    <>
      <Card title="Filtros">
        <ChoiceChips
          title="Nível de alerta"
          options={FILTROS_ALERTA}
          value={nivel}
          onChange={setNivel}
        />
        <Text style={styles.total}>{data?.total ?? 0} contêiner(es) monitorado(s)</Text>
      </Card>

      {loading ? <LoadingState message="Carregando contêineres..." /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={reload} /> : null}

      {!loading && !error ? (
        itens.length === 0 ? (
          <EmptyState
            title="Nenhum contêiner encontrado"
            message="Ajuste o filtro de alerta ou execute o seed de demonstração."
          />
        ) : (
          <View style={styles.list}>
            {itens.map((container) => (
              <View key={container.code}>
                <ContainerCard
                  code={container.code}
                  neighborhood={container.neighborhood}
                  fillLevel={container.current_fill_level}
                  alertLevel={container.alert_level}
                  lastReading={container.last_reading_at}
                  onPress={() =>
                    setSelecionado((atual) => (atual === container.code ? null : container.code))
                  }
                />
                {selecionado === container.code ? (
                  <LeiturasDoContainer code={container.code} />
                ) : null}
              </View>
            ))}
          </View>
        )
      ) : null}
    </>
  );
}

function LeiturasDoContainer({ code }: { code: string }) {
  const carregar = useCallback(() => api.containerReadings(code, { limit: 10 }), [code]);
  const { data, error, loading, reload } = useAsync(carregar, [code]);

  return (
    <Card title={`Histórico · ${code}`} subtitle="Leituras mais recentes primeiro">
      {loading ? <LoadingState message="Carregando leituras..." /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={reload} /> : null}
      {!loading && !error ? (
        (data?.items ?? []).length === 0 ? (
          <Text style={styles.muted}>Nenhuma leitura registrada para este contêiner.</Text>
        ) : (
          (data?.items ?? []).map((leitura) => (
            <View key={leitura.id} style={styles.reading}>
              <View style={styles.readingHeader}>
                <Text style={styles.readingSensor}>{leitura.sensor_id}</Text>
                <Badge label={leitura.alert_level} />
              </View>
              <InfoRow label="Ocupação" value={formatFillLevel(leitura.fill_level)} />
              <InfoRow
                label="Distância medida"
                value={
                  leitura.distance_cm !== null ? `${leitura.distance_cm.toFixed(1)} cm` : '—'
                }
              />
              <InfoRow label="Medida em" value={formatDateTime(leitura.measured_at)} />
            </View>
          ))
        )
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  total: {
    fontSize: typography.caption,
    color: colors.textMuted,
    fontWeight: '700',
  },
  list: {
    gap: spacing.md,
  },
  muted: {
    fontSize: typography.caption,
    color: colors.textMuted,
  },
  reading: {
    gap: spacing.xs,
    paddingVertical: spacing.sm,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  readingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  readingSensor: {
    fontSize: typography.body,
    fontWeight: '700',
    color: colors.text,
  },
});