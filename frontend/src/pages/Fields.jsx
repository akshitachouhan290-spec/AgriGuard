import React, { useState, useEffect } from "react";
import AppLayout from "../components/AppLayout";
import FieldCard from "../components/FieldCard";
import { getFields, createField } from "../services/api";
import { cropsList } from "../data/crops";
import { useLocationContext } from "../context/LocationContext";
import { Plus, X, Loader2, MapPin } from "lucide-react";

export default function Fields() {
  const { selectedLocation } = useLocationContext();
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form states
  const [fieldName, setFieldName] = useState("");
  const [crop, setCrop] = useState("Tomato");
  const [area, setArea] = useState("");
  const [customLocation, setCustomLocation] = useState("");

  const formatLocationLabel = (loc) => {
    if (loc.city === "Custom Location") {
      return `Custom (Lat: ${loc.latitude.toFixed(4)}, Lon: ${loc.longitude.toFixed(4)})`;
    }
    return `${loc.city}, ${loc.state || ""}`;
  };

  const loadFields = async () => {
    try {
      setLoading(true);
      const data = await getFields();
      setFields(data);
    } catch (err) {
      console.error("Failed to load fields", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFields();
  }, []);

  // Sync initial location input with global location when modal opens
  useEffect(() => {
    if (showModal) {
      setCustomLocation(formatLocationLabel(selectedLocation));
    }
  }, [showModal, selectedLocation]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fieldName.trim()) return;

    try {
      setLoading(true);
      await createField({
        name: fieldName,
        crop,
        area: area ? `${area} acres` : "N/A",
        location: customLocation
      });
      // Clear form
      setFieldName("");
      setArea("");
      setShowModal(false);
      await loadFields();
    } catch (err) {
      console.error("Failed to create field", err);
      setLoading(false);
    }
  };

  return (
    <AppLayout title="Field Management">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <div>
          <h2 style={{ fontSize: "1.5rem" }}>My Registered Fields</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Manage and inspect risk profiles for each area section.</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          <Plus size={16} /> Add Field
        </button>
      </div>

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "40vh", flexDirection: "column", gap: "1rem" }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--primary)", animation: "spin 1.5s infinite linear" }} />
          <p style={{ color: "var(--text-muted)" }}>Loading fields...</p>
        </div>
      ) : (
        <div className="app-field-grid">
          {fields.map((field) => (
            <FieldCard key={field.id} field={field} />
          ))}
        </div>
      )}

      {/* Add Field Modal Form */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 style={{ fontSize: "1.25rem", margin: 0 }}>Register New Field</h3>
              <button onClick={() => setShowModal(false)} className="btn" style={{ padding: "0.25rem", border: "none", background: "none", color: "var(--text-muted)" }}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="field-name-input">Field Name</label>
                <input
                  id="field-name-input"
                  type="text"
                  className="form-control"
                  placeholder="e.g. West Side Tomato"
                  value={fieldName}
                  onChange={(e) => setFieldName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-crop-select">Cultivated Crop</label>
                <select
                  id="field-crop-select"
                  className="form-control"
                  value={crop}
                  onChange={(e) => setCrop(e.target.value)}
                >
                  {cropsList.map(c => (
                    <option key={c.id} value={c.name}>{c.icon} {c.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="field-area-input">Area Size (Acres)</label>
                <input
                  id="field-area-input"
                  type="number"
                  step="0.1"
                  className="form-control"
                  placeholder="e.g. 2.5"
                  value={area}
                  onChange={(e) => setArea(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-location-input">Location / Coordinates</label>
                <input
                  id="field-location-input"
                  type="text"
                  className="form-control"
                  value={customLocation}
                  onChange={(e) => setCustomLocation(e.target.value)}
                  placeholder="Village, District or Coordinates"
                />
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem", display: "inline-block" }}>
                  📍 Defaults to your current active global location.
                </span>
              </div>

              <div className="modal-footer">
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-outline">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Field
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
