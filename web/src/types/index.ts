export type Role = "admin" | "teacher" | "student" | "coordinator";

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: Role;
  institution_id?: string;
  is_active: boolean;
  created_at: string;
}

export interface Course {
  id: number;
  code: string;
  name: string;
}

export interface Room {
  id: number;
  name: string;
  capacity: number;
  room_type: "normal" | "laboratorio" | "anatomia";
  allowed_courses?: string[];
  reserved_times?: Array<{ dia: string; hora: number }>;
  setup_before: number;
  cleanup_after: number;
  course_id?: number;
  is_active: boolean;
}

export interface Subject {
  id: number;
  code: string;
  name: string;
  weekly_load: number;
  room_type_required: string;
  periodicity: "semanal" | "quinzenal" | "modulo_semestre";
  weeks_active?: number[];
  course_id: number;
  is_active: boolean;
}

export interface SchoolClass {
  id: number;
  name: string;
  course_id: number;
  year: number;
  student_count: number;
  weeks_active?: number[];
  is_active: boolean;
}

export interface Teacher {
  id: number;
  user_id: number;
  employee_code?: string;
  day_off_preferred?: string;
  morning_preferred: boolean;
  lunch_sacred: boolean;
  commute_time: number;
  availability?: Record<string, number[]>;
  is_active: boolean;
}

export interface Slot {
  dia: string;
  hora: number;
}

export interface ScheduleAssignment {
  id: number;
  version_id: number;
  class_id: number;
  subject_id: number;
  teacher_id: number;
  room_id: number;
  slot: Slot;
  created_at: string;
  class_name?: string;
  subject_name?: string;
  teacher_name?: string;
  room_name?: string;
}

export interface ScheduleVersion {
  id: number;
  institution_id?: string;
  status: "draft" | "published" | "archived";
  solver_used?: string;
  score?: number;
  hard_violations: number;
  soft_penalties: number;
  created_at: string;
  published_at?: string;
}

export interface Unavailability {
  id: number;
  teacher_id: number;
  slot: Slot;
  justification: string;
  reason?: string;
  created_at: string;
}

export interface JustificationOption {
  value: string;
  label: string;
}

export const JUSTIFICATION_OPTIONS: JustificationOption[] = [
  { value: "deslocamento", label: "Deslocamento entre instituições" },
  { value: "folga", label: "Dia de folga preferido" },
  { value: "almoço", label: "Hora de almoço" },
  { value: "compromisso", label: "Compromisso pessoal" },
  { value: "doença", label: "Doença / indisponibilidade temporária" },
  { value: "outro", label: "Outro" },
];

export interface Dispute {
  id: number;
  teacher_id: number;
  assignment_id: number;
  reason: string;
  justification: string;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
  resolved_at?: string;
  resolved_by?: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface SolverRunRequest {
  institution_id?: string;
  solver?: "cp_sat" | "tabu_search" | "simulated_annealing";
  time_limit_seconds?: number;
}

export interface SolverStatus {
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  schedule_version_id?: number;
  score?: number;
  hard_violations?: number;
  soft_penalties?: number;
  error?: string;
}
