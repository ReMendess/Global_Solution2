/**
 * Tipos do domínio, espelhando os schemas Pydantic do backend (docs/API_SPEC.md).
 * Os valores dos enums são os mesmos retornados por GET /api/v1/meta/enums.
 */

export type OccurrenceCategory =
  | 'ILLEGAL_DUMPING'
  | 'OVERFLOW'
  | 'DAMAGED_CONTAINER'
  | 'OTHER';

export type OccurrenceStatus =
  | 'OPEN'
  | 'CLASSIFIED'
  | 'PENDING_DISPATCH'
  | 'DISPATCHED'
  | 'IN_PROGRESS'
  | 'RESOLVED'
  | 'REJECTED';

export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AlertLevel = 'NORMAL' | 'HIGH' | 'CRITICAL';

export type UserRole = 'CITIZEN' | 'ADMIN';

export type ModelLabel = 'REGULAR' | 'IRREGULAR';

export interface OccurrenceImage {
  id: number;
  file_path: string;
  content_type: string;
  size_bytes: number;
  width: number | null;
  height: number | null;
  is_simulated: boolean;
  created_at: string;
}

export interface StatusHistoryEntry {
  id: number;
  from_status: OccurrenceStatus | null;
  to_status: OccurrenceStatus;
  note: string | null;
  changed_by: string;
  created_at: string;
}

export interface Occurrence {
  id: number;
  protocol: string;
  category: OccurrenceCategory;
  status: OccurrenceStatus;
  priority: Priority;
  description: string | null;
  neighborhood: string;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  model_label: ModelLabel | null;
  confidence: number | null;
  needs_human_review: boolean;
  model_version: string | null;
  dispatch_protocol: string | null;
  is_simulated: boolean;
  created_at: string;
  updated_at: string;
}

export interface OccurrenceDetail extends Occurrence {
  images: OccurrenceImage[];
  status_history: StatusHistoryEntry[];
}

export interface Paginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export type OccurrenceList = Paginated<Occurrence>;

export interface Container {
  id: number;
  code: string;
  neighborhood: string;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  capacity_liters: number;
  current_fill_level: number;
  alert_level: AlertLevel;
  is_simulated: boolean;
  last_reading_at: string | null;
  created_at: string;
}

export interface ContainerList {
  items: Container[];
  total: number;
}

export interface SensorReading {
  id: number;
  sensor_id: string;
  container_code: string;
  fill_level: number;
  distance_cm: number | null;
  alert_level: AlertLevel;
  is_simulated: boolean;
  measured_at: string;
  created_at: string;
}

export type SensorReadingList = Paginated<SensorReading>;

export interface DashboardSummary {
  total_occurrences: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
  needs_human_review: number;
  average_resolution_hours: number | null;
}

export interface ContainerAlertSummary {
  total_containers: number;
  by_alert_level: Record<string, number>;
  critical_codes: string[];
}

export interface NeighborhoodItem {
  neighborhood: string;
  total: number;
}

export interface NeighborhoodRanking {
  items: NeighborhoodItem[];
  limit: number;
}

export interface EnumsPayload {
  categories: string[];
  model_labels: string[];
  statuses: string[];
  priorities: string[];
  alert_levels: string[];
  user_roles: string[];
  rpa_statuses: string[];
  allowed_transitions: Record<string, string[]>;
}

export interface Health {
  status: string;
  version: string;
  environment: string;
  database: string;
  model_loaded: boolean;
}

export interface OccurrenceFilters {
  status?: OccurrenceStatus;
  category?: OccurrenceCategory;
  priority?: Priority;
  neighborhood?: string;
  needsHumanReview?: boolean;
  limit?: number;
  offset?: number;
}

/** Imagem escolhida pelo cidadão (câmera ou galeria). */
export interface PickedImage {
  uri: string;
  name: string;
  type: string;
}

/** Dados do formulário de registro de ocorrência. */
export interface NewOccurrenceInput {
  neighborhood: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  description?: string;
  reporterName?: string;
  reportedCategory?: OccurrenceCategory;
  image?: PickedImage;
}
/** Resposta do agente a uma mensagem do usuário. */
export interface AgentMessage {
  session_id: string;
  intent: string;
  tool_used: string | null;
  response: string;
  data: Record<string, unknown> | null;
}

/** Item do histórico de conversa com o agente. */
export interface AgentInteractionRead {
  id: number;
  session_id: string;
  intent: string;
  message: string;
  response: string;
  tool_used: string | null;
  tool_payload: string | null;
  created_at: string;
}

/** Histórico completo de uma sessão do agente. */
export interface AgentSession {
  session_id: string;
  interactions: AgentInteractionRead[];
  total: number;
}