import React, { useState, useEffect } from "react";
import AppLayout from "../components/AppLayout";
import AnalysisCard from "../components/AnalysisCard";
import { getHistory } from "../services/api";
import { ShieldAlert, AlertTriangle, CheckCircle, Loader2 } from "lucide-react";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        const data = await getHistory();
        setHistory(data);
      } catch (err) {
        console.error("Failed to load history", err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  const getRiskBadgeClass = (risk) => {
    switch (risk?.toLowerCase()) {
      case "high": return "risk-tag high";
      case "medium": return "risk-tag medium";
      case "low":
      default: return "risk-tag low";
    }
  };

  const getRiskIcon = (risk) => {
    switch (risk?.toLowerCase()) {
      case "high": return <ShieldAlert size={16} />;
      case "medium": return <AlertTriangle size={16} />;
      case "low":
      default: return <CheckCircle size={16} />;
    }
  };

  if (loading) {
    return (
      <AppLayout title="Crop History">
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "40vh", flexDirection: "column", gap: "1rem" }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--primary)", animation: "spin 1.5s infinite linear" }} />
          <p style={{ color: "var(--text-muted)" }}>Loading history records...</p>
        </div>
      </AppLayout>
    );
  }

  // If a specific report is selected, show its full page detail
  if (selectedReport) {
    return (
      <AppLayout title="Analysis Detail">
        <div style={{ marginBottom: "1.5rem" }}>
          <button onClick={() => setSelectedReport(null)} className="btn btn-outline">
            ← Back to History List
          </button>
        </div>
        <AnalysisCard
          report={selectedReport}
          onDone={() => setSelectedReport(null)}
          hasBack={true}
          onBack={() => setSelectedReport(null)}
        />
      </AppLayout>
    );
  }

  return (
    <AppLayout title="Crop Diagnostics History">
      <div style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.5rem" }}>Previous Crop Checks</h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Browse historical disease scans and recommended treatments.</p>
      </div>

      {history.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: "3rem",
          backgroundColor: "#fff",
          borderRadius: "8px",
          border: "1px solid var(--border)",
          color: "var(--text-muted)"
        }}>
          <p>No diagnostics history records found. Perform a crop health check first.</p>
        </div>
      ) : (
        <div className="timeline">
          {history.map((item) => (
            <div
              key={item.id}
              className={`timeline-item ${item.risk?.toLowerCase()}`}
              onClick={() => setSelectedReport(item)}
            >
              <div className="timeline-content">
                <span className="timeline-date">{item.date}</span>
                
                <div className="timeline-details">
                  <h4 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    {item.crop === "Tomato" ? "🍅" : item.crop === "Wheat" ? "🌾" : item.crop === "Potato" ? "🥔" : "🌱"}{" "}
                    {item.crop} - <span style={{ color: "var(--charcoal)" }}>{item.disease}</span>
                  </h4>
                  <p style={{ marginTop: "0.25rem" }}>
                    Confidence: {item.confidence}% • Severity: {item.severity}
                  </p>
                </div>

                <div className={getRiskBadgeClass(item.risk)} style={{ fontSize: "0.8rem" }}>
                  {getRiskIcon(item.risk)}
                  <span>{item.risk}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </AppLayout>
  );
}
