import { useCallback, useEffect, useRef, useState } from 'react';

import { ApiError } from '@/services/api-client';

export interface AsyncState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

/** Extrai uma mensagem amigável (pt-BR) de qualquer erro recebido. */
export function describeError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return 'Não foi possível carregar as informações.';
}

/**
 * Executa uma chamada assíncrona e expõe dados, erro e estado de carregamento.
 *
 * `loader` deve ser estável (useCallback) ou depender apenas de `deps`.
 */
export function useAsync<T>(loader: () => Promise<T>, deps: unknown[] = []): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [nonce, setNonce] = useState(0);
  const ativo = useRef(true);

  useEffect(() => {
    ativo.current = true;
    return () => {
      ativo.current = false;
    };
  }, []);

  useEffect(() => {
    let cancelado = false;
    setLoading(true);
    setError(null);

    loader()
      .then((resultado) => {
        if (!cancelado && ativo.current) {
          setData(resultado);
        }
      })
      .catch((causa: unknown) => {
        if (!cancelado && ativo.current) {
          setError(describeError(causa));
        }
      })
      .finally(() => {
        if (!cancelado && ativo.current) {
          setLoading(false);
        }
      });

    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  const reload = useCallback(() => setNonce((valor) => valor + 1), []);

  return { data, error, loading, reload };
}