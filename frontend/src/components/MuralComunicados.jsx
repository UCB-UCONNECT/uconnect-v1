// src/components/MuralComunicados.jsx
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "./navBar";
import MenuLateral from "./MenuLateral";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { getAnnouncements } from "../services/api";

function normalizePost(raw) {
  // data/hora
  const when = raw.date ? new Date(raw.date) : raw.createdAt ? new Date(raw.createdAt) : null;
  const time =
    when &&
    when.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  const date =
    when &&
    when.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });

  // autor pode vir como string OU objeto; garantimos string
  let author = "UCB Community";
  if (typeof raw.authorName === "string" && raw.authorName.trim()) {
    author = raw.authorName.trim();
  } else if (raw.author || raw.user || raw.created_by) {
    const a = raw.author || raw.user || raw.created_by;
    if (typeof a === "string") author = a;
    else if (a && typeof a === "object") {
      author =
        (typeof a.name === "string" && a.name.trim()) ||
        (typeof a.email === "string" && a.email.trim()) ||
        (a.registration != null && String(a.registration)) ||
        author;
    }
  }

  // mensagem sempre string
  const message =
    (typeof raw.content === "string" && raw.content) ||
    (typeof raw.message === "string" && raw.message) ||
    "";

  // caminho/área à esquerda (apenas decorativo)
  const pathLeft =
    (typeof raw.area === "string" && raw.area) ||
    (typeof raw.unit === "string" && raw.unit) /*||
    "Teste";*/

  // id seguro para React
  const safeId =
    raw.id != null
      ? String(raw.id)
      : (typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : Math.random().toString(36).slice(2));

  return { id: safeId, author, pathLeft, message, time: time || "", date: date || "" };
}

export default function MuralComunicados() {
  const navigate = useNavigate();

  const [tab, setTab] = useState("comunicados");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setErr(null);
      const data = await getAnnouncements();
      const list = Array.isArray(data) ? data : data?.results || [];
      const normalized = list.map(normalizePost);
      setItems(normalized.filter((p) => (p.message || "").trim().length > 0));
    } catch (e) {
      console.error(e);
      setErr("Erro ao carregar comunicados");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <>
      <Navbar />
      <div className="d-flex">
        <MenuLateral />

        <div className="container-fluid mt-4">
          <div className="card shadow-sm">
            <div className="card-header bg-white">
              <ul className="nav nav-tabs card-header-tabs">
                <li className="nav-item">
                  <button
                    className={`nav-link ${tab === "comunicados" ? "active" : ""}`}
                    onClick={() => setTab("comunicados")}
                  >
                    Comunicados
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${tab === "avisos" ? "active" : ""}`}
                    onClick={() => setTab("avisos")}
                    title="Ainda não diferenciado no backend"
                  >
                    Avisos
                  </button>
                </li>
              </ul>
            </div>

            <div className="card-body">
              <div className="d-flex justify-content-end mb-3">
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => navigate("/comunicados/novo")}
                >
                  Novo comunicado
                </button>
              </div>

              {err && (
                <div className="alert alert-danger d-flex align-items-center" role="alert">
                  <i className="bi bi-exclamation-triangle-fill me-2"></i>
                  {err}
                </div>
              )}

              {!err && loading && (
                <div className="text-center p-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Carregando…</span>
                  </div>
                </div>
              )}

              {!err && !loading && items.length === 0 && (
                <div className="text-center text-muted p-4">
                  Nenhum comunicado encontrado.
                </div>
              )}

              <div className="d-flex flex-column gap-3">
                {items.map((it) => (
                  <div key={it.id} className="card" style={{ borderRadius: 10 }}>
                    <div className="card-body">
                      <div className="d-flex align-items-center mb-2">
                        <div className="text-primary fw-semibold me-2">{it.author}</div>
                        <span className="text-muted">›</span>
                        <div className="ms-2 text-secondary">{it.pathLeft}</div>
                      </div>

                      <div className="text-body" style={{ whiteSpace: "pre-wrap" }}>
                        {it.message}
                      </div>

                      <div className="text-end text-muted small mt-2">
                        {it.time && it.date ? `${it.time} — ${it.date}` : ""}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="my-3 small text-muted">
            Este é o seu mural. Aqui você vê os comunicados recentes.
          </div>
        </div>
      </div>
    </>
  );
}