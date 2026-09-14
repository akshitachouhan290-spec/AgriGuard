import React from "react";
import { useNavigate } from "react-router-dom";
import { MapPin, Calendar, Layers, ShieldAlert, CheckCircle, AlertTriangle } from "lucide-react";

export default function FieldCard({ field }) {
  const navigate = useNavigate();

  const getRiskBadge = (risk) => {
    switch (risk?.toLowerCase()) {
      case "high":
        return (
          <span className="risk-tag high">
            <ShieldAlert size={16} /> 🔴 HIGH RISK
          </span>
        );
      case "medium":
        return (
          <span className="risk-tag medium">
            <AlertTriangle size={16} /> 🟠 MEDIUM RISK
          </span>
        );
      case "low":
      default:
        return (
          <span className="risk-tag low">
            <CheckCircle size={16} /> 🟢 LOW RISK
          </span>
        );
    }
  };

  const getCropEmoji = (crop) => {
    switch (crop?.toLowerCase()) {
      case "tomato": return "🍅";
      case "wheat": return "🌾";
      case "potato": return "🥔";
      case "rice": return "🌾";
      case "maize":
      case "corn": return "🌽";
      case "cotton": return "☁️";
      case "onion": return "🧅";
      case "sugarcane": return "🎋";
      case "banana": return "🍌";
      case "tea": return "🍃";
      case "apple": return "🍎";
      case "grapes": return "🍇";
      case "chilli": return "🌶️";
      case "cucumber": return "🥒";
      case "brinjal":
      case "eggplant": return "🍆";
      case "okra": return "🥬";
      case "cabbage": return "🥬";
      case "cauliflower": return "🥦";
      default: return "🌱";
    }
  };

  return (
    <div className="app-field-card" id={`field-card-${field.id}`}>
      <div className="app-field-card-header" style={{ alignItems: "center" }}>
        <div>
          <h3 className="app-field-title">
            {getCropEmoji(field.crop)} {field.name}
          </h3>
          <div className="app-field-subtitle" style={{ display: "flex", alignItems: "center", gap: "0.25rem", marginTop: "0.25rem" }}>
            <MapPin size={12} /> {field.location || "Unknown Location"}
          </div>
        </div>
        {getRiskBadge(field.currentRisk)}
      </div>

      <div style={{ marginTop: "1rem", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
        <div style={{ fontSize: "0.85rem" }}>
          <span style={{ color: "var(--text-muted)", display: "block" }}>Area Size</span>
          <strong style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
            <Layers size={12} /> {field.area || "N/A"}
          </strong>
        </div>
        <div style={{ fontSize: "0.85rem" }}>
          <span style={{ color: "var(--text-muted)", display: "block" }}>Last Checked</span>
          <strong style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
            <Calendar size={12} /> {field.lastAnalysis || "Never"}
          </strong>
        </div>
      </div>

      {field.diseaseDetected && field.diseaseDetected !== "Healthy" && (
        <div style={{
          marginTop: "1rem",
          padding: "0.75rem",
          backgroundColor: "var(--bg-light)",
          borderRadius: "6px",
          border: "1px solid var(--border)",
          fontSize: "0.85rem"
        }}>
          <span style={{ color: "var(--text-muted)" }}>Last Detected:</span>{" "}
          <strong style={{ color: "var(--risk-high)" }}>{field.diseaseDetected}</strong>
          {field.severity && <span> ({field.severity} severity)</span>}
        </div>
      )}

      <div className="app-field-actions">
        <button
          onClick={() => navigate("/app/check", { state: { selectFieldId: field.id, selectCrop: field.crop } })}
          className="btn btn-primary btn-block"
        >
          Check Crop
        </button>
      </div>
    </div>
  );
}
