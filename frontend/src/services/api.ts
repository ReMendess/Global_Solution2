import type {
  AlertLevel,
  ContainerAlertSummary,
  ContainerList,
  Container,
  DashboardSummary,
  EnumsPayload,
  Health,
  NeighborhoodRanking,
  NewOccurrenceInput,
  OccurrenceDetail,
  OccurrenceFilters,
  OccurrenceList,
  OccurrenceStatus,
  SensorReadingList,
} from '@/types/domain';

import { request } from './api-client';
import { buildOccurrenceFormData } from './occurrence-form';

const BASE = '/api/v1';

function queryString(params: Record<string, string | number | boolean | undefined>): string {
  const entradas = Object.entries(params).filter(([, valor]) => valor !== undefined && valor !== '');
  if (entradas.length === 0) {
    return '';
  }
  const busca = entradas
    .map(([chave, valor]) => `${encodeURIComponent(chave)}=${encodeURIComponent(String(valor))}`)
    .join('&');
  return `?${busca}`;
}

/** Cliente da API do Cidade Limpa (único ponto de acesso HTTP do frontend). */
export const api = {
  /** GET /health */
  health: () => request<Health>('/health'),

  /** GET /api/v1/meta/enums */
  enums: () => request<EnumsPayload>(`${BASE}/meta/enums`),

  /** POST /api/v1/occurrences (multipart) */
  createOccurrence: async (input: NewOccurrenceInput): Promise<OccurrenceDetail> => {
    const form = await buildOccurrenceFormData(input);
    return request<OccurrenceDetail>(`${BASE}/occurrences`, { method: 'POST', body: form });
  },

  /** GET /api/v1/occurrences/protocol/{protocol} */
  occurrenceByProtocol: (protocol: string) =>
    request<OccurrenceDetail>(`${BASE}/occurrences/protocol/${encodeURIComponent(protocol.trim())}`),

  /** GET /api/v1/occurrences (perfil ADMIN) */
  listOccurrences: (filters: OccurrenceFilters = {}) =>
    request<OccurrenceList>(
      `${BASE}/occurrences${queryString({
        status: filters.status,
        category: filters.category,
        priority: filters.priority,
        neighborhood: filters.neighborhood,
        needs_human_review: filters.needsHumanReview,
        limit: filters.limit,
        offset: filters.offset,
      })}`,
      { role: 'ADMIN' },
    ),

  /** GET /api/v1/occurrences/{id} (perfil ADMIN) */
  occurrenceDetail: (id: number) =>
    request<OccurrenceDetail>(`${BASE}/occurrences/${id}`, { role: 'ADMIN' }),

  /** PATCH /api/v1/occurrences/{id}/status (perfil ADMIN) */
  updateOccurrenceStatus: (id: number, status: OccurrenceStatus, note?: string) =>
    request<OccurrenceDetail>(`${BASE}/occurrences/${id}/status`, {
      method: 'PATCH',
      role: 'ADMIN',
      body: { status, note: note?.trim() ? note.trim() : undefined },
    }),

  /** GET /api/v1/containers (perfil ADMIN) */
  listContainers: (params: { neighborhood?: string; alertLevel?: AlertLevel } = {}) =>
    request<ContainerList>(
      `${BASE}/containers${queryString({
        neighborhood: params.neighborhood,
        alert_level: params.alertLevel,
      })}`,
      { role: 'ADMIN' },
    ),

  /** GET /api/v1/containers/{code} */
  container: (code: string) =>
    request<Container>(`${BASE}/containers/${encodeURIComponent(code)}`),

  /** GET /api/v1/containers/{code}/readings (perfil ADMIN) */
  containerReadings: (code: string, params: { limit?: number; offset?: number } = {}) =>
    request<SensorReadingList>(
      `${BASE}/containers/${encodeURIComponent(code)}/readings${queryString({
        limit: params.limit,
        offset: params.offset,
      })}`,
      { role: 'ADMIN' },
    ),

  /** GET /api/v1/dashboard/summary (perfil ADMIN) */
  dashboardSummary: () =>
    request<DashboardSummary>(`${BASE}/dashboard/summary`, { role: 'ADMIN' }),

  /** GET /api/v1/dashboard/containers (perfil ADMIN) */
  dashboardContainers: () =>
    request<ContainerAlertSummary>(`${BASE}/dashboard/containers`, { role: 'ADMIN' }),

  /** GET /api/v1/dashboard/neighborhoods (perfil ADMIN) */
  dashboardNeighborhoods: (limit = 8) =>
    request<NeighborhoodRanking>(`${BASE}/dashboard/neighborhoods${queryString({ limit })}`, {
      role: 'ADMIN',
    }),
};

export type Api = typeof api;