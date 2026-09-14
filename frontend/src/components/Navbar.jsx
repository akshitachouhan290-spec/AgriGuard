import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Sprout, Menu, X, Search } from "lucide-react";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleCheckCrop = () => {
    setMobileMenuOpen(false);
    navigate("/app");
  };

  const navLinks = [
    { label: "About", to: "#about" },
    { label: "How It Works", to: "#how-it-works" },
    { label: "Crop Health", to: "#crop-health-preview" },
    { label: "Alerts", to: "#alerts-preview" },
    { label: "Our Mission", to: "#mission" }
  ];

  const handleAnchorClick = (e, to) => {
    if (to.startsWith("#")) {
      e.preventDefault();
      const element = document.getElementById(to.substring(1));
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
      setMobileMenuOpen(false);
    }
  };

  return (
    <nav className="nav-wrapper">
      {/* Top Main Navigation */}
      <div className="container nav-main">
        <Link to="/" className="logo-container">
          <Sprout className="logo-icon" size={28} strokeWidth={2.5} />
          <span>AgriGuard</span>
        </Link>

        {/* Desktop Links */}
        <ul className="nav-links">
          {navLinks.map((link) => (
            <li key={link.label}>
              {link.to.startsWith("#") ? (
                <a href={link.to} onClick={(e) => handleAnchorClick(e, link.to)}>
                  {link.label}
                </a>
              ) : (
                <Link to={link.to}>{link.label}</Link>
              )}
            </li>
          ))}
        </ul>

        {/* Desktop CTA actions */}
        <div className="nav-actions">
          <Link to="/app" className="login-link">Login</Link>
          <Link to="/app" className="login-link">Register</Link>
          <button onClick={handleCheckCrop} className="btn btn-secondary">
            CHECK MY CROP →
          </button>
        </div>

        {/* Mobile Hamburger Toggle */}
        <button
          className="mobile-nav-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Level 2 Sub-Nav Action Area */}
      <div className="nav-sub">
        <div className="container nav-sub-container">
          <ul className="nav-sub-links">
            <li>
              <Link to="/app">My Fields</Link>
            </li>
            <li>
              <Link to="/app/history">Disease History</Link>
            </li>
            <li>
              <Link to="/app/alerts">Weather Alerts</Link>
            </li>
            <li>
              <a href="#help" onClick={(e) => handleAnchorClick(e, "#how-it-works")}>Help</a>
            </li>
          </ul>

          <div className="nav-search">
            <Search size={14} className="search-icon" style={{ marginRight: "4px" }} />
            <input type="text" placeholder="Search crops, pests, diseases..." aria-label="Search" />
          </div>
        </div>
      </div>

      {/* Mobile Slide-down Menu */}
      {mobileMenuOpen && (
        <ul className="mobile-nav-menu">
          {navLinks.map((link) => (
            <li key={link.label}>
              {link.to.startsWith("#") ? (
                <a href={link.to} onClick={(e) => handleAnchorClick(e, link.to)}>
                  {link.label}
                </a>
              ) : (
                <Link to={link.to} onClick={() => setMobileMenuOpen(false)}>
                  {link.label}
                </Link>
              )}
            </li>
          ))}
          <li style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <Link
              to="/app"
              onClick={() => setMobileMenuOpen(false)}
              className="btn btn-outline-white"
              style={{ textAlign: "center" }}
            >
              Login / Register
            </Link>
            <button
              onClick={handleCheckCrop}
              className="btn btn-secondary btn-block"
              style={{ justifyContent: "center" }}
            >
              CHECK MY CROP →
            </button>
          </li>
        </ul>
      )}
    </nav>
  );
}
