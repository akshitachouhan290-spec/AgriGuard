import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Button from "../components/Button";
import ChatbotWidget from "../components/ChatbotWidget";
import WeatherCard from "../components/WeatherCard";
import RiskCard from "../components/RiskCard";
import AnalysisCard from "../components/AnalysisCard";
import { mockWeather } from "../data/mockData";
import { cropsList } from "../data/crops";
import { locationsList } from "../data/locations";
import {
  ShieldCheck,
  CloudSun,
  BookOpen,
  Camera,
  Upload,
  Smartphone,
  Globe2,
  Leaf
} from "lucide-react";

export default function LandingPage() {
  const navigate = useNavigate();
  const [selectedCrop, setSelectedCrop] = useState("Tomato");
  const [simLocation, setSimLocation] = useState(locationsList[0]); // default Jaipur
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationComplete, setSimulationComplete] = useState(false);
  const [activeStep, setActiveStep] = useState(null);

  // Mapped simulation report
  const getSimulatedReport = () => {
    const lowerCrop = selectedCrop?.toLowerCase();
    
    if (lowerCrop === "tomato") {
      return {
        crop: "Tomato",
        disease: "Early Blight",
        confidence: 91,
        severity: "Moderate",
        risk: "High",
        why: [
          "Target-pattern leaf lesions identified",
          "High humidity registered near location context (72%)",
          "Rain probability threshold exceeded",
          "Local disease vector report active"
        ],
        advice: [
          "Prune lower infected leaves immediately.",
          "Avoid sprinkler irrigation to prevent spore drift.",
          "Apply locally approved bio-fungicides."
        ],
        date: "Today"
      };
    } else if (lowerCrop === "potato") {
      return {
        crop: "Potato",
        disease: "Late Blight",
        confidence: 88,
        severity: "Severe",
        risk: "High",
        why: [
          "Large water-soaked leaf spots detected",
          "Optimal cold-wet growth temperature parameters"
        ],
        advice: [
          "Harvest mature crop early to avoid tuber rot.",
          "Apply protective copper spray immediately."
        ],
        date: "Today"
      };
    } else if (lowerCrop === "rice") {
      return {
        crop: "Rice",
        disease: "Rice Blast",
        confidence: 90,
        severity: "Moderate",
        risk: "High",
        why: [
          "Diamond-shaped leaf lesions spotted",
          "Prolonged leaf wetness index warning"
        ],
        advice: [
          "Avoid excessive nitrogen fertilizer application.",
          "Use healthy certified disease-free seeds."
        ],
        date: "Today"
      };
    } else {
      // General mock check response for other crops
      return {
        crop: selectedCrop,
        disease: "Mild leaf spotting",
        confidence: 85,
        severity: "Mild",
        risk: "Medium",
        why: [
          "Faint circular chlorotic halos visible",
          "Moderate environmental risk factors"
        ],
        advice: [
          "Monitor daily for spot expansion.",
          "Keep field clear of weed hosts and crop residue."
        ],
        date: "Today"
      };
    }
  };

  const handleSimulateAnalysis = () => {
    setIsSimulating(true);
    setSimulationComplete(false);
    setTimeout(() => {
      setIsSimulating(false);
      setSimulationComplete(true);
      const resultElem = document.getElementById("analysis-results-section");
      if (resultElem) {
        resultElem.scrollIntoView({ behavior: "smooth" });
      }
    }, 1500);
  };

  const handleLocationChange = (e) => {
    const cityName = e.target.value;
    const matchedCity = locationsList.find(c => c.city === cityName);
    if (matchedCity) {
      setSimLocation(matchedCity);
      setSimulationComplete(false);
    }
  };

  const stepsData = [
    { num: "01", title: "Create Profile", desc: "Input your mobile credentials, language preference, and coordinates." },
    { num: "02", title: "Add Field", desc: "Establish field bounds and associate your cultivated crop types." },
    { num: "03", title: "Upload Photo", desc: "Use your device camera to take a clear, close picture of the leaf spots." },
    { num: "04", title: "AI Detection", desc: "Our engine analyzes leaf textures to diagnose pathogens in seconds." },
    { num: "05", title: "Weather + Risk", desc: "Correlates weather conditions to score overall disease spread risk." },
    { num: "06", title: "Actionable Advice", desc: "Obtain specific remedy instructions translated into your local language." }
  ];

  return (
    <div className="app-container">
      <Navbar />

      {/* Hero Section - Using high-composition crop field texture */}
      <header
        className="hero-section"
        style={{
          backgroundImage: "linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.75)), url('https://images.unsplash.com/photo-1605000797499-95a51c5269ae?auto=format&fit=crop&q=80&w=1200')"
        }}
      >
        <div className="container hero-content">
          <h1 className="hero-title">
            Healthy Crops.<br />Better Harvests.
          </h1>
          <p className="hero-subtitle">
            Use AI to detect crop diseases early and get simple, actionable advice. Prevent crop losses before pathogens multiply.
          </p>
          <div className="hero-ctas">
            <Button size="large" variant="secondary" onClick={() => navigate("/app")}>
              CHECK MY CROP →
            </Button>
            <Button size="large" variant="outline-white" onClick={() => {
              document.getElementById("how-it-works").scrollIntoView({ behavior: "smooth" });
            }}>
              HOW IT WORKS
            </Button>
          </div>
          <span className="hero-trustline">
            AI-powered • Weather-aware • Farmer-friendly
          </span>
        </div>
      </header>

      {/* The Problem Section */}
      <section className="section" id="about">
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <span className="section-tag">The Challenge</span>
            <h2 className="section-title">Crop problems can spread before they are noticed.</h2>
            <p className="section-subtitle" style={{ margin: "0 auto" }}>
              Early detection can help farmers respond before disease causes serious crop loss. Protect your fields with AgriGuard scans.
            </p>
          </div>

          <div className="grid-3">
            <div className="problem-card">
              <span className="num">01</span>
              <h3><ShieldCheck size={24} style={{ color: "var(--primary)" }} /> Early Detection</h3>
              <p>Identify possible crop diseases from a simple photo taken in your field. No agricultural science background required.</p>
            </div>
            <div className="problem-card">
              <span className="num">02</span>
              <h3><CloudSun size={24} style={{ color: "var(--primary)" }} /> Weather Awareness</h3>
              <p>Understand how current localized humidity, temperature, and expected rainfall affect immediate disease multiplication.</p>
            </div>
            <div className="problem-card">
              <span className="num">03</span>
              <h3><BookOpen size={24} style={{ color: "var(--primary)" }} /> Actionable Advice</h3>
              <p>Get clear, step-by-step instructions about what to examine on the plant and what remedies are safe and locally recommended.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="section alt-bg" id="how-it-works">
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <span className="section-tag">Process Flow</span>
            <h2 className="section-title">From a photo to a clear crop health report.</h2>
            <p className="section-subtitle" style={{ margin: "0 auto" }}>
              Follow these simple steps. Click on any step to understand how it protects your field crop health.
            </p>
          </div>

          <div className="flow-steps">
            {stepsData.map((step, idx) => (
              <div
                key={idx}
                className="flow-step"
                onClick={() => setActiveStep(activeStep === idx ? null : idx)}
                style={{ borderColor: activeStep === idx ? "var(--primary)" : "" }}
              >
                <div className="step-num">{step.num}</div>
                <h4>{step.title}</h4>
                <p>{activeStep === idx ? step.desc : "Click to read details."}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive AI Crop Check Preview */}
      <section className="section" id="crop-health-preview">
        <div className="container">
          <div className="split-preview">
            <div className="preview-media">
              <img
                src="https://images.unsplash.com/photo-1597362925123-77861d3fbac7?auto=format&fit=crop&q=80&w=800"
                alt="Detailed Crop Leaves Texture"
              />
              <div className="preview-media-overlay">
                <h4 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <Leaf size={18} /> Crop Diagnostic Simulator
                </h4>
                <p style={{ fontSize: "0.85rem", opacity: 0.9 }}>
                  Toggle the crop type and field location selection inputs to test our weather-aware risk scoring index.
                </p>
              </div>
            </div>

            <div className="preview-form-card">
              <h3>Check your crop in seconds</h3>
              
              <div className="form-group">
                <label htmlFor="sim-crop-select">Select Crop</label>
                <select
                  id="sim-crop-select"
                  className="form-control"
                  value={selectedCrop}
                  onChange={(e) => {
                    setSelectedCrop(e.target.value);
                    setSimulationComplete(false);
                  }}
                >
                  {cropsList.map((c) => (
                    <option key={c.id} value={c.name}>
                      {c.icon} {c.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Dynamic Location selector for interactive simulator */}
              <div className="form-group">
                <label htmlFor="sim-location-select">Select Location</label>
                <select
                  id="sim-location-select"
                  className="form-control"
                  value={simLocation.city}
                  onChange={handleLocationChange}
                >
                  {locationsList.map((l) => (
                    <option key={l.city} value={l.city}>
                      {l.city}, {l.state}
                    </option>
                  ))}
                </select>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem", display: "inline-block" }}>
                  Coordinates: Lat {simLocation.latitude.toFixed(4)}, Lon {simLocation.longitude.toFixed(4)}
                </span>
              </div>

              <div className="form-group">
                <label>Photo Upload</label>
                <div className="photo-buttons-grid">
                  <button className="btn btn-outline" style={{ pointerEvents: "none", fontSize: "0.85rem" }}>
                    <Camera size={14} /> Take Photo
                  </button>
                  <button className="btn btn-outline" style={{ pointerEvents: "none", fontSize: "0.85rem" }}>
                    <Upload size={14} /> Upload Image
                  </button>
                </div>
              </div>

              <Button
                variant="secondary"
                block
                onClick={handleSimulateAnalysis}
                disabled={isSimulating}
              >
                {isSimulating ? "Analysing Crop..." : "Analyse My Crop →"}
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* AI Simulation Result Dashboard Section */}
      {(simulationComplete || !isSimulating) && (
        <section className="section alt-bg" id="analysis-results-section" style={{ borderTop: "1px solid var(--border)" }}>
          <div className="container">
            <div style={{ textAlign: "center", marginBottom: "3rem" }}>
              <span className="section-tag">Simulator Output</span>
              <h2 className="section-title">Scan Results & Risk Diagnostics</h2>
              <p className="section-subtitle" style={{ margin: "0 auto" }}>
                This is a live preview of what the farmer receives in their dashboard based on the inputs selected above.
              </p>
            </div>

            <div className="grid-2" style={{ marginBottom: "3rem" }}>
              <AnalysisCard
                report={getSimulatedReport()}
                onSave={() => alert("Mock Data Mode: Please login to save actual reports.")}
                onWhatsApp={() => {}}
                onDone={() => setSimulationComplete(false)}
              />

              <div className="details-flex" style={{ gridTemplateColumns: "1fr" }}>
                <WeatherCard weather={{ ...mockWeather, location: `${simLocation.city}, ${simLocation.state}` }} />
                <RiskCard
                  crop={getSimulatedReport().crop}
                  disease={getSimulatedReport().disease}
                  risk={getSimulatedReport().risk}
                  score={getSimulatedReport().risk === "High" ? 78 : 45}
                  description={
                    getSimulatedReport().risk === "High"
                      ? "High humidity and expected rainfall may increase disease spread."
                      : "Environment parameters are moderately stable."
                  }
                />
              </div>
            </div>
          </div>
        </section>
      )}

      {/* History Preview Section */}
      <section className="section" id="alerts-preview">
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <span className="section-tag">Historical Tracking</span>
            <h2 className="section-title">Track your crop health over time.</h2>
            <p className="section-subtitle" style={{ margin: "0 auto" }}>
              Keep permanent records of every analysis to trace disease spread patterns and review recovery rates.
            </p>
          </div>

          <div className="grid-2">
            <div>
              <h3 className="dashboard-card-title" style={{ marginBottom: "1.5rem" }}>Past Analysis Timeline</h3>
              <div className="timeline">
                <div className="timeline-item high">
                  <div className="timeline-content">
                    <span className="timeline-date">23 Aug</span>
                    <div className="timeline-details">
                      <h4>Tomato - Early Blight</h4>
                      <p>Jaipur • Confidence 91%</p>
                    </div>
                    <span className="risk-tag high" style={{ fontSize: "0.75rem" }}>🔴 High</span>
                  </div>
                </div>

                <div className="timeline-item medium">
                  <div className="timeline-content">
                    <span className="timeline-date">20 Aug</span>
                    <div className="timeline-details">
                      <h4>Tomato - Early Symptoms</h4>
                      <p>Jaipur • Confidence 82%</p>
                    </div>
                    <span className="risk-tag medium" style={{ fontSize: "0.75rem" }}>🟠 Medium</span>
                  </div>
                </div>

                <div className="timeline-item low">
                  <div className="timeline-content">
                    <span className="timeline-date">15 Aug</span>
                    <div className="timeline-details">
                      <h4>Tomato - Healthy</h4>
                      <p>Jaipur • Confidence 95%</p>
                    </div>
                    <span className="risk-tag low" style={{ fontSize: "0.75rem" }}>🟢 Low</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="dashboard-card-title" style={{ marginBottom: "1.5rem" }}>Field Risk Progress Chart</h3>
              <div className="progress-graph">
                <div className="graph-bars">
                  <div className="graph-bar-container">
                    <div className="graph-bar low" style={{ height: "40px" }} data-val="15%" />
                    <span className="graph-label">15 Aug</span>
                  </div>
                  <div className="graph-bar-container">
                    <div className="graph-bar medium" style={{ height: "120px" }} data-val="45%" />
                    <span className="graph-label">20 Aug</span>
                  </div>
                  <div className="graph-bar-container">
                    <div className="graph-bar high" style={{ height: "160px" }} data-val="78%" />
                    <span className="graph-label">23 Aug</span>
                  </div>
                </div>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "1rem", textAlign: "center" }}>
                  Risk Index growth correlates directly with rising local humidity levels.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* WhatsApp Alerts Preview */}
      <section className="section alt-bg">
        <div className="container whatsapp-section">
          <div className="phone-mockup">
            <div className="phone-header">
              <div style={{ width: "32px", height: "32px", borderRadius: "50%", backgroundColor: "var(--primary-light)", display: "flex", alignItems: "center", justifyCenter: "center", color: "var(--primary)", fontWeight: 800 }}>
                🌱
              </div>
              <div>
                <div style={{ fontSize: "0.85rem", fontWeight: "bold" }}>AgriGuard</div>
                <div style={{ fontSize: "0.65rem", opacity: 0.8 }}>Online Alert System</div>
              </div>
            </div>
            <div className="phone-chat-bg">
              <div className="whatsapp-message">
                <h5>🌱 AgriGuard Alert</h5>
                <span className="alert-header">Risk: HIGH 🔴</span>
                <p style={{ marginTop: "0.25rem" }}>
                  Possible Early Blight detected in your Tomato field. High humidity and rain expected. Please check the affected plants.
                </p>
                <a href="#demo" onClick={(e) => { e.preventDefault(); navigate("/app"); }} className="whatsapp-btn">
                  View Report
                </a>
              </div>
            </div>
          </div>

          <div>
            <span className="section-tag">Instant Communication</span>
            <h2 className="section-title">Your crop updates, right on WhatsApp.</h2>
            <p className="section-subtitle">
              Farmers can receive important crop-health alerts without constantly opening the website. WhatsApp warnings are sent when local weather sensors register extreme crop disease threat index spikes.
            </p>
            <Button variant="secondary" onClick={() => navigate("/app")}>
              GET WHATSAPP UPDATES
            </Button>
          </div>
        </div>
      </section>

      {/* Local Language Translations showcase */}
      <section className="section" id="mission">
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <span className="section-tag">Universal Accessibility</span>
            <h2 className="section-title">Technology farmers can actually understand.</h2>
            <p className="section-subtitle" style={{ margin: "0 auto" }}>
              Our application offers text guidelines in local regional languages to make crop diagnostic science accessible to all.
            </p>
          </div>

          <div className="language-showcase">
            <div className="lang-row">
              <span className="lang-name">English</span>
              <span className="lang-text">"Early symptoms of disease detected in your crop."</span>
            </div>
            <div className="lang-row">
              <span className="lang-name">हिन्दी (Hindi)</span>
              <span className="lang-text">"आपकी फसल में रोग के शुरुआती लक्षण पाए गए हैं।"</span>
            </div>
            <div className="lang-row">
              <span className="lang-name">मराठी (Marathi)</span>
              <span className="lang-text">"तुमच्या पिकात रोगाची सुरुवातीची लक्षणे आढळली आहेत."</span>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Banner - Sunset wheat fields landscape */}
      <section
        className="cta-section"
        style={{
          backgroundImage: "linear-gradient(rgba(46, 125, 50, 0.85), rgba(22, 36, 25, 0.9)), url('https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&q=80&w=1200')"
        }}
      >
        <div className="container">
          <h2>Don't wait for the disease to spread.</h2>
          <p>Check your crop today.</p>
          <Button size="large" variant="secondary" onClick={() => navigate("/app")}>
            CHECK MY CROP →
          </Button>
        </div>
      </section>

      <Footer />
      <ChatbotWidget />
    </div>
  );
}
