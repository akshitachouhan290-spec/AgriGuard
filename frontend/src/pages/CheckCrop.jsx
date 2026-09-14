import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import LoadingAnalysis from "../components/LoadingAnalysis";
import AnalysisCard from "../components/AnalysisCard";
import { getFields, analyzeCrop, createField } from "../services/api";
import { cropsList } from "../data/crops";
import { useLocationContext } from "../context/LocationContext";
import { Camera, Upload, Plus, Search, MapPin } from "lucide-react";

export default function CheckCrop() {
  const location = useLocation();
  const navigate = useNavigate();
  const { selectedLocation } = useLocationContext();

  const [step, setStep] = useState(1);
  const [fields, setFields] = useState([]);
  
  // Selections
  const [selectedFieldId, setSelectedFieldId] = useState("");
  const [selectedCrop, setSelectedCrop] = useState("Tomato");
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  
  // Searchable Crop state
  const [cropSearchQuery, setCropSearchQuery] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // Analysis status
  const [report, setReport] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isAddingField, setIsAddingField] = useState(false);

  // New field form state
  const [newFieldName, setNewFieldName] = useState("");
  const [newFieldCrop, setNewFieldCrop] = useState("Tomato");
  const [newFieldArea, setNewFieldArea] = useState("2 acres");

  const formatLocationLabel = (loc) => {
    if (loc.city === "Custom Location") {
      return `Custom (Lat: ${loc.latitude.toFixed(4)}, Lon: ${loc.longitude.toFixed(4)})`;
    }
    return `${loc.city}, ${loc.state || ""}`;
  };

  // Load fields
  useEffect(() => {
    async function loadFields() {
      const data = await getFields();
      setFields(data);
      
      // Pre-select field if navigation state is provided
      if (location.state?.selectFieldId) {
        setSelectedFieldId(location.state.selectFieldId);
        if (location.state.selectCrop) {
          setSelectedCrop(location.state.selectCrop);
          setCropSearchQuery(location.state.selectCrop);
        }
        setStep(3);
      } else if (data && data.length > 0) {
        setSelectedFieldId(data[0].id);
        setSelectedCrop(data[0].crop);
        setCropSearchQuery(data[0].crop);
      }
    }
    loadFields();
  }, [location]);

  // Handle Field select change
  const handleFieldChange = (fieldId) => {
    setSelectedFieldId(fieldId);
    const selected = fields.find(f => f.id === fieldId);
    if (selected) {
      setSelectedCrop(selected.crop);
      setCropSearchQuery(selected.crop);
    }
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
      setStep(4);
    }
  };

  const handleSimulatedCapture = () => {
    setPhoto("simulated-leaf-photo.jpg");
    let leafUrl = "https://images.unsplash.com/photo-1592417817098-8f3d6eb19675?auto=format&fit=crop&q=80&w=600";
    if (selectedCrop === "Potato") {
      leafUrl = "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&q=80&w=600";
    } else if (selectedCrop === "Wheat") {
      leafUrl = "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&q=80&w=600";
    }
    setPhotoPreview(leafUrl);
    setStep(4);
  };

  const handleAnalysisComplete = async () => {
    try {
      const result = await analyzeCrop(photo, selectedCrop, selectedFieldId);
      setReport(result);
      setStep(5);
    } catch (err) {
      console.error("Analysis failed", err);
    }
  };

  const handleSaveReport = async () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      alert("Crop Health Report Saved to Field History!");
      navigate("/app");
    }, 800);
  };

  const handleDone = () => {
    navigate("/app");
  };

  const handleAddNewField = async (e) => {
    e.preventDefault();
    if (!newFieldName.trim()) return;
    
    try {
      // Rule: New fields initially inherit the global location!
      const addedField = await createField({
        name: newFieldName,
        crop: newFieldCrop,
        area: newFieldArea ? `${newFieldArea} acres` : "N/A",
        location: formatLocationLabel(selectedLocation)
      });
      const updatedFields = await getFields();
      setFields(updatedFields);
      setSelectedFieldId(addedField.id);
      setSelectedCrop(addedField.crop);
      setCropSearchQuery(addedField.crop);
      setIsAddingField(false);
      setNewFieldName("");
    } catch (err) {
      console.error("Failed to add field", err);
    }
  };

  // Search filter matching 24+ crops
  const filteredCrops = cropsList.filter((c) =>
    c.name.toLowerCase().includes(cropSearchQuery.toLowerCase())
  );

  return (
    <AppLayout title="Check Crop Health">
      <div className="wizard-box">
        {/* Step Progress Headers */}
        <div className="wizard-steps-header">
          <div className={`wizard-step-indicator ${step === 1 ? "active" : ""} ${step > 1 ? "completed" : ""}`}>
            1. Select Field
          </div>
          <div className={`wizard-step-indicator ${step === 2 ? "active" : ""} ${step > 2 ? "completed" : ""}`}>
            2. Select Crop
          </div>
          <div className={`wizard-step-indicator ${step === 3 ? "active" : ""} ${step > 3 ? "completed" : ""}`}>
            3. Upload Photo
          </div>
          <div className={`wizard-step-indicator ${step === 4 ? "active" : ""} ${step > 4 ? "completed" : ""}`}>
            4. Analyzing
          </div>
          <div className={`wizard-step-indicator ${step === 5 ? "active" : ""}`}>
            5. Report
          </div>
        </div>

        {/* Wizard Main Area */}
        <div className="wizard-body">
          {/* STEP 1: SELECT FIELD */}
          {step === 1 && (
            <div>
              <h3 className="dashboard-card-title">Choose Field to Diagnostics</h3>
              
              {!isAddingField ? (
                <div>
                  <div className="wizard-selection-list">
                    {fields.map((f) => (
                      <div
                        key={f.id}
                        className={`wizard-selection-card ${selectedFieldId === f.id ? "selected" : ""}`}
                        onClick={() => handleFieldChange(f.id)}
                      >
                        <input
                          type="radio"
                          id={`field-radio-${f.id}`}
                          name="field-select"
                          checked={selectedFieldId === f.id}
                          readOnly
                        />
                        <div className="wizard-selection-text">
                          <h4>{f.name}</h4>
                          <p>{f.crop} • {f.area} • {f.location}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => setIsAddingField(true)}
                    className="btn btn-outline"
                    style={{ marginTop: "1rem" }}
                  >
                    <Plus size={16} /> Add New Field
                  </button>
                </div>
              ) : (
                <form onSubmit={handleAddNewField} style={{ marginTop: "1rem" }}>
                  <div className="form-group">
                    <label htmlFor="w-field-name">Field Name</label>
                    <input
                      id="w-field-name"
                      type="text"
                      className="form-control"
                      placeholder="e.g. North Side Plot"
                      value={newFieldName}
                      onChange={(e) => setNewFieldName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="w-field-crop">Crop Cultivated</label>
                    <select
                      id="w-field-crop"
                      className="form-control"
                      value={newFieldCrop}
                      onChange={(e) => setNewFieldCrop(e.target.value)}
                    >
                      {cropsList.map(c => (
                        <option key={c.id} value={c.name}>{c.icon} {c.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="w-field-area">Field Area (Acres)</label>
                    <input
                      id="w-field-area"
                      type="number"
                      step="0.1"
                      className="form-control"
                      placeholder="e.g. 2.5"
                      value={newFieldArea.replace(" acres", "")}
                      onChange={(e) => setNewFieldArea(e.target.value)}
                    />
                  </div>
                  
                  {/* Visual confirmation that it uses the global context location */}
                  <div className="form-group" style={{ display: "flex", alignItems: "center", gap: "0.25rem", color: "var(--text-muted)", fontSize: "0.85rem", margin: "1rem 0" }}>
                    <MapPin size={12} />
                    <span>Location: <strong>{formatLocationLabel(selectedLocation)}</strong> (Inherited from Current Location)</span>
                  </div>

                  <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
                    <button type="submit" className="btn btn-primary">
                      Save & Select Field
                    </button>
                    <button
                      type="button"
                      onClick={() => setIsAddingField(false)}
                      className="btn btn-outline"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* STEP 2: SEARCHABLE CROP SELECTOR */}
          {step === 2 && (
            <div>
              <h3 className="dashboard-card-title">Confirm Cultivated Crop</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
                Search and select the crop from the catalog below.
              </p>
              
              <div style={{ position: "relative", marginBottom: "1.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", position: "relative" }}>
                  <Search size={18} style={{ position: "absolute", left: "12px", color: "var(--text-muted)" }} />
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search crop (e.g. Tomato, Rice, Apple...)"
                    style={{ paddingLeft: "36px" }}
                    value={cropSearchQuery}
                    onChange={(e) => {
                      setCropSearchQuery(e.target.value);
                      setDropdownOpen(true);
                    }}
                    onFocus={() => setDropdownOpen(true)}
                  />
                </div>

                {dropdownOpen && (
                  <div style={{
                    position: "absolute",
                    top: "100%",
                    left: 0,
                    right: 0,
                    backgroundColor: "#fff",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    maxHeight: "220px",
                    overflowY: "auto",
                    boxShadow: "0 10px 20px rgba(0,0,0,0.08)",
                    zIndex: 10,
                    marginTop: "4px"
                  }}>
                    {filteredCrops.length === 0 ? (
                      <div style={{ padding: "1rem", color: "var(--text-muted)", fontSize: "0.9rem", textAlign: "center" }}>
                        No crops match "{cropSearchQuery}"
                      </div>
                    ) : (
                      filteredCrops.map((c) => (
                        <div
                          key={c.id}
                          onClick={() => {
                            setSelectedCrop(c.name);
                            setCropSearchQuery(c.name);
                            setDropdownOpen(false);
                          }}
                          style={{
                            padding: "0.75rem 1rem",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: "0.75rem",
                            backgroundColor: selectedCrop === c.name ? "var(--primary-light)" : "transparent",
                            transition: "background-color 0.2s"
                          }}
                          className="crop-search-option"
                        >
                          <span style={{ fontSize: "1.2rem" }}>{c.icon}</span>
                          <span style={{ fontWeight: selectedCrop === c.name ? 700 : 500 }}>{c.name}</span>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>

              {/* Quick Suggestions grid */}
              <div style={{ marginTop: "1rem" }}>
                <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>Common suggestions:</span>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
                  {["Tomato", "Rice", "Wheat", "Potato", "Chilli"].map((cname) => {
                    const matchedC = cropsList.find(x => x.name === cname);
                    return (
                      <button
                        key={cname}
                        onClick={() => {
                          setSelectedCrop(cname);
                          setCropSearchQuery(cname);
                          setDropdownOpen(false);
                        }}
                        className={`btn ${selectedCrop === cname ? "btn-primary" : "btn-outline"}`}
                        style={{ padding: "0.4rem 0.8rem", fontSize: "0.8rem" }}
                      >
                        {matchedC?.icon} {cname}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: UPLOAD PHOTO */}
          {step === 3 && (
            <div>
              <h3 className="dashboard-card-title">Take or Upload Leaf Photo</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
                Capture leaves showing spots or symptoms.
              </p>
              
              <div className="form-group" style={{ display: "flex", gap: "1rem", flexWrap: "wrap", padding: "0.75rem", backgroundColor: "var(--bg-light)", borderRadius: "8px", border: "1px solid var(--border)", fontSize: "0.85rem", marginBottom: "1rem" }}>
                <div>Crop: <strong>{selectedCrop}</strong></div>
                <div style={{ borderLeft: "1px solid var(--border)", paddingLeft: "1rem" }}>
                  Location: <strong>{formatLocationLabel(selectedLocation)}</strong>
                </div>
              </div>

              <div className="upload-zone" onClick={handleSimulatedCapture}>
                <Camera className="upload-icon" size={40} />
                <strong>📷 SIMULATE FIELD LEAF SCAN</strong>
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  Click to simulate scanning a diseased {selectedCrop} leaf.
                </p>
              </div>

              <div style={{ margin: "2rem 0", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ borderBottom: "1px solid var(--border)", width: "100px", display: "inline-block" }} />
                <span style={{ padding: "0 1rem", fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: "bold" }}>OR</span>
                <span style={{ borderBottom: "1px solid var(--border)", width: "100px", display: "inline-block" }} />
              </div>

              <div>
                <label
                  htmlFor="file-upload-input"
                  className="btn btn-outline btn-block"
                  style={{ cursor: "pointer", justifyContent: "center" }}
                >
                  <Upload size={18} />
                  UPLOAD LEAF IMAGE FILE
                </label>
                <input
                  id="file-upload-input"
                  type="file"
                  accept="image/*"
                  onChange={handlePhotoUpload}
                  style={{ display: "none" }}
                />
              </div>
            </div>
          )}

          {/* STEP 4: ANALYSING */}
          {step === 4 && (
            <LoadingAnalysis onComplete={handleAnalysisComplete} />
          )}

          {/* STEP 5: FINAL REPORT */}
          {step === 5 && (
            <div>
              {photoPreview && (
                <div style={{ width: "100%", maxWidth: "300px", margin: "0 auto 2rem auto", borderRadius: "8px", overflow: "hidden", border: "1px solid var(--border)" }}>
                  <img src={photoPreview} alt="Scanned Leaf Preview" style={{ width: "100%", display: "block" }} />
                </div>
              )}
              <AnalysisCard
                report={report}
                onSave={handleSaveReport}
                onWhatsApp={() => {}}
                onDone={handleDone}
                isSaving={isSaving}
              />
            </div>
          )}
        </div>

        {/* Wizard Navigation Footer */}
        {step < 4 && (
          <div className="wizard-footer">
            <button
              onClick={() => {
                setStep(prev => Math.max(1, prev - 1));
                setDropdownOpen(false);
              }}
              disabled={step === 1}
              className="btn btn-outline"
            >
              Previous
            </button>
            
            {step < 3 ? (
              <button
                onClick={() => {
                  setStep(prev => prev + 1);
                  setDropdownOpen(false);
                }}
                className="btn btn-primary"
              >
                Next
              </button>
            ) : (
              <div />
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
