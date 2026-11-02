import { Card, Button, Table, Input, Badge, Modal, Select, ConfirmDialog } from "@/design-system";
import { useState, useEffect } from "react";

import { useAuthStore } from "@/stores/authStore";
import { require_role, Role } from "@/stores/authStore"; // Assumindo que existe
import {
  schoolService,
  authService,
} from "@/services/api";
import { User, Role as UserRole } from "@/types";

import {
  Room, RoomCreate, RoomRead, RoomUpdate,
  Subject, SubjectCreate, SubjectRead, SubjectUpdate,
  Class, ClassCreate, ClassRead, ClassUpdate,
  UserRead, UserUpdate,
} from "@/schemas/school"; // Assumindo que existem

type EntityType = "users" | "rooms" | "subjects" | "classes";

interface EntityConfig<T> {
  type: EntityType;
  title: string;
  columns: string[];
  apiGet: () => Promise<any>;
  apiCreate: (data: any) => Promise<any>;
  apiUpdate: (id: number, data: any) => Promise<any>;
  apiDelete: (id: number) => Promise<any>;
  createFields: React.ReactNode;
  mapData: (item: any) => any;
  uniqueKey: keyof any;
}

function getEntityConfig(type: EntityType, currentUser: any): EntityConfig<any> {
  const institution_id = currentUser?.institution_id;

  switch (type) {
    case "users":
      return {
        type,
        title: "Utilizadores",
        columns: ["Email", "Nome", "Papel", "Ativo"],
        apiGet: () => authService.listUsers(),
        apiCreate: (data: any) => authService.register({ ...data, institution_id }),
        apiUpdate: (id: number, data: any) => authService.updateUser(id, data),
        apiDelete: (id: number) => authService.deleteUser(id),
        uniqueKey: "id",
        mapData: (item: any) => ({
          id: item.id,
          email: item.email,
          full_name: item.full_name,
          role: item.role,
          is_active: item.is_active,
        }),
        createFields: (
          <UserCreateForm institution_id={institution_id} />
        ),
      };
    case "rooms":
      return {
        type,
        title: "Salas",
        columns: ["Nome", "Capacidade", "Tipo", "Cursos Permitidos"],
        apiGet: () => schoolService.getRooms(),
        apiCreate: (data: any) => schoolService.createRoom({ ...data, institution_id }),
        apiUpdate: (id: number, data: any) => schoolService.updateRoom(id, { ...data, institution_id }),
        apiDelete: (id: number) => schoolService.deleteRoom(id),
        uniqueKey: "id",
        mapData: (item: any) => ({
          id: item.id,
          name: item.name,
          capacity: item.capacity,
          room_type: item.room_type,
          allowed_courses: item.allowed_courses?.join(", ") || "Todos",
        }),
        createFields: (
          <RoomCreateForm institution_id={institution_id} />
        ),
      };
    case "subjects":
      return {
        type,
        title: "Disciplinas",
        columns: ["Código", "Nome", "Carga Semanal", "Tipo Sala", "Curso"],
        apiGet: () => schoolService.getSubjects(),
        apiCreate: (data: any) => schoolService.createSubject({ ...data, institution_id }),
        apiUpdate: (id: number, data: any) => schoolService.updateSubject(id, { ...data, institution_id }),
        apiDelete: (id: number) => schoolService.deleteSubject(id),
        uniqueKey: "id",
        mapData: (item: any) => ({
          id: item.id,
          code: item.code,
          name: item.name,
          weekly_load: item.weekly_load,
          room_type_required: item.room_type_required,
          course_name: item.course?.name || "N/A",
        }),
        createFields: (
          <SubjectCreateForm institution_id={institution_id} />
        ),
      };
    case "classes":
      return {
        type,
        title: "Turmas",
        columns: ["Nome", "Curso", "Ano", "Alunos"],
        apiGet: () => schoolService.getClasses(),
        apiCreate: (data: any) => schoolService.createClass({ ...data, institution_id }),
        apiUpdate: (id: number, data: any) => schoolService.updateClass(id, { ...data, institution_id }),
        apiDelete: (id: number) => schoolService.deleteClass(id),
        uniqueKey: "id",
        mapData: (item: any) => ({
          id: item.id,
          name: item.name,
          course_name: item.course?.name || "N/A",
          year: item.year,
          student_count: item.student_count,
        }),
        createFields: (
          <ClassCreateForm institution_id={institution_id} />
        ),
      };
    default:
      throw new Error(`Tipo desconhecido: ${type}`);
  }
}

