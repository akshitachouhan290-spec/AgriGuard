import React, { useState, useEffect } from "react";
import { Check, Loader2 } from "lucide-react";

export default function LoadingAnalysis({ onComplete }) {
  const [steps, setSteps] = useState([
    { id: 1, text: "Identifying crop", status: "pending" }, // pending, loading, done
    { id: 2, text: "Checking possible diseases", status: "pending" },
    { id: 3, text: "Checking weather info", status: "pending" },
    { id: 4, text: "Checking previous history", status: "pending" }
  ]);

  useEffect(() => {
    // Step 1: Start immediately
    setSteps(prev => prev.map(s => s.id === 1 ? { ...s, status: "loading" } : s));

    const timeouts = [
      setTimeout(() => {
        setSteps(prev => prev.map(s => {
          if (s.id === 1) return { ...s, status: "done" };
          if (s.id === 2) return { ...s, status: "loading" };
          return s;
        }));
      }, 500),

      setTimeout(() => {
        setSteps(prev => prev.map(s => {
          if (s.id === 2) return { ...s, status: "done" };
          if (s.id === 3) return { ...s, status: "loading" };
          return s;
        }));
      }, 1000),

      setTimeout(() => {
        setSteps(prev => prev.map(s => {
          if (s.id === 3) return { ...s, status: "done" };
          if (s.id === 4) return { ...s, status: "loading" };
          return s;
        }));
      }, 1500),

      setTimeout(() => {
        setSteps(prev => prev.map(s => s.id === 4 ? { ...s, status: "done" } : s));
      }, 2000),

      setTimeout(() => {
        if (onComplete) onComplete();
      }, 2400)
    ];

    return () => {
      timeouts.forEach(t => clearTimeout(t));
    };
  }, [onComplete]);

  return (
    <div className="loader-container">
      <div className="spinner" />
      <h3>Checking your crop...</h3>
      <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginTop: "0.25rem" }}>
        Analyzing leaves and environmental metadata
      </p>

      <ul className="loader-status-list">
        {steps.map((step) => {
          const isDone = step.status === "done";
          const isLoading = step.status === "loading";
          
          return (
            <li
              key={step.id}
              className={`loader-status-item ${isDone ? "done" : ""} ${isLoading ? "current" : ""}`}
            >
              {isDone ? (
                <Check size={18} style={{ color: "var(--primary)" }} />
              ) : isLoading ? (
                <Loader2 size={18} className="animate-spin" style={{ color: "var(--secondary)", animation: "spin 1.5s infinite linear" }} />
              ) : (
                <div style={{ width: 18, height: 18, borderRadius: "50%", border: "2px solid var(--border)" }} />
              )}
              <span>
                {step.text}
                {isLoading && "..."}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
