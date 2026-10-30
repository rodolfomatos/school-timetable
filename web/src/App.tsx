import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import TeacherCalendar from "@/pages/TeacherCalendar";
import ScheduleTable from "@/pages/ScheduleTable";
import Disputes from "@/pages/Disputes";
import ManageUsers from "@/pages/ManageUsers";
import ManageRooms from "@/pages/ManageRooms";
import ManageSubjects from "@/pages/ManageSubjects";
import ManageClasses from "@/pages/ManageClasses";

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
          path="/admin/users"
          element={
            <RequireAuth>
              <RequireRole roles={["admin", "coordinator"]}>
                <ManageUsers />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/rooms"
          element={
            <RequireAuth>
              <RequireRole roles={["admin", "coordinator"]}>
                <ManageRooms />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/subjects"
          element={
            <RequireAuth>
              <RequireRole roles={["admin", "coordinator"]}>
                <ManageSubjects />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/classes"
          element={
            <RequireAuth>
              <RequireRole roles={["admin", "coordinator"]}>
                <ManageClasses />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
