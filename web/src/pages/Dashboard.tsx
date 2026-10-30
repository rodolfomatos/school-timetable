import { Card, Button, Badge, StatCard } from "@ilabuporto/design-system";
import { useAuthStore } from "@/stores/authStore";
import { scheduleService } from "@/services/api";
import { useScheduleStore } from "@/stores/scheduleStore";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const { user } = useAuthStore();
  const { setSolverStatus } = useScheduleStore();
  const [stats, setStats] = useState({
    totalRooms: 0,
    totalSubjects: 0,
    totalClasses: 0,
    totalTeachers: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Carregar estatísticas (mock - em produção viria da API)
    setStats({
      totalRooms: 8,
      totalSubjects: 12,
      totalClasses: 10,
      totalTeachers: 15,
    });
    setLoading(false);
  }, []);

  const handleGenerate = async () => {
    setSolverStatus({
      taskId: null,
      status: "running",
      score: null,
      error: null,
    });
    try {
      const response = await scheduleService.runSolver({
        solver: "simulated_annealing",
        time_limit_seconds: 60,
      });
      const { data } = response;
      setSolverStatus({
        taskId: data.task_id,
        status: "running",
        score: null,
        error: null,
      });

      // Polling do status
      const pollStatus = async () => {
        for (let i = 0; i < 12; i++) {
          await new Promise((r) => setTimeout(r, 2000));
          const statusResp = await scheduleService.getSolverStatus(
            data.task_id
          );
          const statusData = statusResp.data;
          setSolverStatus({
            taskId: data.task_id,
            status: statusData.status,
            score: statusData.score,
            error: statusData.error,
          });
          if (statusData.status === "completed" || statusData.status === "failed") {
            break;
          }
        }
      };
      pollStatus();
    } catch (err: any) {
      setSolverStatus({
        taskId: null,
        status: "failed",
        score: null,
        error: err.response?.data?.detail || "Erro ao executar o solver",
      });
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Bem-vindo, {user?.full_name || user?.email}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard label="Salas" value={stats.totalRooms} variant="info" />
        <StatCard label="Disciplinas" value={stats.totalSubjects} variant="brand" />
        <StatCard label="Turmas" value={stats.totalClasses} variant="accent" />
        <StatCard label="Docentes" value={stats.totalTeachers} variant="warning" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Gerar Horário</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Execute o solver para gerar um horário automático respeitando todas as restrições.
          </p>
          <Button
            onClick={handleGenerate}
            disabled={loading}
            variant="primary"
            className="w-full btn-brand"
          >
            {setSolverStatus.toString().includes("running") ? "A processar..." : "Gerar Horário"}
          </Button>
          {useScheduleStore.getState().solverStatus.status === "completed" && (
            <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-500 rounded">
              <p className="text-sm text-green-800 dark:text-green-300 font-medium">
                ✓ Horário gerado com sucesso!
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Score: {useScheduleStore.getState().solverStatus.score}
              </p>
            </div>
          )}
          {useScheduleStore.getState().solverStatus.status === "failed" && (
            <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500 rounded">
              <p className="text-sm text-red-800 dark:text-red-300 font-medium">
                ⚠ Erro ao gerar horário
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {useScheduleStore.getState().solverStatus.error}
              </p>
            </div>
          )}
        </Card>

        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Ações Rápidas</h3>
          <div className="space-y-3">
            <Button
              variant="secondary"
              onClick={() => (window.location.href = "/teacher/calendar")}
              className="w-full"
            >
              Minhas Restrições
            </Button>
            <Button
              variant="secondary"
              onClick={() => (window.location.href = "/schedule")}
              className="w-full"
            >
              Ver Horário
            </Button>
            <Button
              variant="secondary"
              onClick={() => (window.location.href = "/disputes")}
              className="w-full"
            >
              Contestações
            </Button>
          </div>
        </Card>

        {user && (user.role === "admin" || user.role === "coordinator") && (
          <Card>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Gestão</h3>
            <div className="space-y-3">
              <Button
                variant="secondary"
                onClick={() => (window.location.href = "/admin/users")}
                className="w-full"
              >
                Utilizadores
              </Button>
              <Button
                variant="secondary"
                onClick={() => (window.location.href = "/admin/rooms")}
                className="w-full"
              >
                Salas
              </Button>
              <Button
                variant="secondary"
                onClick={() => (window.location.href = "/admin/subjects")}
                className="w-full"
              >
                Disciplinas
              </Button>
              <Button
                variant="secondary"
                onClick={() => (window.location.href = "/admin/classes")}
                className="w-full"
              >
                Turmas
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
