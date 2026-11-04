import { buildUploadUrl, extractHost, resolveApiBaseUrl } from '@/services/config';

describe('extractHost', () => {
  it('extrai o host de um hostUri com porta', () => {
    expect(extractHost('192.168.0.10:8081')).toBe('192.168.0.10');
  });

  it('remove esquema e caminho', () => {
    expect(extractHost('exp://192.168.0.10:8081/--/admin')).toBe('192.168.0.10');
    expect(extractHost('http://localhost:19006/')).toBe('localhost');
  });

  it('retorna null para entrada vazia', () => {
    expect(extractHost(undefined)).toBeNull();
    expect(extractHost(null)).toBeNull();
    expect(extractHost('')).toBeNull();
  });
});

describe('resolveApiBaseUrl', () => {
  it('prioriza EXPO_PUBLIC_API_URL e remove a barra final', () => {
    expect(resolveApiBaseUrl({ envUrl: 'https://api.exemplo.com/', hostUri: '192.168.0.10:8081' })).toBe(
      'https://api.exemplo.com',
    );
  });

  it('usa o host do servidor de desenvolvimento com a porta da API', () => {
    expect(resolveApiBaseUrl({ envUrl: '', hostUri: '192.168.0.10:8081' })).toBe(
      'http://192.168.0.10:8000',
    );
  });

  it('cai no fallback local quando não há host', () => {
    expect(resolveApiBaseUrl({ envUrl: '', hostUri: null, fallback: 'http://127.0.0.1:8000' })).toBe(
      'http://127.0.0.1:8000',
    );
  });
});

describe('buildUploadUrl', () => {
  it('monta a URL pública da imagem servida pelo backend', () => {
    expect(buildUploadUrl('abc123.png', 'http://127.0.0.1:8000')).toBe(
      'http://127.0.0.1:8000/uploads/abc123.png',
    );
  });

  it('normaliza a base e o caminho', () => {
    expect(buildUploadUrl('/pasta/abc123.png', 'http://127.0.0.1:8000/')).toBe(
      'http://127.0.0.1:8000/uploads/pasta/abc123.png',
    );
  });
});