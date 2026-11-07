import { Link } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { Badge } from '@/components/badge';
import { Card, InfoRow } from '@/components/card';
import { ProfileSwitch } from '@/components/profile-switch';
import { Screen } from '@/components/screen';
import { StatCard } from '@/components/states';
import { colors, radius, spacing, typography } from '@/constants/theme';
import { useAsync } from '@/hooks/use-async';
import { api } from '@/services/api';
import { useProfile } from '@/state/profile-context';

const ATALHOS = [
  {
    href: '/registrar' as const,
    title: 'Registrar ocorrência',
    description: 'Envie uma foto, informe o bairro e receba um protocolo de acompanhamento.',
  },
  {
    href: '/consultar' as const,
    title: 'Consultar protocolo',
    description: 'Acompanhe o status da sua solicitação a partir do número recebido.',
  },
  {
    href: '/admin/dashboard' as const,
    title: 'Área administrativa',
    description: 'Indicadores, ocorrências, contêineres e histórico de sensores.',
  },
];

/** Página inicial do cidadão. */
export default function HomeScreen() {
  const { isAdmin } = useProfile();
  // As informações técnicas (status da API, versão, banco, modelo) só são
  // carregadas para o perfil administrador.
  const { data: health, error } = useAsync(
    () => (isAdmin ? api.health() : Promise.resolve(null)),
    [isAdmin],
  );

  const statusApi = health ? health.status : '—';

  return (
    <Screen
      title="Smart Clean City"
      subtitle="Registre problemas de resíduos urbanos e acompanhe a resolução pela nossa plataforma."
      headerRight={<ProfileSwitch />}
    >
      <Card>
        <Text style={styles.heroTitle}>Descarte irregular? Nós cuidamos do encaminhamento.</Text>
        <Text style={styles.heroText}>
          Fotografe a situação, informe o bairro e a plataforma identifica o tipo de problema,
          encaminha a demanda para a equipe responsável e gera um protocolo para você acompanhar.
        </Text>
      </Card>

      <View style={styles.grid}>
        {ATALHOS.map((atalho) => (
          <Link key={atalho.href} href={atalho.href} style={styles.linkCard}>
            <View style={styles.linkContent}>
              <Text style={styles.linkTitle}>{atalho.title}</Text>
              <Text style={styles.linkDescription}>{atalho.description}</Text>
              <Text style={styles.linkCta}>Acessar →</Text>
            </View>
          </Link>
        ))}
      </View>

      <Card title="Como funciona" subtitle="Fluxo de uma ocorrência na plataforma">
        <InfoRow label="1. Registro" value="Cidadão envia foto e localização" />
        <InfoRow label="2. Identificação" value="A plataforma reconhece o tipo de problema" />
        <InfoRow label="3. Encaminhamento" value="A demanda é enviada para a equipe responsável" />
        <InfoRow label="4. Acompanhamento" value="Status atualizado até a resolução" />
      </Card>

      {isAdmin ? (
        <>
          <Card title="Status do sistema" subtitle="Informações técnicas (visível só para admin)">
            <View style={styles.heroStatus}>
              <Badge
                label={`API: ${statusApi}`}
                background={error ? colors.dangerSoft : colors.primarySoft}
                textColor={error ? colors.danger : colors.primary}
              />
              <Badge
                label={
                  health?.model_loaded
                    ? 'Classificação por IA: ativa'
                    : 'Classificação por IA: aguardando modelo'
                }
                background={health?.model_loaded ? colors.accentSoft : colors.surfaceMuted}
                textColor={health?.model_loaded ? colors.accent : colors.textMuted}
              />
            </View>
          </Card>

          <View style={styles.statsRow}>
            <StatCard label="Versão da API" value={health?.version ?? '—'} hint={health?.environment} />
            <StatCard
              label="Banco de dados"
              value={health?.database ?? '—'}
              hint="SQLite local"
              accent={health?.database === 'ok' ? colors.primary : colors.danger}
            />
            <StatCard
              label="Modelo de visão"
              value={health?.model_loaded ? 'carregado' : 'pendente'}
              hint="Treinamento na FASE 3"
              accent={health?.model_loaded ? colors.accent : colors.warning}
            />
          </View>
        </>
      ) : null}

      {error ? <Text style={styles.offlineHint}>{error}</Text> : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  heroTitle: {
    fontSize: typography.heading,
    fontWeight: '800',
    color: colors.text,
    lineHeight: 27,
  },
  heroText: {
    fontSize: typography.body,
    color: colors.textMuted,
    lineHeight: 22,
  },
  heroStatus: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  linkCard: {
    flexGrow: 1,
    flexBasis: 260,
    textDecorationLine: 'none',
  },
  linkContent: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.sm,
    height: '100%',
  },
  linkTitle: {
    fontSize: typography.subheading,
    fontWeight: '700',
    color: colors.text,
  },
  linkDescription: {
    fontSize: typography.caption,
    color: colors.textMuted,
    lineHeight: 19,
  },
  linkCta: {
    fontSize: typography.caption,
    fontWeight: '800',
    color: colors.primary,
    marginTop: 'auto',
  },
  statsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  offlineHint: {
    fontSize: typography.caption,
    color: colors.danger,
  },
});