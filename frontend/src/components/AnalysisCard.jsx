import React, { useState } from "react";
import { Check, ShieldAlert, AlertTriangle, CheckCircle, Smartphone, Save, ArrowLeft } from "lucide-react";

export default function AnalysisCard({ report, onSave, onWhatsApp, onDone, isSaving, hasBack = false, onBack }) {
  const [whatsAppSent, setWhatsAppSent] = useState(false);

  if (!report) return null;

  const getRiskBadge = (riskVal) => {
    switch (riskVal?.toLowerCase()) {
      case "high":
        return (
          <span className="risk-tag high">
            <ShieldAlert size={16} /> 🔴 HIGH
          </span>
        );
      case "medium":
        return (
          <span className="risk-tag medium">
            <AlertTriangle size={16} /> 🟠 MEDIUM
          </span>
        );
      case "low":
      default:
        return (
          <span className="risk-tag low">
            <CheckCircle size={16} /> 🟢 LOW
          </span>
        );
    }
  };

  const handleWhatsAppClick = () => {
    setWhatsAppSent(true);
    if (onWhatsApp) onWhatsApp(report);
    setTimeout(() => {
      setWhatsAppSent(false);
    }, 4000);
  };

  return (
    <div className="report-card" id="analysis-report-card">
      <div className="report-header">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {hasBack && (
            <button onClick={onBack} className="btn" style={{ padding: "0.25rem", color: "var(--text-muted)", border: "none", background: "none" }}>
              <ArrowLeft size={20} />
            </button>
          )}
          <h3 style={{ margin: 0, fontSize: "1.25rem" }}>YOUR CROP HEALTH REPORT</h3>
        </div>
        <div>
          {report.date && <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 600 }}>{report.date}</span>}
        </div>
      </div>

      <div className="report-body">
        {/* Main Details Grid */}
        <div className="report-grid">
          <div className="report-meta-item">
            <div className="label">Crop</div>
            <div className="val">{report.crop}</div>
          </div>
          <div className="report-meta-item">
            <div className="label">Possible Disease</div>
            <div className="val" style={{ color: report.risk === "High" ? "var(--risk-high)" : report.risk === "Medium" ? "var(--risk-medium)" : "var(--risk-low)" }}>
              {report.disease}
            </div>
          </div>
          <div className="report-meta-item">
            <div className="label">AI Confidence</div>
            <div className="val">{report.confidence}%</div>
          </div>
          <div className="report-meta-item">
            <div className="label">Severity</div>
            <div className="val">{report.severity}</div>
          </div>
          <div className="report-meta-item" style={{ gridColumn: "span 2", border: "none" }}>
            <div className="label" style={{ marginBottom: "0.25rem" }}>Overall Risk</div>
            <div>{getRiskBadge(report.risk)}</div>
          </div>
        </div>

        {/* Why section */}
        {report.why && report.why.length > 0 && (
          <div style={{ marginBottom: "2rem" }}>
            <h4 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.75rem", borderBottom: "1px solid var(--border)", paddingBottom: "0.5rem" }}>
              Why is the risk {report.risk?.toLowerCase()}?
            </h4>
            <ul className="reasons-list">
              {report.why.map((reason, index) => (
                <li key={index}>
                  <Check size={16} />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actionable Advice */}
        {report.advice && report.advice.length > 0 && (
          <div className="advice-box">
            <h4 className="advice-title">What should you do?</h4>
            <ul className="advice-list">
              {report.advice.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* WhatsApp Sent Alert Banner */}
        {whatsAppSent && (
          <div style={{
            marginTop: "1.5rem",
            backgroundColor: "#d4edda",
            color: "#155724",
            padding: "0.75rem 1rem",
            borderRadius: "6px",
            fontSize: "0.88rem",
            fontWeight: 600,
            textAlign: "center"
          }}>
            🌱 Report successfully sent to your WhatsApp number!
          </div>
        )}

        {/* CTAs */}
        <div style={{
          marginTop: "2.5rem",
          display: "flex",
          flexWrap: "wrap",
          gap: "1rem",
          justifyContent: "space-between",
          borderTop: "1px solid var(--border)",
          paddingTop: "1.5rem"
        }}>
          <div style={{ display: "flex", gap: "1rem", flexGrow: 1 }}>
            {onSave && (
              <button
                onClick={onSave}
                className="btn btn-primary"
                disabled={isSaving}
                style={{ flexGrow: 1, minWidth: "140px" }}
              >
                <Save size={18} />
                {isSaving ? "Saving..." : "SAVE REPORT"}
              </button>
            )}

            <button
              onClick={handleWhatsAppClick}
              className="btn btn-outline"
              style={{ flexGrow: 1, minWidth: "180px", color: "#25d366", borderColor: "#25d366", backgroundColor: "transparent" }}
            >
              <Smartphone size={18} />
              SEND TO WHATSAPP
            </button>
          </div>

          {onDone && (
            <button
              onClick={onDone}
              className="btn btn-secondary"
              style={{ minWidth: "100px" }}
            >
              DONE
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
