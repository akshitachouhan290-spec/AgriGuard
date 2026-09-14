import React from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import { LocationProvider } from "./context/LocationContext";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import CheckCrop from "./pages/CheckCrop";
import Fields from "./pages/Fields";
import History from "./pages/History";
import Alerts from "./pages/Alerts";
import Profile from "./pages/Profile";

export default function App() {
  return (
    <LocationProvider>
      <Router>
        <Routes>
          {/* Public Landing Page */}
          <Route path="/" element={<LandingPage />} />

          {/* Farmer Application */}
          <Route path="/app" element={<Dashboard />} />
          <Route path="/app/check" element={<CheckCrop />} />
          <Route path="/app/fields" element={<Fields />} />
          <Route path="/app/history" element={<History />} />
          <Route path="/app/alerts" element={<Alerts />} />
          <Route path="/app/profile" element={<Profile />} />
        </Routes>
      </Router>
    </LocationProvider>
  );
}

