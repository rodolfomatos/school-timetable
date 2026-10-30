import { useState } from "react";
import { Card, Button, Input } from "@ilabuporto/design-system";
import { authService } from "@/services/api";
import { useAuthStore } from "@/stores/authStore";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await authService.login(email, password);
      const { data } = response;
      // O cookie de acesso é definido automaticamente pelo navegador (httpOnly)
      useAuthStore.getState().login(data);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao fazer login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-brand dark:text-white">Horário Escolar</h1>
          <p className="text-gray-600 dark:text-gray-400">Faça login para continuar</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
            <Input
              type="email"
              placeholder="email@exemplo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Palavra-passe</label>
            <Input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && (
            <div className="text-sm text-destructive dark:text-red-400">{error}</div>
          )}
          <Button
            type="submit"
            variant="primary"
            disabled={loading}
            className="w-full btn-brand"
          >
            {loading ? "A entrar..." : "Entrar"}
          </Button>
        </form>
        <p className="text-center text-sm text-gray-600 dark:text-gray-400 mt-6">
          Não tem uma conta? Contacte o administrador da instituição.
        </p>
      </Card>
    </div>
  );
}
