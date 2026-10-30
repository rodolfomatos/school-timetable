import { Card, Button, Table, Input, Badge } from "@ilabuporto/design-system";
import { useState } from "react";

type EntityType = "users" | "rooms" | "subjects" | "classes";

interface ManageEntityProps {
  type: EntityType;
  title: string;
  columns: string[];
  data: any[];
  createFields: React.ReactNode;
}

export function ManageUsers() {
  const [data, setData] = useState([
    { id: 1, email: "admin@escola.pt", nome: "Admin", role: "admin", ativo: true },
    { id: 2, email: "prof1@escola.pt", nome: "Prof. Matemática", role: "teacher", ativo: true },
    { id: 3, email: "estudante1@escola.pt", nome: "João Silva", role: "student", ativo: true },
  ]);
  return <GenericEntity type="users" title="Utilizadores" columns={["Email", "Nome", "Papel", "Ativo"]} data={data} />;
}

export function ManageRooms() {
  const [data, setData] = useState([
    { id: 1, name: "Sala 101", capacity: 30, tipo: "normal", cursos: "Todos" },
    { id: 2, name: "Lab. Ciências", capacity: 20, tipo: "laboratorio", cursos: "Ciências" },
    { id: 3, name: "Sala Anatómia", capacity: 40, tipo: "anatomia", cursos: "Medicina" },
  ]);
  return <GenericEntity type="rooms" title="Salas" columns={["Nome", "Capacidade", "Tipo", "Cursos"]} data={data} />;
}

export function ManageSubjects() {
  const [data, setData] = useState([
    { id: 1, code: "MAT101", name: "Matemática", load: 5, tipo: "normal" },
    { id: 2, code: "POR101", name: "Português", load: 5, tipo: "normal" },
    { id: 3, code: "CIE101", name: "Ciências", load: 4, tipo: "laboratorio" },
  ]);
  return <GenericEntity type="subjects" title="Disciplinas" columns={["Código", "Nome", "Carga", "Tipo Sala"]} data={data} />;
}

export function ManageClasses() {
  const [data, setData] = useState([
    { id: 1, name: "10º Ano A", course: "Cientifico-Humanistico", year: 10, students: 25 },
    { id: 2, name: "10º Ano B", course: "Cientifico-Humanistico", year: 10, students: 26 },
    { id: 3, name: "11º Ano A", course: "Cientifico-Humanistico", year: 11, students: 24 },
  ]);
  return <GenericEntity type="classes" title="Turmas" columns={["Nome", "Curso", "Ano", "Alunos"]} data={data} />;
}

function GenericEntity({ type, title, columns, data }: ManageEntityProps) {
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const filtered = data.filter((item) =>
    Object.values(item).some((v) =>
      String(v).toLowerCase().includes(search.toLowerCase())
    )
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Gerencie as {title.toLowerCase()} da instituição
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)} variant="primary" className="btn-brand">
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
        <Table columns={columns} data={filtered} />
      </Card>

      {showCreate && (
        <Card className="mt-4">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Nova Entrada</h3>
          {createFields}
          <Button onClick={() => setShowCreate(false)} variant="ghost">
            Cancelar
          </Button>
        </Card>
      )}
    </div>
  );
}
