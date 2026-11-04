import { router, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';

import { AdminGate } from '@/components/admin-gate';
import { Badge } from '@/components/badge';
import { Button } from '@/components/button';
import { Card, InfoRow } from '@/components/card';
import { ChoiceChips } from '@/components/choice-chips';
import { PriorityBadge, StatusBadge } from '@/components/occurrence-list-item';
import { Screen } from '@/components/screen';
import { ErrorState, LoadingState } from '@/components/states';
import { TextField } from '@/components/text-field';
import { colors, radius, spacing, typography } from '@/constants/theme';
import { describeError, useAsync } from '@/hooks/use-async';
import { categoryLabel, formatConfidence, formatDateTime, statusLabel } from '@/lib/format';
import { api } from '@/services/api';
import { buildUploadUrl } from '@/services/config';
import type { OccurrenceStatus } from '@/types/domain';

/** Detalhe administrativo de uma ocorrência, com imagem e transições de status. */
export default function OcorrenciaDetalheScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  return (
    <Screen title={`Ocorrência #${id}`} subtitle="Detalhe, classificação e histórico de status.">
      <AdminGate>
        <Detalhe ocorrenciaId={Number(id)} />
      </AdminGate>
    </Screen>
  );
}

function Detalhe({ ocorrenciaId }: { ocorrenciaId: number }) {
  const carregar = useCallback(() => api.occurrenceDetail(ocorrenciaId), [ocorrenciaId]);
  const enums = useAsync(() => api.enums(), []);
  const { data, error, loading, reload } = useAsync(carregar, [ocorrenciaId]);

  const [nota, setNota] = useState('');
  const [novoStatus, setNovoStatus] = useState<OccurrenceStatus | undefined>();
  const [salvando, setSalvando] = useState(false);
  const [erroAcao, setErroAcao] = useState<string | null>(null);

  async function alterarStatus() {
    if (!novoStatus) {
      setErroAcao('Selecione o novo status.');
      return;
    }
    setSalvando(true);
    setErroAcao(null);
    try {
      await api.updateOccurrenceStatus(ocorrenciaId, novoStatus, nota);
      setNota('');
      setNovoStatus(undefined);
      reload();
    } catch (causa) {
      setErroAcao(describeError(causa));
    } finally {
      setSalvando(false);
    }
  }

  if (loading || enums.loading) {
    return <LoadingState message="Carregando ocorrência..." />;
  }
  if (error) {
    return <ErrorState message={error} onRetry={reload} />;
  }
  if (!data) {
    return <ErrorState message="Ocorrência não encontrada." onRetry={reload} />;
  }

  const transicoes = (enums.data?.allowed_transitions?.[data.status] ?? []).map((valor) => ({
    value: valor as OccurrenceStatus,
    label: statusLabel(valor),
  }));
return (
    <>
      <Card title={data.protocol} subtitle={`Registrado em ${formatDateTime(data.created_at)}`}>
        <View style={styles.badges}>
          <StatusBadge status={data.status} />
          <PriorityBadge priority={data.priority} />
          <Badge label={categoryLabel(data.category)} />
          {data.needs_human_review ? (
            <Badge
              label="Revisão humana"
              background={colors.warningSoft}
              textColor={colors.warning}
            />
          ) : null}
        </View>
        <InfoRow label="Bairro" value={data.neighborhood} />
        {data.address ? <InfoRow label="Endereço" value={data.address} /> : null}
        {data.latitude !== null && data.longitude !== null ? (
          <InfoRow label="Coordenadas" value={`${data.latitude}, ${data.longitude}`} />
        ) : null}
        {data.description ? <InfoRow label="Descrição" value={data.description} /> : null}
        <InfoRow
          label="Classificação da IA"
          value={
            data.model_label
              ? `${data.model_label} (${formatConfidence(data.confidence)})`
              : 'Aguardando modelo treinado (FASE 3)'
          }
        />
        {data.dispatch_protocol ? (
          <InfoRow label="Protocolo no portal" value={data.dispatch_protocol} />
        ) : null}
        <InfoRow label="Dados simulados" value={data.is_simulated ? 'sim' : 'não'} />
      </Card>

      {data.images.length > 0 ? (
        <Card title="Imagens enviadas" subtitle="Arquivos gravados no servidor">
          {data.images.map((imagem) => (
            <View key={imagem.id} style={styles.imageWrapper}>
              <Image
                source={{ uri: buildUploadUrl(imagem.file_path) }}
                style={styles.image}
                resizeMode="cover"
                accessibilityLabel={`Imagem da ocorrência ${data.protocol}`}
              />
              <Text style={styles.imageMeta}>
                {imagem.content_type} · {(imagem.size_bytes / 1024).toFixed(1)} KB
                {imagem.width && imagem.height ? ` · ${imagem.width}×${imagem.height}` : ''}
              </Text>
            </View>
          ))}
        </Card>
      ) : null}

      <Card title="Alterar status" subtitle="Apenas transições permitidas pela máquina de estados">
        {transicoes.length === 0 ? (
          <Text style={styles.muted}>
            Este status é terminal: a ocorrência não pode mais mudar de estado.
          </Text>
        ) : (
          <>
            <ChoiceChips
              title="Novo status"
              options={transicoes}
              value={novoStatus}
              allowClear={false}
              onChange={(valor) => setNovoStatus(valor)}
            />
            <TextField
              label="Observação"
              value={nota}
              onChangeText={setNota}
              placeholder="Obrigatória para resolver ou rejeitar"
              multiline
              maxLength={255}
            />
            {erroAcao ? <Text style={styles.error}>{erroAcao}</Text> : null}
            <Button
              label="Confirmar alteração"
              onPress={alterarStatus}
              loading={salvando}
              variant="secondary"
            />
          </>
        )}
      </Card>

      <Card title="Histórico" subtitle="Trilha de auditoria">
        {data.status_history.map((item) => (
          <View key={item.id} style={styles.historyItem}>
            <Text style={styles.historyStatus}>
              {item.from_status ? `${statusLabel(item.from_status)} → ` : ''}
              {statusLabel(item.to_status)}
            </Text>
            <Text style={styles.historyMeta}>
              {formatDateTime(item.created_at)} · {item.changed_by}
            </Text>
            {item.note ? <Text style={styles.historyNote}>{item.note}</Text> : null}
          </View>
        ))}
      </Card>

      <Button label="Voltar para a lista" variant="ghost" onPress={() => router.back()} />
    </>
  );
}

const styles = StyleSheet.create({
  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  imageWrapper: {
    gap: spacing.xs,
  },
  image: {
    width: '100%',
    height: 240,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceMuted,
  },
  imageMeta: {
    fontSize: typography.caption,
    color: colors.textMuted,
  },
  muted: {
    fontSize: typography.caption,
    color: colors.textMuted,
  },
  error: {
    color: colors.danger,
    fontSize: typography.body,
  },
  historyItem: {
    gap: 2,
    paddingVertical: spacing.sm,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  historyStatus: {
    fontSize: typography.body,
    fontWeight: '700',
    color: colors.text,
  },
  historyMeta: {
    fontSize: typography.caption,
    color: colors.textMuted,
  },
  historyNote: {
    fontSize: typography.caption,
    color: colors.textMuted,
    fontStyle: 'italic',
  },
});