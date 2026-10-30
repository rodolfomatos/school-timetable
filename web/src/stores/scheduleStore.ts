import { create } from "zustand";
import type {
  ScheduleVersion,
  ScheduleAssignment,
  Slot,
  JustificationOption,
  JUSTIFICATION_OPTIONS,
} from "@/types";

interface ScheduleState {
  currentVersion: ScheduleVersion | null;
  assignments: ScheduleAssignment[];
  isLoading: boolean;
  solverStatus: {
    taskId: string | null;
    status: "pending" | "running" | "completed" | "failed" | null;
    score: number | null;
    error: string | null;
  };
  setCurrentVersion: (version: ScheduleVersion | null) => void;
  setAssignments: (assignments: ScheduleAssignment[]) => void;
  setLoading: (loading: boolean) => void;
  setSolverStatus: (status: {
    taskId: string | null;
    status: "pending" | "running" | "completed" | "failed" | null;
    score: number | null;
    error: string | null;
  }) => void;
  clearSchedule: () => void;
  getAssignmentsBySlot: (slot: Slot) => ScheduleAssignment[];
  getAssignmentsByTeacher: (teacherId: number) => ScheduleAssignment[];
  getAssignmentsByClass: (classId: number) => ScheduleAssignment[];
  getAssignmentsByRoom: (roomId: number) => ScheduleAssignment[];
}

export const useScheduleStore = create<ScheduleState>((set, get) => ({
  currentVersion: null,
  assignments: [],
  isLoading: false,
  solverStatus: { taskId: null, status: null, score: null, error: null },
  setCurrentVersion: (version) => set({ currentVersion: version }),
  setAssignments: (assignments) => set({ assignments }),
  setLoading: (loading) => set({ isLoading: loading }),
  setSolverStatus: (status) => set({ solverStatus: status }),
  clearSchedule: () => set({ currentVersion: null, assignments: [] }),
  getAssignmentsBySlot: (slot) => {
    return get().assignments.filter(
      (a) => a.slot.dia === slot.dia && a.slot.hora === slot.hora
    );
  },
  getAssignmentsByTeacher: (teacherId) => {
    return get().assignments.filter((a) => a.teacher_id === teacherId);
  },
  getAssignmentsByClass: (classId) => {
    return get().assignments.filter((a) => a.class_id === classId);
  },
  getAssignmentsByRoom: (roomId) => {
    return get().assignments.filter((a) => a.room_id === roomId);
  },
}));

export { JUSTIFICATION_OPTIONS, type JustificationOption };
