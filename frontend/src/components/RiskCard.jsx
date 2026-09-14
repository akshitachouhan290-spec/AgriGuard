import React from "react";
import { useLocationContext } from "../context/LocationContext";
import { ShieldAlert, AlertTriangle, CheckCircle, MapPin } from "lucide-react";

export default function RiskCard({ crop, disease, risk, score, description }) {
  const { selectedLocation } = useLocationContext();

  const getRiskColor = (riskVal) => {
    switch (riskVal?.toLowerCase()) {
      case "high":
        return {
          bg: "var(--risk-high-light)",
          text: "var(--risk-high)",
          label: "🔴 HIGH RISK",
          icon: <ShieldAlert size={20} />
        };
      case "medium":
        return {
          bg: "var(--risk-medium-light)",
          text: "var(--risk-medium)",
          label: "🟠 MEDIUM RISK",
          icon: <AlertTriangle size={20} />
        };
      case "low":
      default:
        return {
          bg: "var(--risk-low-light)",
          text: "var(--risk-low)",
          label: "🟢 LOW RISK",
          icon: <CheckCircle size={20} />
        };
    }
  };

  const riskInfo = getRiskColor(risk);

  const formatLocationLabel = (loc) => {
    if (loc.city === "Custom Location") {
      return `Custom (Lat: ${loc.latitude.toFixed(3)}, Lon: ${loc.longitude.toFixed(3)})`;
    }
    return `${loc.city}${loc.state ? `, ${loc.state}` : ""}`;
  };

  return (
    <div className="weather-card-inner" id="risk-card" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
      <div>
        <h4 className="dashboard-card-title">Crop Disease Risk</h4>
        
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: "1rem 0" }}>
          <div>
            <strong style={{ fontSize: "1.1rem", display: "block" }}>{crop || "Tomato"}</strong>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", display: "block" }}>Suspected Disease: {disease || "Early Blight"}</span>
            <span style={{ fontSize: "0.8rem", color: "var(--primary)", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.25rem", marginTop: "0.25rem" }}>
              <MapPin size={10} /> {formatLocationLabel(selectedLocation)}
            </span>
          </div>
          <div className="risk-tag" style={{ backgroundColor: riskInfo.bg, color: riskInfo.text }}>
            {riskInfo.icon}
            <span>{riskInfo.label}</span>
          </div>
        </div>
      </div>

      <div style={{ margin: "1.5rem 0" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", fontWeight: 700, marginBottom: "0.35rem" }}>
          <span>Risk Score</span>
          <span style={{ color: riskInfo.text }}>{score || 78}/100</span>
        </div>
        <div style={{ height: "8px", backgroundColor: "var(--border)", borderRadius: "4px", overflow: "hidden" }}>
          <div style={{
            height: "100%",
            width: `${score || 78}%`,
            backgroundColor: riskInfo.text,
            borderRadius: "4px",
            transition: "width 1s ease-in-out"
          }} />
        </div>
      </div>

      <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", margin: 0, borderTop: "1px solid var(--border)", paddingTop: "1rem" }}>
        {description || "High humidity and expected rainfall may increase disease spread."}
      </p>
    </div>
  );
}
