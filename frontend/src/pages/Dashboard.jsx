import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import FieldCard from "../components/FieldCard";
import WeatherCard from "../components/WeatherCard";
import { getFields, getWeather, getHistory } from "../services/api";
import { useLocationContext } from "../context/LocationContext";
import { ShieldAlert, AlertTriangle, CheckCircle, Loader2 } from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const { selectedLocation } = useLocationContext();
  const [loading, setLoading] = useState(true);
  const [fields, setFields] = useState([]);
  const [weather, setWeather] = useState(null);
  const [recentReport, setRecentReport] = useState(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        // Fetch weather and fields
        const [fieldsData, weatherData, historyData] = await Promise.all([
          getFields(),
          getWeather(selectedLocation.latitude, selectedLocation.longitude),
          getHistory()
        ]);
        setFields(fieldsData);
        setWeather(weatherData);
        if (historyData && historyData.length > 0) {
          setRecentReport(historyData[0]);
        }
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, [selectedLocation]); // Reload dashboard metrics when global location changes!

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

  const formatLocationLabel = (loc) => {
    if (loc.city === "Custom Location") {
      return `Custom (Lat: ${loc.latitude.toFixed(3)}, Lon: ${loc.longitude.toFixed(3)})`;
    }
    return `${loc.city}, ${loc.state}`;
  };

  if (loading) {
    return (
      <AppLayout title="Dashboard">
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "50vh", flexDirection: "column", gap: "1rem" }}>
          <Loader2 size={40} className="animate-spin" style={{ color: "var(--primary)", animation: "spin 1.5s infinite linear" }} />
          <p style={{ color: "var(--text-muted)", fontWeight: 500 }}>Loading farmer dashboard data...</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout title="Dashboard">
      <div className="farmer-header-block">
        <h2>Good morning, Farmer Rajesh 👋</h2>
        <p>
          Current View: <strong style={{ color: "var(--primary)" }}>{formatLocationLabel(selectedLocation)}</strong>
        </p>
      </div>

      <div className="dashboard-summary-grid">
        {/* Fields list */}
        <div>
          <h3 className="dashboard-card-title">My Fields</h3>
          <div className="app-field-grid">
            {fields.map((field) => (
              <FieldCard key={field.id} field={field} />
            ))}
          </div>
        </div>

        {/* Weather Widget & Recent Checks */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <WeatherCard weather={weather} />

          {/* Recent Analysis Summary Card */}
          {recentReport && (
            <div className="weather-card-inner" style={{ borderLeft: `4px solid var(--risk-${recentReport.risk?.toLowerCase()})` }}>
              <h4 className="dashboard-card-title" style={{ marginBottom: "0.75rem" }}>Recent Analysis</h4>
              
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <strong style={{ fontSize: "1.05rem" }}>{recentReport.crop}</strong>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "0.2" }}>
                    Detected: <span style={{ fontWeight: 600 }}>{recentReport.disease}</span>
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                    Confidence: {recentReport.confidence}%
                  </div>
                </div>
                <div className={getRiskBadgeClass(recentReport.risk)}>
                  {getRiskIcon(recentReport.risk)}
                  <span>{recentReport.risk} Risk</span>
                </div>
              </div>

              <button
                onClick={() => navigate("/app/history")}
                className="btn btn-outline btn-block"
                style={{ marginTop: "1rem", padding: "0.5rem" }}
              >
                View History Report
              </button>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
