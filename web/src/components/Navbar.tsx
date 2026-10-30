import { useAuthStore } from "@/stores/authStore";
import { Button, Brand, Navbar as DSNavbar } from "@ilabuporto/design-system";
import { Link, useNavigate } from "react-router-dom";

export function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <DSNavbar
      brand={<Brand />}
      title="Horário Escolar"
      user={user?.full_name || user?.email || "Utilizador"}
      onLogout={handleLogout}
      onProfileClick={() => navigate("/dashboard")}
    />
  );
}
