import * as ImagePicker from 'expo-image-picker';
import { useState } from 'react';
import { Image, Platform, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { Card } from '@/components/card';
import { ChoiceChips } from '@/components/choice-chips';
import { TextField } from '@/components/text-field';
import { colors, radius, spacing, typography } from '@/constants/theme';
import { describeError } from '@/hooks/use-async';
import { categoryOptions } from '@/lib/format';
import {
  isFormValid,
  parseCoordinate,
  validateOccurrenceForm,
  type OccurrenceFormErrors,
  type OccurrenceFormValues,
} from '@/lib/validation';
import { api } from '@/services/api';
import { ApiError } from '@/services/api-client';
import type { OccurrenceCategory, OccurrenceDetail, PickedImage } from '@/types/domain';

const FORM_INICIAL: OccurrenceFormValues = {
  neighborhood: '',
  address: '',
  description: '',
  reportedCategory: 'ILLEGAL_DUMPING',
};

interface OccurrenceFormProps {
  /** Chamado após o registro bem-sucedido. */
  onCreated: (ocorrencia: OccurrenceDetail) => void;
}

/** Formulário de registro de ocorrência (campos, foto e envio). */
export function OccurrenceForm({ onCreated }: OccurrenceFormProps) {
  const [form, setForm] = useState<OccurrenceFormValues>(FORM_INICIAL);
  const [errors, setErrors] = useState<OccurrenceFormErrors>({});
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [imagem, setImagem] = useState<PickedImage | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  function atualizar(campo: keyof OccurrenceFormValues, valor: string) {
    setForm((atual) => ({ ...atual, [campo]: valor }));
    setErrors((atual) => ({ ...atual, [campo]: undefined }));
  }

  async function escolherImagem(origem: 'camera' | 'galeria') {
    setErro(null);
    try {
      if (Platform.OS !== 'web') {
        const permissao =
          origem === 'camera'
            ? await ImagePicker.requestCameraPermissionsAsync()
            : await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (!permissao.granted) {
          setErro('Permissão negada para acessar a câmera/galeria.');
          return;
        }
      }

      const selecao =
        origem === 'camera'
          ? await ImagePicker.launchCameraAsync({ quality: 0.7, mediaTypes: ['images'] })
          : await ImagePicker.launchImageLibraryAsync({ quality: 0.7, mediaTypes: ['images'] });

      if (selecao.canceled || !selecao.assets?.length) {
        return;
      }
      const asset = selecao.assets[0];
      setImagem({
        uri: asset.uri,
        name: asset.fileName ?? `foto-${Date.now()}.jpg`,
        type: asset.mimeType ?? 'image/jpeg',
      });
    } catch (causa) {
      setErro(describeError(causa));
    }
  }

  async function enviar() {
    const validacao = validateOccurrenceForm(form);
    setErrors(validacao);
    if (!isFormValid(validacao)) {
      return;
    }

    const lat = parseCoordinate(latitude);
    const lon = parseCoordinate(longitude);
    if (Number.isNaN(lat) || Number.isNaN(lon)) {
      setErro('Latitude e longitude devem ser números (ex.: -23.5678).');
      return;
    }

    setEnviando(true);
    setErro(null);
    try {
      const ocorrencia = await api.createOccurrence({
        neighborhood: form.neighborhood,
        address: form.address,
        description: form.description,
        reportedCategory: form.reportedCategory,
        latitude: lat,
        longitude: lon,
        image: imagem ?? undefined,
      });
      onCreated(ocorrencia);
    } catch (causa) {
      setErro(causa instanceof ApiError ? causa.message : describeError(causa));
    } finally {
      setEnviando(false);
    }
  }
return (
    <>
      <Card title="Local">
        <TextField
          label="Bairro *"
          value={form.neighborhood}
          onChangeText={(valor) => atualizar('neighborhood', valor)}
          placeholder="Ex.: Pinheiros"
          error={errors.neighborhood}
          maxLength={120}
          testID="campo-bairro"
        />
        <TextField
          label="Endereço ou referência"
          value={form.address}
          onChangeText={(valor) => atualizar('address', valor)}
          placeholder="Ex.: Rua dos Pinheiros, 120"
          error={errors.address}
          maxLength={255}
        />
        <View style={styles.row}>
          <View style={styles.rowItem}>
            <TextField
              label="Latitude"
              value={latitude}
              onChangeText={setLatitude}
              placeholder="-23.5678"
              keyboardType="numbers-and-punctuation"
            />
          </View>
          <View style={styles.rowItem}>
            <TextField
              label="Longitude"
              value={longitude}
              onChangeText={setLongitude}
              placeholder="-46.6920"
              keyboardType="numbers-and-punctuation"
            />
          </View>
        </View>
      </Card>

      <Card title="Descrição">
        <ChoiceChips
          title="Categoria"
          options={categoryOptions()}
          value={form.reportedCategory as OccurrenceCategory}
          allowClear={false}
          onChange={(valor) => {
            if (valor) {
              atualizar('reportedCategory', valor);
            }
          }}
        />
        <TextField
          label="O que está acontecendo?"
          value={form.description}
          onChangeText={(valor) => atualizar('description', valor)}
          placeholder="Ex.: contêiner transbordando há dois dias"
          error={errors.description}
          multiline
          maxLength={1000}
          hint={`${form.description.length}/1000 caracteres`}
        />
      </Card>

      <Card title="Foto" subtitle="Opcional, mas ajuda na classificação automática">
        {imagem ? (
          <View style={styles.previewWrapper}>
            <Image source={{ uri: imagem.uri }} style={styles.preview} resizeMode="cover" />
            <Button label="Remover foto" variant="ghost" onPress={() => setImagem(null)} />
          </View>
        ) : (
          <View style={styles.photoActions}>
            {Platform.OS !== 'web' ? (
              <Button label="Tirar foto" onPress={() => escolherImagem('camera')} />
            ) : null}
            <Button
              label="Escolher da galeria"
              variant={Platform.OS === 'web' ? 'primary' : 'secondary'}
              onPress={() => escolherImagem('galeria')}
            />
          </View>
        )}
      </Card>

      {erro ? <Text style={styles.error}>{erro}</Text> : null}

      <Button
        label={enviando ? 'Enviando...' : 'Enviar ocorrência'}
        onPress={enviar}
        loading={enviando}
      />
    </>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  rowItem: {
    flexGrow: 1,
    flexBasis: 160,
  },
  photoActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  previewWrapper: {
    gap: spacing.sm,
    alignItems: 'flex-start',
  },
  preview: {
    width: '100%',
    height: 220,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceMuted,
  },
  error: {
    color: colors.danger,
    fontSize: typography.body,
  },
});