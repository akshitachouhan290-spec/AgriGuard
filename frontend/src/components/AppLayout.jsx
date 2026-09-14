import React, { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { Sprout, LayoutDashboard, Layers, Camera, History, Bell, User, LogOut, Home, Navigation, Loader2 } from "lucide-react";
import { useLocationContext } from "../context/LocationContext";
import { locationsList } from "../data/locations";

export default function AppLayout({ children, title }) {
  const navigate = useNavigate();
  const { selectedLocation, setLocation, updateLocationByCoordinates } = useLocationContext();
  const [geoLoading, setGeoLoading] = useState(false);
  const [geoError, setGeoError] = useState("");

  const menuItems = [
    { label: "Dashboard", to: "/app", icon: <LayoutDashboard size={20} /> },
    { label: "My Fields", to: "/app/fields", icon: <Layers size={20} /> },
    { label: "Check Crop", to: "/app/check", icon: <Camera size={20} />, special: true },
    { label: "History", to: "/app/history", icon: <History size={20} /> },
    { label: "Alerts", to: "/app/alerts", icon: <Bell size={20} /> },
    { label: "Profile", to: "/app/profile", icon: <User size={20} /> }
  ];

  const handleCitySelect = (e) => {
    setGeoError("");
    const cityName = e.target.value;
    const cityObj = locationsList.find((c) => c.city === cityName);
    if (cityObj) {
      setLocation(cityObj);
    }
  };

  const handleUseGeolocation = () => {
    setGeoError("");
    if (!navigator.geolocation) {
      setGeoError("Geolocation is not supported by your browser.");
      return;
    }

    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        updateLocationByCoordinates(latitude, longitude);
        setGeoLoading(false);
      },
      (error) => {
        console.error("Geolocation error", error);
        setGeoError("Unable to access your location. Please select your location manually.");
        setGeoLoading(false);
      },
      { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
  };

  const formatLocationLabel = (loc) => {
    if (loc.city === "Custom Location") {
      return `📍 Custom (Lat: ${loc.latitude.toFixed(4)}, Lon: ${loc.longitude.toFixed(4)})`;
    }
    return `📍 ${loc.city}, ${loc.state}`;
  };

  return (
    <div className="app-layout">
      {/* Sidebar for Desktop */}
      <aside className="app-sidebar">
        <div className="app-sidebar-header">
          <Link to="/" className="logo-container">
            <Sprout className="logo-icon" size={24} />
            <span style={{ fontWeight: 800 }}>AgriGuard</span>
          </Link>
        </div>

        <ul className="app-sidebar-menu">
          {menuItems.map((item) => {
            if (item.special) {
              return (
                <li key={item.label} className="app-sidebar-item special-action">
                  <NavLink to={item.to} end>
                    {item.icon}
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              );
            }
            return (
              <li key={item.label} className="app-sidebar-item">
                <NavLink to={item.to} className={({ isActive }) => (isActive ? "active" : "")} end>
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>

        <div style={{ padding: "1.5rem", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9rem", color: "rgba(255,255,255,0.6)" }}>
            <Home size={16} />
            <span>Landing Page</span>
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="app-main-content">
        {/* Desktop Header */}
        <header className="app-header" style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", height: "auto", minHeight: "var(--header-height)", padding: "1rem 2rem", gap: "1rem" }}>
          <h2 className="app-header-title">{title || "Farmer App"}</h2>
          
          {/* Global Location Picker in Desktop Header */}
          <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-muted)" }}>Current Location:</span>
                <span style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--primary)" }}>
                  {formatLocationLabel(selectedLocation)}
                </span>
              </div>
              
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <select
                  value={selectedLocation.city === "Custom Location" ? "Custom Location" : selectedLocation.city}
                  onChange={handleCitySelect}
                  className="form-control"
                  style={{ padding: "0.25rem 0.5rem", fontSize: "0.78rem", width: "160px", height: "30px" }}
                  aria-label="Select manual city location"
                >
                  {selectedLocation.city === "Custom Location" && (
                    <option value="Custom Location">Custom Location</option>
                  )}
                  {locationsList.map((c) => (
                    <option key={c.city} value={c.city}>
                      {c.city}, {c.state}
                    </option>
                  ))}
                </select>
                
                <button
                  type="button"
                  onClick={handleUseGeolocation}
                  disabled={geoLoading}
                  className="btn btn-outline"
                  style={{ height: "30px", padding: "0 0.5rem", fontSize: "0.75rem", display: "flex", gap: "0.25rem" }}
                  title="Use My Current Location"
                >
                  {geoLoading ? (
                    <Loader2 size={12} className="animate-spin" style={{ animation: "spin 1.5s infinite linear" }} />
                  ) : (
                    <Navigation size={12} />
                  )}
                  <span>GPS</span>
                </button>
              </div>
              
              {geoError && (
                <span style={{ fontSize: "0.75rem", color: "var(--risk-high)", maxWidth: "250px", display: "inline-block" }}>
                  {geoError}
                </span>
              )}
            </div>

            <div style={{ borderLeft: "1px solid var(--border)", paddingLeft: "1rem", display: "flex", alignItems: "center", gap: "1rem" }}>
              <span style={{ fontSize: "0.9rem", fontWeight: 600 }}>Farmer Rajesh 👋</span>
              <button onClick={() => navigate("/")} className="btn btn-outline" style={{ padding: "0.4rem 0.8rem", fontSize: "0.8rem" }}>
                <LogOut size={12} /> Logout
              </button>
            </div>
          </div>
        </header>

        {/* Mobile Top Navbar */}
        <header className="app-mobile-nav">
          <Link to="/" className="logo-container" style={{ fontSize: "1.1rem" }}>
            <Sprout className="logo-icon" size={20} />
            <span>AgriGuard</span>
          </Link>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <select
              value={selectedLocation.city === "Custom Location" ? "Custom Location" : selectedLocation.city}
              onChange={handleCitySelect}
              className="form-control"
              style={{ padding: "0.15rem 0.35rem", fontSize: "0.7rem", width: "110px", height: "26px", color: "#fff", background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)" }}
              aria-label="Mobile select location"
            >
              {selectedLocation.city === "Custom Location" && (
                <option value="Custom Location">Custom Location</option>
              )}
              {locationsList.map((c) => (
                <option key={c.city} value={c.city} style={{ color: "#333" }}>
                  {c.city}
                </option>
              ))}
            </select>
            
            <button
              onClick={handleUseGeolocation}
              disabled={geoLoading}
              className="btn btn-secondary"
              style={{ width: "26px", height: "26px", padding: 0, borderRadius: "4px" }}
              title="Use GPS Geolocation"
            >
              <Navigation size={12} />
            </button>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="app-body-container">
          {geoError && (
            <div style={{
              backgroundColor: "var(--risk-high-light)",
              color: "var(--risk-high)",
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              fontSize: "0.85rem",
              fontWeight: 600,
              marginBottom: "1rem"
            }}>
              ⚠️ {geoError}
            </div>
          )}
          {children}
        </main>

        {/* Mobile Bottom Navigation Bar */}
        <nav className="app-bottom-nav">
          <NavLink to="/app" className={({ isActive }) => `bottom-nav-item ${isActive ? "active" : ""}`} end>
            <LayoutDashboard size={20} />
            <span>Home</span>
          </NavLink>
          <NavLink to="/app/fields" className={({ isActive }) => `bottom-nav-item ${isActive ? "active" : ""}`}>
            <Layers size={20} />
            <span>Fields</span>
          </NavLink>
          <NavLink to="/app/check" className={({ isActive }) => `bottom-nav-item special-action ${isActive ? "active" : ""}`}>
            <Camera size={22} />
            <span>Check</span>
          </NavLink>
          <NavLink to="/app/history" className={({ isActive }) => `bottom-nav-item ${isActive ? "active" : ""}`}>
            <History size={20} />
            <span>History</span>
          </NavLink>
          <NavLink to="/app/profile" className={({ isActive }) => `bottom-nav-item ${isActive ? "active" : ""}`}>
            <User size={20} />
            <span>Profile</span>
          </NavLink>
        </nav>
      </div>
    </div>
  );
}
