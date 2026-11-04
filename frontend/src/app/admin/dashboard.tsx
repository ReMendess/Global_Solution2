import { Link } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { AdminGate } from '@/components/admin-gate';
import { Badge, ProgressBar } from '@/components/badge';
import { Card, InfoRow } from '@/components/card';
import { Screen } from '@/components/screen';
import { ErrorState, LoadingState, StatCard } from '@/components/states';
import { colors, radius, spacing, typography } from '@/constants/theme';
import { useAsync } from '@/hooks/use-async';
import { alertLabel, categoryLabel, formatHours } from '@/lib/format';
import { api } from '@/services/api';

const ATALHOS = [
  { href: '/admin/ocorrencias' as const, label: 'Ver ocorrências' },
  { href: '/admin/conteineres' as const, label: 'Ver contêineres' },
];

/** Dashboard administrativo com os indicadores reais da API. */
export default function DashboardScreen() {
  return (
    <Screen
      title="Dashboard"
      subtitle="Indicadores calculados a partir dos dados persistidos no backend."
    >
      <AdminGate>
        <DashboardContent />
      </AdminGate>
    </Screen>
  );
}

function DashboardContent() {
  const resumo = useAsync(() => api.dashboardSummary(), []);
  const containers = useAsync(() => api.dashboardContainers(), []);
  const bairros = useAsync(() => api.dashboardNeighborhoods(8), []);

  if (resumo.loading || containers.loading || bairros.loading) {
    return <LoadingState message="Carregando indicadores..." />;
  }

  if (resumo.error || containers.error || bairros.error) {
    return (
      <ErrorState
        message={resumo.error ?? containers.error ?? bairros.error ?? ''}
        onRetry={() => {
          resumo.reload();
          containers.reload();
          bairros.reload();
        }}
      />
    );
  }

  const dados = resumo.data;
  const alertas = containers.data;
  const ranking = bairros.data;

  return (
    <>
      <View style={styles.statsRow}>
        <StatCard
          label="Ocorrências"
          value={dados?.total_occurrences ?? 0}
          hint="total registrado"
        />
        <StatCard
          label="Aguardando envio"
          value={dados?.by_status?.PENDING_DISPATCH ?? 0}
          hint="fila do RPA"
          accent={colors.warning}
        />
        <StatCard
          label="Resolvidas"
          value={dados?.by_status?.RESOLVED ?? 0}
          hint="atendimentos concluídos"
        />
        <StatCard
          label="Revisão humana"
          value={dados?.needs_human_review ?? 0}
          hint="classificação duvidosa"
          accent={colors.warning}
        />
        <StatCard
          label="Tempo médio"
          value={formatHours(dados?.average_resolution_hours ?? null)}
          hint="até a resolução"
        />
      </View>

      <View style={styles.columns}>
        <View style={styles.column}>
          <Card title="Por status" subtitle="Distribuição das ocorrências">
            {Object.entries(dados?.by_status ?? {}).map(([chave, valor]) => (
              <InfoRow key={chave} label={chave} value={valor} />
            ))}
          </Card>
        </View>
        <View style={styles.column}>
          <Card title="Por categoria" subtitle="Classificação das ocorrências">
            {Object.entries(dados?.by_category ?? {}).map(([chave, valor]) => (
              <InfoRow key={chave} label={categoryLabel(chave)} value={valor} />
            ))}
          </Card>
        </View>
        <View style={styles.column}>
          <Card title="Por prioridade">
            {Object.entries(dados?.by_priority ?? {}).map(([chave, valor]) => (
              <InfoRow key={chave} label={chave} value={valor} />
            ))}
          </Card>
        </View>
      </View>

      <Card
        title="Contêineres monitorados"
        subtitle={`${alertas?.total_containers ?? 0} contêineres com telemetria simulada`}
      >
        {(['NORMAL', 'HIGH', 'CRITICAL'] as const).map((nivel) => {
          const total = alertas?.by_alert_level?.[nivel] ?? 0;
          const totalGeral = alertas?.total_containers ?? 0;
          const percentual = totalGeral > 0 ? (total / totalGeral) * 100 : 0;
          const cor =
            nivel === 'CRITICAL'
              ? colors.danger
              : nivel === 'HIGH'
                ? colors.warning
                : colors.primary;
          return (
            <View key={nivel} style={styles.alertRow}>
              <View style={styles.alertHeader}>
                <Badge label={alertLabel(nivel)} />
                <Text style={styles.alertValue}>{total}</Text>
              </View>
              <ProgressBar value={percentual} color={cor} />
            </View>
          );
        })}
        {alertas?.critical_codes?.length ? (
          <Text style={styles.muted}>
            Em nível crítico: {alertas.critical_codes.join(', ')}
          </Text>
        ) : null}
      </Card>

      <Card title="Bairros com mais ocorrências" subtitle="Ranking por volume">
        {(ranking?.items ?? []).length === 0 ? (
          <Text style={styles.muted}>Sem dados suficientes.</Text>
        ) : (
          ranking?.items.map((item) => (
            <InfoRow key={item.neighborhood} label={item.neighborhood} value={item.total} />
          ))
        )}
      </Card>

      <View style={styles.links}>
        {ATALHOS.map((atalho) => (
          <Link key={atalho.href} href={atalho.href} style={styles.linkButton}>
            <Text style={styles.linkLabel}>{atalho.label}</Text>
          </Link>
        ))}
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  statsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  columns: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  column: {
    flexGrow: 1,
    flexBasis: 260,
  },
  alertRow: {
    gap: spacing.xs,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  alertValue: {
    fontSize: typography.body,
    fontWeight: '700',
    color: colors.text,
  },
  muted: {
    fontSize: typography.caption,
    color: colors.textMuted,
  },
  links: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  linkButton: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    textDecorationLine: 'none',
  },
  linkLabel: {
    color: colors.primary,
    fontWeight: '700',
    fontSize: typography.body,
  },
});