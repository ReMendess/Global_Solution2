import { ApiError, request } from '@/services/api-client';

const BASE = 'http://api.test';

function mockFetch(response: Partial<Response> & { jsonBody?: unknown }) {
  const json = jest.fn().mockResolvedValue(response.jsonBody ?? {});
  const text = jest
    .fn()
    .mockResolvedValue(response.jsonBody === undefined ? '' : JSON.stringify(response.jsonBody));
  const fetchMock = jest.fn().mockResolvedValue({
    ok: response.ok ?? true,
    status: response.status ?? 200,
    json,
    text,
  });
  global.fetch = fetchMock as unknown as typeof fetch;
  return fetchMock;
}

describe('request', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('envia JSON e devolve o corpo tipado', async () => {
    const fetchMock = mockFetch({ jsonBody: { id: 1 } });

    const resultado = await request<{ id: number }>('/api/v1/ocorrencias', {
      baseUrl: BASE,
      method: 'POST',
      body: { neighborhood: 'Pinheiros' },
    });

    expect(resultado).toEqual({ id: 1 });
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe(`${BASE}/api/v1/ocorrencias`);
    expect(init.method).toBe('POST');
    expect(init.headers['Content-Type']).toBe('application/json');
    expect(init.body).toBe(JSON.stringify({ neighborhood: 'Pinheiros' }));
  });

  it('não define Content-Type quando o corpo é FormData', async () => {
    const fetchMock = mockFetch({ jsonBody: { ok: true } });
    const form = new FormData();
    form.append('neighborhood', 'Pinheiros');

    await request('/api/v1/occurrences', { baseUrl: BASE, method: 'POST', body: form });

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers['Content-Type']).toBeUndefined();
    expect(init.body).toBe(form);
  });

  it('envia o cabeçalho X-User-Role quando o perfil é informado', async () => {
    const fetchMock = mockFetch({ jsonBody: { items: [] } });

    await request('/api/v1/occurrences', { baseUrl: BASE, role: 'ADMIN' });

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers['X-User-Role']).toBe('ADMIN');
  });

  it('converte erro HTTP em ApiError com o detail do backend', async () => {
    mockFetch({ ok: false, status: 409, jsonBody: { detail: 'Já existe uma ocorrência aberta.' } });

    await expect(request('/api/v1/occurrences', { baseUrl: BASE })).rejects.toMatchObject({
      status: 409,
      message: 'Já existe uma ocorrência aberta.',
    });
  });

  it('marca falha de rede como ApiError de status 0', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('Failed to fetch')) as unknown as typeof fetch;

    await expect(request('/api/v1/health', { baseUrl: BASE })).rejects.toBeInstanceOf(ApiError);
    await expect(request('/api/v1/health', { baseUrl: BASE })).rejects.toMatchObject({
      status: 0,
      isNetworkError: true,
    });
  });

  it('devolve undefined para respostas 204', async () => {
    mockFetch({ status: 204, ok: true });

    await expect(request('/api/v1/ocorrencias/1', { baseUrl: BASE, method: 'PATCH' })).resolves.toBeUndefined();
  });
});