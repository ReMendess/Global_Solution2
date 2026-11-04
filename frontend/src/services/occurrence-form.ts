import { Platform } from 'react-native';

import type { NewOccurrenceInput, PickedImage } from '@/types/domain';

type UploadPart = Blob | { uri: string; name: string; type: string };

/**
 * Converte a imagem escolhida no formato esperado por cada plataforma.
 *
 * - Web: precisa de um `Blob` real (o navegador não entende `{ uri }`).
 * - Nativo (iOS/Android): React Native envia `{ uri, name, type }` no multipart.
 */
export async function toUploadPart(
  image: PickedImage,
  platform: string = Platform.OS,
): Promise<UploadPart> {
  if (platform === 'web') {
    const resposta = await fetch(image.uri);
    return await resposta.blob();
  }
  return { uri: image.uri, name: image.name, type: image.type };
}

/**
 * Monta o `FormData` do registro de ocorrência.
 *
 * Campos opcionais vazios são omitidos para não enviar strings em branco à API.
 */
export async function buildOccurrenceFormData(
  input: NewOccurrenceInput,
  platform: string = Platform.OS,
): Promise<FormData> {
  const form = new FormData();

  form.append('neighborhood', input.neighborhood.trim());

  if (input.address?.trim()) {
    form.append('address', input.address.trim());
  }
  if (input.description?.trim()) {
    form.append('description', input.description.trim());
  }
  if (input.reporterName?.trim()) {
    form.append('reporter_name', input.reporterName.trim());
  }
  if (input.reportedCategory) {
    form.append('reported_category', input.reportedCategory);
  }
  if (typeof input.latitude === 'number' && Number.isFinite(input.latitude)) {
    form.append('latitude', String(input.latitude));
  }
  if (typeof input.longitude === 'number' && Number.isFinite(input.longitude)) {
    form.append('longitude', String(input.longitude));
  }
  if (input.image) {
    const parte = await toUploadPart(input.image, platform);
    form.append('image', parte as unknown as Blob);
  }

  return form;
}