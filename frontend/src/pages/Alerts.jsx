import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import { getAlerts } from "../services/api";
import { ShieldAlert, AlertTriangle, CloudRain, Loader2, ArrowRight } from "lucide-react";

export default function Alerts() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAlerts() {
      try {
        setLoading(true);
        const data = await getAlerts();
        setAlerts(data || []);
      } catch (err) {
        console.error("Failed to fetch alerts", err);
      } finally {
        setLoading(false);
      }
    }
    loadAlerts();
  }, []);

  const getAlertIcon = (type) => {
    switch (type) {
      case "disease":
        return <ShieldAlert size={24} style={{ color: "var(--risk-high)" }} />;
      case "weather":
      default:
        return <CloudRain size={24} style={{ color: "var(--primary)" }} />;
    }
  };

  const getAlertClass = (type) => {
    return type === "disease" ? "alert-item-card danger" : "alert-item-card warning";
  };

  return (
    <AppLayout title="Risk Alerts">
      <div style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.5rem" }}>Crop Health & Weather Warnings</h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Early warning indicators based on scanned diagnostics and localized weather forecasts.</p>
      </div>

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "40vh", flexDirection: "column", gap: "1rem" }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--primary)", animation: "spin 1.5s infinite linear" }} />
          <p style={{ color: "var(--text-muted)" }}>Loading alerts...</p>
        </div>
      ) : alerts.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: "3rem",
          backgroundColor: "#fff",
          borderRadius: "8px",
          border: "1px solid var(--border)",
          color: "var(--text-muted)"
        }}>
          <p>No active warning alerts recorded for your fields.</p>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert) => (
            <div key={alert.id} className={getAlertClass(alert.type)}>
              <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start", flexGrow: 1 }}>
                <div style={{ marginTop: "0.25rem" }}>
                  {getAlertIcon(alert.type)}
                </div>
                <div className="alert-content-inner">
                  <h4 className="alert-title-text" style={{ color: alert.type === "disease" ? "var(--risk-high)" : "var(--charcoal)" }}>
                    {alert.title}
                  </h4>
                  <p className="alert-message-text">{alert.message}</p>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginTop: "0.5rem", fontWeight: 600 }}>
                    Recorded on {alert.date}
                  </span>
                </div>
              </div>

              {alert.type === "disease" && (
                <button
                  onClick={() => navigate("/app/history")}
                  className="btn btn-outline"
                  style={{ padding: "0.5rem 1rem", fontSize: "0.85rem", whiteSpace: "nowrap" }}
                >
                  View Report <ArrowRight size={14} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </AppLayout>
  );
}
