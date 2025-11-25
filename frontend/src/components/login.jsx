import React, { useState } from "react";
import { login } from "../services/api";
import "../styles/login.css";

function Login({ onLoginSuccess }) {
  const [registration, setRegistration] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await login(registration, password);
      
      console.log("Login bem-sucedido:", data);
      onLoginSuccess();
    } catch (err) {
      setError(err.message || "Erro ao fazer login. Verifique suas credenciais.");
      console.error("Erro no login:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>🎓 UCONNECT</h2>
          <p>Sistema de Calendário Acadêmico</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <div className="mb-3">
            <label htmlFor="registration" className="form-label">
              Matrícula
            </label>
            <input
              type="text"
              className="form-control"
              id="registration"
              value={registration}
              onChange={(e) => setRegistration(e.target.value)}
              placeholder="Digite sua matrícula"
              required
              autoFocus
            />
          </div>

          <div className="mb-3">
            <label htmlFor="password" className="form-label">
              Senha
            </label>
            <input
              type="password"
              className="form-control"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite sua senha"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Entrando...
              </>
            ) : (
              "Entrar"
            )}
          </button>
        </form>

        <div className="login-footer">
          <small className="text-muted">
            Esqueceu a senha? Entre em contato com a coordenação.
          </small>
        </div>
      </div>
    </div>
  );
}

export default Login;
