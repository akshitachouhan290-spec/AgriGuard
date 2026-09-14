import React, { useState, useEffect } from "react";
import AppLayout from "../components/AppLayout";
import { getFarmer, saveFarmer } from "../services/api";
import { useLocationContext } from "../context/LocationContext";
import { locationsList } from "../data/locations";
import { User, Smartphone, Globe, MapPin, Save, Loader2, Navigation } from "lucide-react";

export default function Profile() {
  const { selectedLocation, setLocation, updateLocationByCoordinates } = useLocationContext();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const [geoLoading, setGeoLoading] = useState(false);
  const [geoError, setGeoError] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        setLoading(true);
        const data = await getFarmer();
        setProfile(data);
      } catch (err) {
        console.error("Failed to load profile", err);
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: value
    }));
  };

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
        setGeoError("Unable to access your location. Please select manually.");
        setGeoLoading(false);
      },
      { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      setSaveSuccess(false);
      
      // Save farmer profile state (excluding coordinates/city context)
      await saveFarmer({
        ...profile,
        village: profile.village || ""
      });
      
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to save profile", err);
    } finally {
      setSaving(false);
    }
  };

  const formatLocationLabel = (loc) => {
    if (loc.city === "Custom Location") {
      return `Custom (Lat: ${loc.latitude.toFixed(4)}, Lon: ${loc.longitude.toFixed(4)})`;
    }
    return `${loc.city}, ${loc.state || ""}`;
  };

  if (loading) {
    return (
      <AppLayout title="Farmer Profile">
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "40vh", flexDirection: "column", gap: "1rem" }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--primary)", animation: "spin 1.5s infinite linear" }} />
          <p style={{ color: "var(--text-muted)" }}>Loading profile...</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout title="Farmer Profile">
      <div style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.5rem" }}>My Credentials & Settings</h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Update your contact information, preferred language, and regional coordinates.</p>
      </div>

      <div className="preview-form-card" style={{ maxWidth: "700px", margin: "0 auto", padding: "2rem" }}>
        <form onSubmit={handleSubmit}>
          {saveSuccess && (
            <div style={{
              backgroundColor: "#d4edda",
              color: "#155724",
              padding: "0.75rem 1rem",
              borderRadius: "6px",
              fontSize: "0.9rem",
              fontWeight: 600,
              marginBottom: "1.5rem",
              textAlign: "center"
            }}>
              ✓ Profile settings updated successfully!
            </div>
          )}

          <div className="profile-grid">
            <div className="form-group">
              <label htmlFor="p-name" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <User size={14} /> Full Name
              </label>
              <input
                id="p-name"
                type="text"
                name="name"
                className="form-control"
                value={profile.name || ""}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="p-phone" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Smartphone size={14} /> Mobile Number
              </label>
              <input
                id="p-phone"
                type="tel"
                name="phone"
                className="form-control"
                value={profile.phone || ""}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="p-lang" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Globe size={14} /> Preferred Language
              </label>
              <select
                id="p-lang"
                name="language"
                className="form-control"
                value={profile.language || "Hindi"}
                onChange={handleChange}
              >
                <option value="English">English</option>
                <option value="Hindi">हिन्दी (Hindi)</option>
                <option value="Marathi">मराठी (Marathi)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="p-village" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <MapPin size={14} /> Village / Town
              </label>
              <input
                id="p-village"
                type="text"
                name="village"
                className="form-control"
                value={profile.village || ""}
                onChange={handleChange}
              />
            </div>

            {/* Profile Global Location Context picker */}
            <div className="form-group" style={{ gridColumn: "span 2", marginTop: "1rem", padding: "1.25rem", border: "1px solid var(--border)", borderRadius: "8px", backgroundColor: "var(--bg-light)" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 700, fontSize: "0.95rem" }}>
                <MapPin size={16} style={{ color: "var(--primary)" }} /> Global Current Location
              </label>
              
              <div style={{ margin: "0.5rem 0 1rem 0" }}>
                Active Coordinates City: <strong style={{ color: "var(--primary)" }}>{formatLocationLabel(selectedLocation)}</strong>
              </div>

              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
                <div style={{ flexGrow: 1, minWidth: "200px" }}>
                  <select
                    id="profile-city-select"
                    value={selectedLocation.city === "Custom Location" ? "Custom Location" : selectedLocation.city}
                    onChange={handleCitySelect}
                    className="form-control"
                    aria-label="Profile select location"
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
                </div>

                <button
                  type="button"
                  onClick={handleUseGeolocation}
                  disabled={geoLoading}
                  className="btn btn-outline"
                  style={{ display: "flex", gap: "0.5rem", height: "42px" }}
                >
                  {geoLoading ? (
                    <Loader2 size={16} className="animate-spin" style={{ animation: "spin 1.5s infinite linear" }} />
                  ) : (
                    <Navigation size={16} />
                  )}
                  <span>Use GPS Geolocation</span>
                </button>
              </div>

              {geoError && (
                <div style={{ fontSize: "0.8rem", color: "var(--risk-high)", marginTop: "0.5rem" }}>
                  {geoError}
                </div>
              )}
            </div>
          </div>

          <div style={{ marginTop: "2rem", display: "flex", justifyContent: "flex-end" }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={saving}
              style={{ minWidth: "160px" }}
            >
              {saving ? (
                <>
                  <Loader2 size={16} className="animate-spin" style={{ animation: "spin 1.5s infinite linear" }} />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={16} />
                  Save Settings
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
}
