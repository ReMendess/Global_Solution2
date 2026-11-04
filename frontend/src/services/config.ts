import Constants from 'expo-constants';

/** Porta padrão do backend FastAPI (ver docs/ENVIRONMENT.md §5). */
export const DEFAULT_API_PORT = 8000;

const FALLBACK_BASE_URL = `http://127.0.0.1:${DEFAULT_API_PORT}`;

export interface ResolveApiBaseUrlInput {
  /** Valor de EXPO_PUBLIC_API_URL, quando definido. */
  envUrl?: string;
  /** Host do servidor de desenvolvimento (ex.: "192.168.0.10:8081"). */
  hostUri?: string | null;
  /** Fallback usado quando não há host identificável. */
  fallback?: string;
}

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}

/**
 * Extrai apenas o host de um `hostUri` do Expo (remove esquema, caminho e porta).
 */
export function extractHost(hostUri?: string | null): string | null {
  if (!hostUri) {
    return null;
  }
  const semEsquema = hostUri.replace(/^[a-z]+:\/\//i, '');
  const semCaminho = semEsquema.split('/')[0];
  const host = semCaminho.split(':')[0];
  return host.length > 0 ? host : null;
}

/**
 * Resolve a URL base da API.
 *
 * Prioridade:
 * 1. `EXPO_PUBLIC_API_URL` (permite apontar para qualquer servidor);
 * 2. host do servidor de desenvolvimento do Expo (funciona no Expo Go e na web);
 * 3. fallback local (`http://127.0.0.1:8000`).
 */
export function resolveApiBaseUrl(input: ResolveApiBaseUrlInput = {}): string {
  const envUrl = input.envUrl ?? process.env.EXPO_PUBLIC_API_URL;
  if (envUrl && envUrl.trim().length > 0) {
    return stripTrailingSlash(envUrl.trim());
  }

  const hostUri =
    input.hostUri ?? Constants.expoConfig?.hostUri ?? Constants.expoGoConfig?.debuggerHost;
  const host = extractHost(hostUri);
  if (host) {
    return `http://${host}:${DEFAULT_API_PORT}`;
  }

  return stripTrailingSlash(input.fallback ?? FALLBACK_BASE_URL);
}

/**
 * Monta a URL pública de uma imagem enviada ao backend.
 * O FastAPI serve `data/uploads` em `/uploads` (ver backend/app/main.py).
 */
export function buildUploadUrl(filePath: string, baseUrl?: string): string {
  const base = baseUrl ?? resolveApiBaseUrl();
  return `${stripTrailingSlash(base)}/uploads/${filePath.replace(/^\/+/, '')}`;
}