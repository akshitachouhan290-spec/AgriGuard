import React from "react";
import { Link } from "react-router-dom";
import { Sprout } from "lucide-react";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-grid">
        <div className="footer-col">
          <div className="logo-container" style={{ marginBottom: "1rem" }}>
            <Sprout className="logo-icon" size={24} />
            <span style={{ color: "#fff" }}>AgriGuard</span>
          </div>
          <p style={{ fontSize: "0.9rem", lineHeight: "1.5" }}>
            Know your crop. Act before it's too late. Supporting farmers worldwide with weather-aware early crop disease detection.
          </p>
        </div>

        <div className="footer-col">
          <h4>Product</h4>
          <ul>
            <li><Link to="/app">Check My Crop</Link></li>
            <li><Link to="/app">Field Dashboard</Link></li>
            <li><Link to="/app/history">Analysis History</Link></li>
            <li><Link to="/app/alerts">Weather Alerts</Link></li>
          </ul>
        </div>

        <div className="footer-col">
          <h4>Resources</h4>
          <ul>
            <li><a href="#how-it-works">How It Works</a></li>
            <li><a href="#about">About AI Crop Check</a></li>
            <li><a href="#alerts-preview">Disease Risk Index</a></li>
            <li><a href="#mission">Our Mission</a></li>
          </ul>
        </div>

        <div className="footer-col">
          <h4>Contact & Support</h4>
          <ul>
            <li>Email: contact@crop-health-system.in</li>
            <li>Helpline: 1800-XXX-XXXX</li>
            <li>Village Extension Support</li>
            <li>Jaipur, Rajasthan</li>
          </ul>
        </div>
      </div>

      <div className="container footer-bottom">
        <p>&copy; {new Date().getFullYear()} AgriGuard. Built for Agriculture Technology Hackathon. All rights reserved.</p>
      </div>
    </footer>
  );
}
