import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Badge } from '@/components/badge';
import { Button } from '@/components/button';
import { Card, InfoRow } from '@/components/card';
import { PriorityBadge, StatusBadge } from '@/components/occurrence-list-item';
import { Screen } from '@/components/screen';
import { ErrorState, LoadingState } from '@/components/states';
import { TextField } from '@/components/text-field';
import { colors, spacing, typography } from '@/constants/theme';
import { describeError } from '@/hooks/use-async';
import { categoryLabel, formatConfidence, formatDateTime, statusLabel } from '@/lib/format';
import { isValidProtocol, normalizeProtocol } from '@/lib/validation';
import { api } from '@/services/api';
import type { OccurrenceDetail } from '@/types/domain';

/** Consulta pública do status de uma ocorrência pelo protocolo. */
export default function ConsultarScreen() {
  const [protocolo, setProtocolo] = useState('');
  const [erroCampo, setErroCampo] = useState<string | undefined>();
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [resultado, setResultado] = useState<OccurrenceDetail | null>(null);

  async function consultar() {
    const valor = normalizeProtocol(protocolo);
    if (!isValidProtocol(valor)) {
      setErroCampo('Informe um protocolo no formato CL-2026-000123.');
      return;
    }
    setErroCampo(undefined);
    setErro(null);
    setCarregando(true);
    try {
      const ocorrencia = await api.occurrenceByProtocol(valor);
      setResultado(ocorrencia);
    } catch (causa) {
      setResultado(null);
      setErro(describeError(causa));
    } finally {
      setCarregando(false);
    }
  }

  return (
    <Screen
      title="Consultar protocolo"
      subtitle="Acompanhe o andamento da sua solicitação informando o protocolo recebido."
    >
      <Card>
        <TextField
          label="Protocolo"
          value={protocolo}
          onChangeText={(valor) => {
            setProtocolo(valor);
            setErroCampo(undefined);
          }}
          placeholder="CL-2026-000001"
          autoCapitalize="characters"
          error={erroCampo}
          hint="O protocolo foi informado ao final do registro."
          testID="campo-protocolo"
        />
        <Button label="Consultar" onPress={consultar} loading={carregando} />
      </Card>

      {carregando ? <LoadingState message="Consultando protocolo..." /> : null}

      {!carregando && erro ? (
        <ErrorState message={erro} onRetry={consultar} />
      ) : null}

      {resultado ? (
        <Card title={resultado.protocol} subtitle={`Atualizado em ${formatDateTime(resultado.updated_at)}`}>
          <View style={styles.badges}>
            <StatusBadge status={resultado.status} />
            <PriorityBadge priority={resultado.priority} />
            <Badge label={categoryLabel(resultado.category)} />
          </View>
          <InfoRow label="Bairro" value={resultado.neighborhood} />
          {resultado.address ? <InfoRow label="Endereço" value={resultado.address} /> : null}
          {resultado.description ? (
            <InfoRow label="Descrição" value={resultado.description} />
          ) : null}
          <InfoRow
            label="Classificação da IA"
            value={
              resultado.model_label
                ? `${resultado.model_label} (${formatConfidence(resultado.confidence)})`
                : 'Aguardando modelo treinado (FASE 3)'
            }
          />
          {resultado.dispatch_protocol ? (
            <InfoRow label="Protocolo no portal" value={resultado.dispatch_protocol} />
          ) : null}
        </Card>
      ) : null}

      {resultado ? (
        <Card title="Histórico de status">
          {resultado.status_history.map((item) => (
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
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
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