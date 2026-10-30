import { useState, useEffect } from "react";
import { Card, Button, Badge, Input, Select, Modal, ConfirmDialog } from "@ilabuporto/design-system";
import { useScheduleStore } from "@/stores/scheduleStore";
import { useAuthStore } from "@/stores/authStore";
import { JUSTIFICATION_OPTIONS } from "@/stores/scheduleStore";
import { unavailabilityService } from "@/services/api";

const DAYS = ["segunda", "terca", "quarta", "quinta", "sexta"];
const HOURS = [1, 2, 3, 4, 5, 6, 7, 8];

export default function TeacherCalendar() {
  const { user } = useAuthStore();
  const { assignments } = useScheduleStore();
  const [unavailabilities, setUnavailabilities] = useState<Array<{
    id: number;
    slot: { dia: string; hora: number };
    justification: string;
  }>>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<{ dia: string; hora: number } | null>(null);
  const [justification, setJustification] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadUnavailabilities();
  }, []);

  const loadUnavailabilities = async () => {
    try {
      const response = await unavailabilityService.getUnavailabilities();
      setUnavailabilities(response.data || []);
    } catch {
      setError("Erro ao carregar indisponibilidades");
    }
  };

  const handleSlotClick = (dia: string, hora: number) => {
    setSelectedSlot({ dia, hora });
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!selectedSlot || !justification) return;
    setLoading(true);
    try {
      await unavailabilityService.createUnavailability({
        teacher_id: 1, // Em produção, viria do perfil do utilizador
        slot: selectedSlot,
        justification,
        reason: "",
      });
      setIsModalOpen(false);
      setSelectedSlot(null);
      setJustification("");
      await loadUnavailabilities();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao salvar");
    } finally {
      setLoading(false);
    }
  };

  const isSlotUnavailable = (dia: string, hora: number) => {
    return unavailabilities.some(
      (u) => u.slot.dia === dia && u.slot.hora === hora
    );
  };

  const isSlotSelected = (dia: string, hora: number) => {
    return selectedSlot?.dia === dia && selectedSlot?.hora === hora;
  };

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Minhas Restrições</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Marque os slots em que não pode lecionar e selecione a justificação.
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500 rounded text-sm text-red-800 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-700">
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300 border-b">Hora</th>
              {DAYS.map((dia) => (
                <th key={dia} className="px-4 py-3 text-center text-sm font-semibold text-gray-600 dark:text-gray-300 border-b">
                  {dia.charAt(0).toUpperCase() + dia.slice(1)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {HOURS.map((hora) => (
              <tr key={hora} className="border-b border-gray-200 dark:border-gray-700">
                <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white border-r border-gray-200 dark:border-gray-700">
                  {hora}h
                </td>
                {DAYS.map((dia) => {
                  const isUnav = isSlotUnavailable(dia, hora);
                  const isSel = isSlotSelected(dia, hora);
                  const assignment = assignments.find(
                    (a) => a.slot.dia === dia && a.slot.hora === hora
                  );
                  return (
                    <td
                      key={`${dia}-${hora}`}
                      className={`px-4 py-2 text-center border-r border-gray-200 dark:border-gray-700 ${
                        isUnav
                          ? "bg-red-100 dark:bg-red-900/30"
                          : isSel
                            ? "bg-brand-50 dark:bg-brand-900/20"
                            : assignment
                              ? "bg-blue-50 dark:bg-blue-900/20"
                              : "bg-white dark:bg-gray-800"
                      } cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors`}
                      onClick={() => handleSlotClick(dia, hora)}
                    >
                      {isUnav ? (
                        <div className="text-xs font-medium text-red-600 dark:text-red-400">✕</div>
                      ) : assignment ? (
                        <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                          {assignment.subject_name || "Aula"}
                        </div>
                      ) : (
                        <div className="text-xs text-gray-400">—</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={isModalOpen}
        title="Marcar Indisponibilidade"
        onClose={() => setIsModalOpen(false)}
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Selecione o motivo da sua indisponibilidade para {selectedSlot?.dia} às {selectedSlot?.hora}h:
          </p>
          <Select
            label="Justificação"
            value={justification}
            onChange={(val: string) => setJustification(val || "")}
            options={JUSTIFICATION_OPTIONS.map((o) => ({ label: o.label, value: o.value }))}
            placeholder="Escolha uma justificação"
          />
          <Input
            label="Motivo adicional (opcional)"
            placeholder="Detalhes adicionais..."
          />
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              disabled={!justification}
              onClick={handleSave}
              className="btn-brand"
              loading={loading}
            >
              Guardar
            </Button>
          </div>
        </div>
      </Modal>

      <div className="mt-6 flex flex-wrap gap-2">
        <Badge variant="neutral">Livre</Badge>
        <Badge variant="info">Aula atribuída</Badge>
        <Badge variant="destructive">Indisponível</Badge>
        <Badge variant="brand">Selecionado</Badge>
      </div>
    </div>
  );
}
