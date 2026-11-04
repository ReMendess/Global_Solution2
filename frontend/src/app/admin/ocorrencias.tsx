import { router } from 'expo-router';
import { useCallback, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AdminGate } from '@/components/admin-gate';
import { Button } from '@/components/button';
import { Card } from '@/components/card';
import { ChoiceChips } from '@/components/choice-chips';
import { OccurrenceListItem } from '@/components/occurrence-list-item';
import { Screen } from '@/components/screen';
import { EmptyState, ErrorState, LoadingState } from '@/components/states';
import { TextField } from '@/components/text-field';
import { colors, spacing, typography } from '@/constants/theme';
import { useAsync } from '@/hooks/use-async';
import { categoryOptions, statusOptions } from '@/lib/format';
import { api } from '@/services/api';
import type { OccurrenceCategory, OccurrenceStatus } from '@/types/domain';

const PAGE_SIZE = 10;

/** Lista administrativa de ocorrências com filtros e paginação. */
export default function OcorrenciasScreen() {
  return (
    <Screen
      title="Ocorrências"
      subtitle="Filtre por status, categoria ou bairro e abra o detalhe para acompanhar."
    >
      <AdminGate>
        <ListaOcorrencias />
      </AdminGate>
    </Screen>
  );
}

function ListaOcorrencias() {
  const [status, setStatus] = useState<OccurrenceStatus | undefined>();
  const [categoria, setCategoria] = useState<OccurrenceCategory | undefined>();
  const [bairro, setBairro] = useState('');
  const [bairroAplicado, setBairroAplicado] = useState('');
  const [limite, setLimite] = useState(PAGE_SIZE);

  const carregar = useCallback(
    () =>
      api.listOccurrences({
        status,
        category: categoria,
        neighborhood: bairroAplicado || undefined,
        limit: limite,
        offset: 0,
      }),
    [status, categoria, bairroAplicado, limite],
  );

  const { data, error, loading, reload } = useAsync(carregar, [
    status,
    categoria,
    bairroAplicado,
    limite,
  ]);

  const itens = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <>
      <Card title="Filtros">
        <ChoiceChips
          title="Status"
          options={statusOptions()}
          value={status}
          onChange={setStatus}
        />
        <ChoiceChips
          title="Categoria"
          options={categoryOptions()}
          value={categoria}
          onChange={setCategoria}
        />
        <View style={styles.filtroBairro}>
          <TextField
            label="Bairro"
            value={bairro}
            onChangeText={setBairro}
            placeholder="Ex.: Pinheiros"
          />
          <Button label="Aplicar" variant="secondary" onPress={() => setBairroAplicado(bairro)} />
        </View>
      </Card>

      {loading ? <LoadingState message="Carregando ocorrências..." /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={reload} /> : null}

      {!loading && !error ? (
        <>
          <Text style={styles.total}>{total} ocorrência(s) encontrada(s)</Text>
          {itens.length === 0 ? (
            <EmptyState
              title="Nenhuma ocorrência para estes filtros"
              message="Ajuste os filtros ou registre uma nova ocorrência."
            />
          ) : (
            <View style={styles.list}>
              {itens.map((ocorrencia) => (
                <OccurrenceListItem
                  key={ocorrencia.id}
                  occurrence={ocorrencia}
                  onPress={() => router.push(`/admin/ocorrencias/${ocorrencia.id}`)}
                />
              ))}
            </View>
          )}

          {itens.length < total ? (
            <Button
              label="Carregar mais"
              variant="secondary"
              onPress={() => setLimite((atual) => atual + PAGE_SIZE)}
            />
          ) : null}
        </>
      ) : null}
    </>
  );
}

const styles = StyleSheet.create({
  filtroBairro: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'flex-end',
    gap: spacing.md,
  },
  total: {
    fontSize: typography.caption,
    color: colors.textMuted,
    fontWeight: '700',
  },
  list: {
    gap: spacing.md,
  },
});