function EntityList({
  config,
  currentUser,
}: {
  config: EntityConfig<any>;
  currentUser: any;
}) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [editingItem, setEditingItem] = useState<any | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await config.apiGet();
      const items = response.data || response || [];
      const mapped = items.map(config.mapData);
      setData(mapped);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao carregar dados");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (formData: any) => {
    try {
      await config.apiCreate(formData);
      setShowCreate(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar");
    }
  };

  const handleUpdate = async (id: number, formData: any) => {
    try {
      await config.apiUpdate(id, formData);
      setEditingItem(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao atualizar");
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Tem a certeza que deseja eliminar?")) return;
    try {
      await config.apiDelete(id);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao eliminar");
    }
  };

  const filtered = data.filter((item) =>
    Object.values(item).some((v) =>
      String(v).toLowerCase().includes(search.toLowerCase())
    )
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-10">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500 rounded text-sm text-red-800 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">{config.title}</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Gerencie as {config.title.toLowerCase()} da instituição
          </p>
        </div>
        <Button onClick={() => { setEditingItem(null); setShowCreate(true); }} variant="primary" className="btn-brand">
          Adicionar
        </Button>
      </div>

      <div className="relative">
        <Input
          placeholder="Pesquisar..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full md:w-80"
        />
      </div>

      <Card>
        <Table columns={config.columns} data={filtered} />
      </Card>

      {showCreate && (
        <Modal isOpen={showCreate} title={`Nova ${config.title.slice(0, -1)}`} onClose={() => setShowCreate(false)}>
          <EntityCreateForm config={config} onSubmit={handleCreate} onCancel={() => setShowCreate(false)} />
        </Modal>
      )}

      {editingItem && (
        <Modal isOpen={!!editingItem} title={`Editar ${config.title.slice(0, -1)}`} onClose={() => setEditingItem(null)}>
          <EntityEditForm config={config} item={editingItem} onSubmit={handleUpdate} onCancel={() => setEditingItem(null)} />
        </Modal>
      )}
    </div>
  );
}

function EntityCreateForm({
  config,
  onSubmit,
  onCancel,
}: {
  config: EntityConfig<any>;
  onSubmit: (data: any) => Promise<void>;
  onCancel: () => void;
}) {
  return config.createFields;
}

function EntityEditForm({
  config,
  item,
  onSubmit: any,
  onCancel,
}: {
  config: EntityConfig<any>;
  item: any;
  onSubmit: (id: number, data: any) => Promise<void>;
  onCancel: () => void;
}) {
  // Para simplicidade, reutiliza o create form mas pré-preenchido
  // Em produção, criar formulários específicos
  return config.createFields;
}

// Formulários específicos por entidade
function UserCreateForm({ institution_id }: { institution_id?: string }) {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
    role: "student",
    institution_id: institution_id || "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // O onSubmit será passado via props
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
        <Input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          placeholder="email@exemplo.com"
          required
        />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nome Completo</label>
        <Input
          value={formData.full_name}
          onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
          placeholder="Nome completo"
        />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
        <Input
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          placeholder="Mínimo 6 caracteres"
          minLength={6}
          required
        />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Papel</label>
        <Select
          label="Papel"
          value={formData.role}
          onChange={(val: string) => setFormData({ ...formData, role: val })}
          options={[
            { label: "Estudante", value: "student" },
            { label: "Docente", value: "teacher" },
            { label: "Coordenador", value: "coordinator" },
            { label: "Administrador", value: "admin" },
          ]}
          placeholder="Escolha um papel"
        />
      </div>
    </form>
  );
}

