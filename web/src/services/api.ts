import axios, { AxiosError } from "axios";
import { useAuthStore } from "@/stores/authStore";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para adicionar o token de autorização
api.interceptors.request.use(
  (config) => {
    const { token } = useAuthStore.getState();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros de autenticação (401)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; refresh_token: string }>("/auth/login", {
      email,
      password,
    }),
  register: (data: {
    email: string;
    password: string;
    full_name?: string;
    role?: string;
    institution_id?: string;
  }) => api.post("/auth/register", data),
  refresh: (refreshToken: string) =>
    api.post<{ access_token: string; refresh_token: string }>("/auth/refresh", {
      refresh_token: refreshToken,
    }),
  getMe: () => api.get("/users/me"),
  listUsers: () => api.get("/users"),
  updateUser: (id: number, data: Record<string, unknown>) =>
    api.patch(`/users/${id}`, data),
};

export const schoolService = {
  // Cursos
  getCourses: () => api.get("/schools/courses"),
  createCourse: (data: Record<string, unknown>) =>
    api.post("/schools/courses", data),
  updateCourse: (id: number, data: Record<string, unknown>) =>
    api.patch(`/schools/courses/${id}`, data),
  deleteCourse: (id: number) => api.delete(`/schools/courses/${id}`),

  // Salas
  getRooms: () => api.get("/schools/rooms"),
  createRoom: (data: Record<string, unknown>) =>
    api.post("/schools/rooms", data),
  updateRoom: (id: number, data: Record<string, unknown>) =>
    api.patch(`/schools/rooms/${id}`, data),
  deleteRoom: (id: number) => api.delete(`/schools/rooms/${id}`),

  // Disciplinas
  getSubjects: () => api.get("/schools/subjects"),
  createSubject: (data: Record<string, unknown>) =>
    api.post("/schools/subjects", data),
  updateSubject: (id: number, data: Record<string, unknown>) =>
    api.patch(`/schools/subjects/${id}`, data),
  deleteSubject: (id: number) => api.delete(`/schools/subjects/${id}`),

  // Turmas
  getClasses: () => api.get("/schools/classes"),
  createClass: (data: Record<string, unknown>) => api.post("/schools/classes", data),
  updateClass: (id: number, data: Record<string, unknown>) =>
    api.patch(`/schools/classes/${id}`, data),
  deleteClass: (id: number) => api.delete(`/schools/classes/${id}`),
};

export const scheduleService = {
  runSolver: (data: {
    institution_id?: string;
    solver?: "cp_sat" | "tabu_search" | "simulated_annealing";
    time_limit_seconds?: number;
  }) => api.post("/scheduler/run", data),
  getSolverStatus: (taskId: string) =>
    api.get(`/scheduler/status/${taskId}`),
  getVersions: () => api.get("/schedule/versions"),
  getAssignments: (versionId: number) =>
    api.get(`/schedule/versions/${version_id}/assignments`.replace("{version_id}", String(versionId))),
};

export const disputeService = {
  createDispute: (data: {
    assignment_id: number;
    reason: string;
    justification: string;
  }) => api.post("/disputes", data),
  listDisputes: () => api.get("/disputes"),
  updateDispute: (id: number, status: "accepted" | "rejected") =>
    api.patch(`/disputes/${id}`, { status }),
};

export const unavailabilityService = {
  getUnavailabilities: () => api.get("/unavailability"),
  createUnavailability: (data: {
    teacher_id: number;
    slot: { dia: string; hora: number };
    justification: string;
    reason?: string;
  }) => api.post("/unavailability", data),
};

export default api;
