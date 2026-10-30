import { Card, Button, Badge, Table, Tabs } from "@ilabuporto/design-system";
import { useScheduleStore } from "@/stores/scheduleStore";
import { useAuthStore } from "@/stores/authStore";
import { scheduleService } from "@/services/api";
import { useEffect, useState } from "react";

const DAYS = ["segunda", "terca", "quarta", "quinta", "sexta"];
const HOURS = [1, 2, 3, 4, 5, 6, 7, 8];

export default function ScheduleTable() {
  const { user } = useAuthStore();
  const { assignments, currentVersion, setAssignments } = useScheduleStore();
  const [viewMode, setViewMode] = useState<"class" | "teacher" | "room">("class");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadVersions();
  }, []);

  const loadVersions = async () => {
    setLoading(true);
    try {
      const response = await scheduleService.getVersions();
      const versions = response.data || [];
      if (versions.length > 0) {
        const latest = versions[0];
        setAssignments([]); // Em produção, buscar atribuições da versão
        useScheduleStore.getState().setCurrentVersion(latest);
      }
    } catch {
      // Silencioso se não houver versões ainda
    } finally {
      setLoading(false);
    }
  };

  const getAssignmentsForView = () => {
    if (viewMode === "class") {
      return assignments.filter((a) => a.class_id === selectedId);
    }
    if (viewMode === "teacher") {
      return assignments.filter((a) => a.teacher_id === selectedId);
    }
    return assignments.filter((a) => a.room_id === selectedId);
  };

  const getCell = (dia: string, hora: number) => {
    return getAssignmentsForView().find(
      (a) => a.slot.dia === dia && a.slot.hora === hora
    );
  };

  const entityOptions = viewMode === "class"
    ? [
        { id: 1, name: "Turma 10º Ano A" },
        { id: 2, name: "Turma 10º Ano B" },
        { id: 3, name: "Turma 11º Ano A" },
      ]
    : viewMode === "teacher"
      ? [
          { id: 1, name: "Prof. Matemática" },
          { id: 2, name: "Prof. Português" },
          { id: 3, name: "Prof. Ciências" },
        ]
      : [
          { id: 1, name: "Sala 101" },
          { id: 2, name: "Sala 102" },
          { id: 3, name: "Laboratório" },
        ];

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Horário</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Visualize o horário por turma, docente ou sala
          </p>
        </div>
        {currentVersion && (
          <Badge variant={currentVersion.hard_violations === 0 ? "success" : "warning"}>
            {currentVersion.hard_violations === 0 ? "Viável" : `${currentVersion.hard_violations} conflitos`}
          </Badge>
        )}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-10">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div>
        </div>
      )}

      {!loading && (
        <div className="flex flex-col">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Visualizar por:</span>
              <Tabs
                value={viewMode}
                onValueChange={(val) => setViewMode(val as "class" | "teacher" | "room")}
              >
                <Tabs.Trigger value="class">Turma</Tabs.Trigger>
                <Tabs.Trigger value="teacher">Docente</Tabs.Trigger>
                <Tabs.Trigger value="room">Sala</Tabs.Trigger>
              </Tabs>
            </div>
            <Select
              label="Selecionar"
              value={selectedId?.toString() || ""}
              onChange={(val: string) => setSelectedId(val ? parseInt(val) : null)}
              options={entityOptions.map((o) => ({ label: o.name, value: o.id.toString() }))}
              placeholder="Escolha uma opção"
              disabled={!selectedId}
            />
          </div>

          {selectedId && (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg">
                <thead className="bg-gray-100 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300 border-b">
                      Hora
                    </th>
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
                        const cell = getCell(dia, hora);
                        return (
                          <td
                            key={`${dia}-${hora}`}
                            className={`px-4 py-2 text-center border-r border-gray-200 dark:border-gray-700 ${
                              cell
                                ? "bg-brand-50 dark:bg-brand-900/20 cursor-pointer hover:bg-brand-100 dark:hover:bg-brand-800/30"
                                : "bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                            } transition-colors`}
                            onClick={() => cell && setSelectedId(cell.teacher_id)}
                          >
                            {cell ? (
                              <div className="flex flex-col items-center gap-1">
                                <span className="text-xs font-medium text-brand dark:text-blue-400">
                                  {cell.subject_name || "Aula"}
                                </span>
                                <span className="text-[10px] text-gray-500 dark:text-gray-400">
                                  {cell.teacher_name || "Prof."}
                                </span>
                                <span className="text-[10px] text-gray-500 dark:text-gray-400">
                                  {cell.room_name || "Sala"}
                                </span>
                              </div>
                            ) : (
                              <div className="text-xs text-gray-300 dark:text-gray-600">—</div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
