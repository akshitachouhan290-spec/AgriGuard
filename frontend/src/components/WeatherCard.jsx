import React from "react";
import { useLocationContext } from "../context/LocationContext";
import { CloudRain, Droplets, Wind, MapPin } from "lucide-react";

export default function WeatherCard({ weather }) {
  const { selectedLocation } = useLocationContext();

  if (!weather) return null;

  const formatLocationLabel = (loc) => {
    if (loc.city === "Custom Location") {
      return `Custom (Lat: ${loc.latitude.toFixed(3)}, Lon: ${loc.longitude.toFixed(3)})`;
    }
    return `${loc.city}${loc.state ? `, ${loc.state}` : ""}`;
  };

  return (
    <div className="weather-card-inner" id="weather-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h4 className="dashboard-card-title" style={{ margin: 0 }}>Field Weather</h4>
          <div style={{ display: "flex", alignItems: "center", gap: "0.25rem", color: "var(--text-muted)", fontSize: "0.85rem", marginTop: "0.25rem" }}>
            <MapPin size={12} /> {formatLocationLabel(selectedLocation)}
          </div>
        </div>
        <span style={{
          backgroundColor: "var(--secondary-light)",
          color: "var(--secondary)",
          padding: "0.25rem 0.5rem",
          borderRadius: "4px",
          fontSize: "0.75rem",
          fontWeight: 700
        }}>
          {weather.condition || "Rain expected"}
        </span>
      </div>

      <div className="weather-main-info">
        <CloudRain size={48} className="weather-icon" style={{ color: "var(--primary)" }} />
        <div>
          <div className="weather-temp">{weather.temp || 31}°C</div>
          <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Feels like {weather.feelsLike || 33}°C
          </div>
        </div>
      </div>

      <div className="weather-stats">
        <div className="weather-stat-item">
          <span className="lbl" style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            <Droplets size={12} /> Humidity
          </span>
          <span className="val">{weather.humidity || 72}%</span>
        </div>
        <div className="weather-stat-item">
          <span className="lbl" style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            <CloudRain size={12} /> Rain
          </span>
          <span className="val">{weather.rainProbability || 60}%</span>
        </div>
        <div className="weather-stat-item" style={{ gridColumn: "span 2", marginTop: "0.5rem" }}>
          <span className="lbl" style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            <Wind size={12} /> Wind speed
          </span>
          <span className="val">{weather.windSpeed || 14} km/h</span>
        </div>
      </div>
    </div>
  );
}