function RoomCreateForm({ institution_id }: { institution_id?: string }) {
  const [formData, setFormData] = useState({
    name: "",
    capacity: 30,
    room_type: "normal",
    allowed_courses: "",
    course_id: "",
    institution_id: institution_id || "",
    is_active: true,
    setup_before: 0,
    cleanup_after: 0,
  });

  return (
    <form className="space-y-4">
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nome</label>
        <Input value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="Ex: Sala 101" required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Capacidade</label>
        <Input type="number" value={formData.capacity} onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) })} min={1} required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Tipo de Sala</label>
        <Select label="Tipo" value={formData.room_type} onChange={(val: string) => setFormData({ ...formData, room_type: val })} options={[
          { label: "Normal", value: "normal" },
          { label: "Laboratório", value: "laboratorio" },
          { label: "Anatomia", value: "anatomia" },
        ]} />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Cursos Permitidos (separados por vírgula)</label>
        <Input value={formData.allowed_courses} onChange={(e) => setFormData({ ...formData, allowed_courses: e.target.value })} placeholder="Ex: CS, MATH, BIO" />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Curso (opcional)</label>
        <Input value={formData.course_id} onChange={(e) => setFormData({ ...formData, course_id: e.target.value })} placeholder="ID do curso" />
      </div>
    </form>
  );
}

function SubjectCreateForm({ institution_id }: { institution_id?: string }) {
  const [formData, setFormData] = useState({
    code: "",
    name: "",
    weekly_load: 4,
    room_type_required: "normal",
    periodicity: "semanal",
    course_id: "",
    institution_id: institution_id || "",
    is_active: true,
  });

  return (
    <form className="space-y-4">
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Código</label>
        <Input value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })} placeholder="Ex: MAT101" maxLength={50} required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nome</label>
        <Input value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="Ex: Matemática" required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Carga Semanal</label>
        <Input type="number" value={formData.weekly_load} onChange={(e) => setFormData({ ...formData, weekly_load: parseInt(e.target.value) })} min={1} required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Tipo de Sala Requerida</label>
        <Select label="Tipo" value={formData.room_type_required} onChange={(val: string) => setFormData({ ...formData, room_type_required: val })} options={[
          { label: "Normal", value: "normal" },
          { label: "Laboratório", value: "laboratorio" },
          { label: "Anatomia", value: "anatomia" },
        ]} />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Periodicidade</label>
        <Select label="Periodicidade" value={formData.periodicity} onChange={(val: string) => setFormData({ ...formData, periodicity: val })} options={[
          { label: "Semanal", value: "semanal" },
          { label: "Quinzenal", value: "quinzenal" },
          { label: "Módulo/Semestre", value: "modulo_semestre" },
        ]} />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Curso (ID)</label>
        <Input type="number" value={formData.course_id} onChange={(e) => setFormData({ ...formData, course_id: parseInt(e.target.value) })} placeholder="ID do curso" required />
      </div>
    </form>
  );
}

function ClassCreateForm({ institution_id }: { institution_id?: string }) {
  const [formData, setFormData] = useState({
    name: "",
    course_id: "",
    year: 1,
    student_count: 25,
    institution_id: institution_id || "",
    is_active: true,
  });

  return (
    <form className="space-y-4">
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nome</label>
        <Input value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="Ex: 10º Ano A" required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Curso (ID)</label>
        <Input type="number" value={formData.course_id} onChange={(e) => setFormData({ ...formData, course_id: parseInt(e.target.value) })} min={1} required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Ano</label>
        <Input type="number" value={formData.year} onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })} min={1} required />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Número de Alunos</label>
        <Input type="number" value={formData.student_count} onChange={(e) => setFormData({ ...formData, student_count: parseInt(e.target.value) })} min={1} required />
      </div>
    </form>
  );
}

// Exportar o componente principal
export function ManageEntities() {
  const { user: currentUser } = useAuthStore();

  const tabs: EntityType[] = ["users", "rooms", "subjects", "classes"];
  const [activeTab, setActiveTab] = useState<EntityType>("rooms");

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Gestão de Entidades</h1>
        <p className="text-gray-600 dark:text-gray-400">Gerencie as entidades da instituição</p>
      </div>

      <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-4 overflow-x-auto" aria-label="Tipos de entidade">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === tab
                  ? "text-brand border-b-2 border-brand"
                  : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      <EntityList config={getEntityConfig(activeTab, currentUser)} currentUser={currentUser} />
    </div>
  );
}

export default ManageEntities;