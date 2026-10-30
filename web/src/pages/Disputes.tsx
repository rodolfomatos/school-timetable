import { Card, Button, Badge, Input, Table, Modal } from "@ilabuporto/design-system";
import { useScheduleStore } from "@/stores/scheduleStore";
import { useAuthStore } from "@/stores/authStore";
import { disputeService } from "@/services/api";
import { useEffect, useState } from "react";

export default function Disputes() {
  const { user } = useAuthStore();
  const { assignments } = useScheduleStore();
  const [disputes, setDisputes] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<any>(null);
  const [reason, setReason] = useState("");
  const [justification, setJustification] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDisputes();
  }, []);

  const loadDisputes = async () => {
    try {
      const response = await disputeService.listDisputes();
      setDisputes(response.data || []);
    } catch {
      setError("Erro ao carregar contestações");
    }
  };

  const handleContest = (assignment: any) => {
    setSelectedAssignment(assignment);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    if (!selectedAssignment || !reason || !justification) return;
    setLoading(true);
    try {
      await disputeService.createDispute({
        assignment_id: selectedAssignment.id,
        reason,
        justification,
      });
      setIsModalOpen(false);
      setSelectedAssignment(null);
      setReason("");
      setJustification("");
      await loadDisputes();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao submeter contestação");
    } finally {
      setLoading(false);
    }
  };

  const isTeacher = user?.role === "teacher";
  const isAdmin = user?.role === "admin" || user?.role === "coordinator";

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Contestações</h1>
        <p className="text-gray-600 dark:text-gray-400">
          {isTeacher
            ? "Conteste horários atribuídos a si ou visualize o estado das suas contestações."
            : "Gerencie as contestações dos docentes e aceite ou rejeite."}
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500 rounded text-sm text-red-800 dark:text-red-300">
          {error}
        </div>
      )}

      {isTeacher && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Suas Aulas Atribuídas</h3>
          <div className="overflow-x-auto">
            <Table columns={["Disciplina", "Dia", "Hora", "Sala", "Ação"]} data={assignments.slice(0, 10)} />
          </div>
          <div className="mt-4 space-y-3">
            {assignments.slice(0, 5).map((a) => (
              <div key={a.id} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{a.subject_name || "Aula"}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {a.slot.dia} às {a.slot.hora}h — {a.room_name || "Sala"}
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => handleContest(a)}
                  className="text-sm"
                >
                  Contestar
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {isAdmin && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Contestações Pendentes</h3>
          {disputes.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Não há contestações pendentes.</p>
          ) : (
            <div className="space-y-2">
              {disputes.map((d) => (
                <div key={d.id} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{d.reason}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {d.justification} — Docente #{d.teacher_id}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        disputeService.updateDispute(d.id, "accepted");
                        setDisputes(disputes.filter((x) => x.id !== d.id));
                      }}
                    >
                      Aceitar
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => {
                        disputeService.updateDispute(d.id, "rejected");
                        setDisputes(disputes.filter((x) => x.id !== d.id));
                      }}
                    >
                      Rejeitar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        title="Contestar Aula"
        onClose={() => setIsModalOpen(false)}
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Contestar a aula de <strong>{selectedAssignment?.subject_name || "Desconhecida"}</strong> em{" "}
            {selectedAssignment?.slot.dia} às {selectedAssignment?.slot.hora}h
          </p>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Motivo</label>
            <Input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Explique o motivo da contestação"
              required
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Justificação</label>
            <Select
              label="Justificação pré-definida"
              value={justification}
              onChange={(val: string) => setJustification(val || "")}
              options={[
                { label: "Deslocamento entre instituições", value: "deslocamento" },
                { label: "Dia de folga preferido", value: "folga" },
                { label: "Hora de almoço", value: "almoço" },
                { label: "Compromisso pessoal", value: "compromisso" },
                { label: "Doença / indisponibilidade temporária", value: "doença" },
                { label: "Outro", value: "outro" },
              ]}
              placeholder="Escolha uma justificação"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              disabled={!reason || !justification}
              onClick={handleSubmit}
              className="btn-brand"
              loading={loading}
            >
              Submeter Contestação
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
