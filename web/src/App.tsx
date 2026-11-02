import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { authService } from "@/services/api";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import TeacherCalendar from "@/pages/TeacherCalendar";
import ScheduleTable from "@/pages/ScheduleTable";
import Disputes from "@/pages/Disputes";
import ManageEntities from "@/pages/ManageEntities";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function RequireRole({ roles, children }: { roles: string[]; children: React.ReactNode }) {
  const { user } = useAuthStore();
  if (!user || !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  // Rehidrata a sessão a partir do cookie httpOnly (/users/me) após um reload.
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    let cancelled = false;
    authService
      .getMe()
      .then(({ data }) => {
        if (!cancelled) useAuthStore.getState().login(data);
      })
      .catch(() => {
        // Sem sessão válida: continua como anónimo (rota protegida redireciona).
      })
      .finally(() => {
        if (!cancelled) setBooting(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (booting) return null;

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="/teacher/calendar"
          element={
            <RequireAuth>
              <TeacherCalendar />
            </RequireAuth>
          }
        />
        <Route
          path="/schedule"
          element={
            <RequireAuth>
              <ScheduleTable />
            </RequireAuth>
          }
        />
        <Route
          path="/disputes"
          element={
            <RequireAuth>
              <Disputes />
            </RequireAuth>
          }
        />
        <Route
          path="/admin/entities"
          element={
            <RequireAuth>
              <RequireRole roles={["admin", "coordinator"]}>
                <ManageEntities />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}