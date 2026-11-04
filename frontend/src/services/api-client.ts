import type { UserRole } from '@/types/domain';

import { resolveApiBaseUrl } from './config';

/** Erro de API com o status HTTP e a mensagem devolvida pelo backend. */
export class ApiError extends Error {
  readonly status: number;
  readonly payload: unknown;

  constructor(status: number, message: string, payload?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }

  /** Indica que a requisição não chegou ao servidor (rede/offline/CORS). */
  get isNetworkError(): boolean {
    return this.status === 0;
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  /** Corpo JSON ou FormData (nesse caso o Content-Type é definido automaticamente). */
  body?: unknown;
  /** Perfil enviado no cabeçalho X-User-Role (rotas administrativas exigem ADMIN). */
  role?: UserRole;
  signal?: AbortSignal;
  /** Sobrescreve a URL base (usado em testes). */
  baseUrl?: string;
  timeoutMs?: number;
}

const TIMEOUT_MS = 20000;

function buildHeaders(options: RequestOptions, hasJsonBody: boolean): Record<string, string> {
  const headers: Record<string, string> = { Accept: 'application/json' };

  if (hasJsonBody) {
    headers['Content-Type'] = 'application/json';
  }
  if (options.role) {
    headers['X-User-Role'] = options.role;
  }
  return headers;
}

async function parseBody(response: Response): Promise<unknown> {
  const texto = await response.text();
  if (!texto) {
    return null;
  }
  try {
    return JSON.parse(texto) as unknown;
  } catch {
    return texto;
  }
}

function extractDetail(payload: unknown, fallback: string): string {
  if (payload && typeof payload === 'object' && 'detail' in payload) {
    const detalhe = (payload as { detail: unknown }).detail;
    if (typeof detalhe === 'string' && detalhe.trim().length > 0) {
      return detalhe;
    }
  }
  return fallback;
}

/**
 * Executa uma requisição HTTP contra a API do Cidade Limpa.
 *
 * Converte falhas em `ApiError`, com a mensagem em pt-BR devolvida pelo backend.
 */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const baseUrl = options.baseUrl ?? resolveApiBaseUrl();
  const url = `${baseUrl}${path}`;
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
  const hasJsonBody = options.body !== undefined && !isFormData;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      method: options.method ?? 'GET',
      headers: buildHeaders(options, hasJsonBody),
      body: isFormData
        ? (options.body as FormData)
        : hasJsonBody
          ? JSON.stringify(options.body)
          : undefined,
      signal: options.signal ?? controller.signal,
    });

    if (!response.ok) {
      const payload = await parseBody(response);
      throw new ApiError(
        response.status,
        extractDetail(payload, `Falha na requisição (HTTP ${response.status}).`),
        payload,
      );
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await parseBody(response)) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    const mensagem =
      'Não foi possível falar com a API do Cidade Limpa. Verifique se o backend está em execução.';
    throw new ApiError(0, mensagem, error);
  } finally {
    clearTimeout(timeout);
  }
}