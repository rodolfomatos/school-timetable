import { Sidebar as DSSidebar } from "@ilabuporto/design-system";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";

const menuItems = [
  { path: "/dashboard", label: "Dashboard", icon: "📊" },
  { path: "/teacher/calendar", label: "Minhas Restrições", icon: "📅" },
  { path: "/schedule", label: "Meu Horário", icon: "📋" },
  { path: "/disputes", label: "Contestações", icon: "⚖️" },
  { path: "/admin/users", label: "Utilizadores", icon: "👥" },
  { path: "/admin/rooms", label: "Salas", icon: "🏫" },
  { path: "/admin/subjects", label: "Disciplinas", icon: "📚" },
  { path: "/admin/classes", label: "Turmas", icon: "🏫" },
];

export function Sidebar() {
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();

  const isAdminOrCoordinator =
    user && (user.role === "admin" || user.role === "coordinator");

  const visibleItems = menuItems.filter(
    (item) =>
      !item.path.includes("/admin/") || isAdminOrCoordinator
  );

  return (
    <DSSidebar
      items={visibleItems.map((item) => ({
        label: item.label,
        icon: item.icon,
        onClick: () => navigate(item.path),
      }))}
      activePath={location.pathname}
      onLogout={() => {
        logout();
        navigate("/login");
      }}
    />
  );
}
