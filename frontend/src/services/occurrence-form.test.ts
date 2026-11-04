import { buildOccurrenceFormData, toUploadPart } from '@/services/occurrence-form';

const imagem = { uri: 'file:///tmp/foto.jpg', name: 'foto.jpg', type: 'image/jpeg' };

describe('toUploadPart', () => {
  it('no nativo devolve o objeto { uri, name, type }', async () => {
    await expect(toUploadPart(imagem, 'ios')).resolves.toEqual(imagem);
  });

  it('na web converte a imagem em Blob', async () => {
    const blob = new Blob(['conteudo'], { type: 'image/jpeg' });
    const fetchMock = jest.fn().mockResolvedValue({ blob: () => Promise.resolve(blob) });
    global.fetch = fetchMock as unknown as typeof fetch;

    await expect(toUploadPart(imagem, 'web')).resolves.toBe(blob);
    expect(fetchMock).toHaveBeenCalledWith('file:///tmp/foto.jpg');
  });
});

describe('buildOccurrenceFormData', () => {
  it('envia apenas os campos preenchidos', async () => {
    const form = await buildOccurrenceFormData(
      { neighborhood: '  Pinheiros ', address: '', description: '' },
      'ios',
    );

    expect(form.get('neighborhood')).toBe('Pinheiros');
    expect(form.get('address')).toBeNull();
    expect(form.get('description')).toBeNull();
    expect(form.get('image')).toBeNull();
  });

  it('inclui categoria, coordenadas e imagem', async () => {
    const form = await buildOccurrenceFormData(
      {
        neighborhood: 'Butantã',
        reportedCategory: 'OVERFLOW',
        latitude: -23.5678,
        longitude: -46.692,
        image: imagem,
      },
      'ios',
    );

    expect(form.get('reported_category')).toBe('OVERFLOW');
    expect(form.get('latitude')).toBe('-23.5678');
    expect(form.get('longitude')).toBe('-46.692');
    // O FormData do ambiente de teste converte o objeto em texto; o formato exato
    // do part nativo é verificado em toUploadPart.
    expect(form.get('image')).not.toBeNull();
  });

  it('ignora coordenadas inválidas', async () => {
    const form = await buildOccurrenceFormData(
      { neighborhood: 'Santana', latitude: Number.NaN, longitude: Number.POSITIVE_INFINITY },
      'ios',
    );

    expect(form.get('latitude')).toBeNull();
    expect(form.get('longitude')).toBeNull();
  });
});