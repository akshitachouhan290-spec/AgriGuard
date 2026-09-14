import React, { useState, useEffect, useRef } from "react";
import { MessageCircle, X, Send, Bot, Loader2, MoreVertical, Plus, Trash2 } from "lucide-react";
import { sendChatMessage } from "../services/chatApi";

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  
  // Menu and modal states
  const [menuOpen, setMenuOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const menuRef = useRef(null);

  // Initialize with welcome message
  useEffect(() => {
    const timeString = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages([
      {
        id: "welcome",
        sender: "bot",
        text: "👋 Hello! I'm your AgriGuard Crop Health Assistant.\nHow can I help you today?",
        time: timeString
      }
    ]);
  }, []);

  // Scroll to bottom whenever messages or typing state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 300);
    }
  }, [isOpen]);

  // Click outside menu handler to close dropdown
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const suggestions = [
    { label: "🌱 What is wrong with my crop?", query: "What is wrong with my crop?" },
    { label: "🌦️ Check my crop risk", query: "Check my crop risk" },
    { label: "📋 Show my latest crop report", query: "Show my latest crop report" },
    { label: "🌾 Give me crop advice", query: "Give me crop advice" }
  ];

  const handleSendMessage = async (text) => {
    if (!text.trim() || isTyping) return;

    const timeString = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    
    // Add user message
    const userMsg = {
      id: `msg-${Date.now()}-user`,
      sender: "user",
      text: text,
      time: timeString
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsTyping(true);
    setShowSuggestions(false); // Hide suggestions once user starts conversing

    try {
      const response = await sendChatMessage(text);
      const botTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      
      const botMsg = {
        id: `msg-${Date.now()}-bot`,
        sender: "bot",
        text: response.text,
        time: botTime
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error("Chat error", error);
      const errorTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      const errorMsg = {
        id: `msg-${Date.now()}-error`,
        sender: "bot",
        text: "⚠️ Sorry, I encountered an error. Please try again later.",
        time: errorTime
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const handleSuggestionClick = (query) => {
    handleSendMessage(query);
  };

  // Resets conversation immediately to a clean welcome state
  const handleNewChat = () => {
    const timeString = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages([
      {
        id: "welcome",
        sender: "bot",
        text: "👋 Hello! I'm your AgriGuard Crop Health Assistant.\nHow can I help you today?",
        time: timeString
      }
    ]);
    setShowSuggestions(true);
    setInputValue("");
    setIsTyping(false);
    setMenuOpen(false);
  };

  // Opens deletion confirmation
  const handleDeleteChatClick = () => {
    setMenuOpen(false);
    setShowDeleteConfirm(true);
  };

  // Resets conversation on confirmation
  const confirmDeleteChat = () => {
    const timeString = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages([
      {
        id: "welcome",
        sender: "bot",
        text: "👋 Hello! I'm your AgriGuard Crop Health Assistant.\nHow can I help you today?",
        time: timeString
      }
    ]);
    setShowSuggestions(true);
    setInputValue("");
    setIsTyping(false);
    setShowDeleteConfirm(false);
  };

  return (
    <div className="chatbot-wrapper">
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`chatbot-float-btn ${isOpen ? "active" : ""}`}
        aria-label={isOpen ? "Close AgriGuard Assistant" : "Open AgriGuard Assistant"}
        title={isOpen ? "Close Assistant" : "Open Assistant"}
      >
        {isOpen ? <X size={26} /> : <MessageCircle size={26} />}
      </button>

      {/* Chat Popup Window */}
      <div className={`chatbot-popup ${isOpen ? "open" : ""}`} aria-hidden={!isOpen}>
        {/* Header */}
        <div className="chatbot-header">
          <div className="chatbot-header-info">
            <div className="chatbot-avatar">
              <Bot size={20} />
            </div>
            <div>
              <h4 className="chatbot-title">AgriGuard</h4>
              <span className="chatbot-subtitle">AgriGuard Assistant</span>
            </div>
          </div>
          
          <div className="chatbot-header-actions" style={{ display: "flex", alignItems: "center", gap: "0.25rem", position: "relative" }}>
            {/* Options Dropdown Menu */}
            <div className="chatbot-menu-container" ref={menuRef}>
              <button
                type="button"
                onClick={() => setMenuOpen(!menuOpen)}
                className={`chatbot-menu-toggle-btn ${menuOpen ? "active" : ""}`}
                aria-label="Chat options"
                title="Options"
              >
                <MoreVertical size={18} />
              </button>
              
              {menuOpen && (
                <div className="chatbot-menu-dropdown">
                  <button
                    type="button"
                    onClick={handleNewChat}
                    className="chatbot-menu-item"
                    aria-label="Start new chat"
                  >
                    <Plus size={14} />
                    <span>New Chat</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleDeleteChatClick}
                    className="chatbot-menu-item delete-item"
                    aria-label="Delete chat conversation"
                  >
                    <Trash2 size={14} />
                    <span>Delete Chat</span>
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="chatbot-close-btn"
              aria-label="Close AgriGuard Assistant"
              title="Close"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Message Area */}
        <div className="chatbot-messages">
          {/* Deletion Confirmation Modal Overlay */}
          {showDeleteConfirm && (
            <div className="chatbot-confirm-overlay">
              <div className="chatbot-confirm-modal">
                <h5 className="chatbot-confirm-title">Delete this chat?</h5>
                <p className="chatbot-confirm-text">This will remove the current conversation.</p>
                <div className="chatbot-confirm-actions">
                  <button
                    type="button"
                    className="chatbot-confirm-btn cancel-btn"
                    onClick={() => setShowDeleteConfirm(false)}
                    aria-label="Cancel deletion"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="chatbot-confirm-btn delete-btn"
                    onClick={confirmDeleteChat}
                    aria-label="Confirm delete conversation"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`chatbot-message-row ${msg.sender === "user" ? "user-row" : "bot-row"}`}>
              {msg.sender === "bot" && (
                <div className="chatbot-msg-avatar">
                  <Bot size={14} />
                </div>
              )}
              <div className={`chatbot-message-bubble ${msg.sender === "user" ? "user-bubble" : "bot-bubble"}`}>
                <div className="chatbot-message-text">
                  {msg.text.split("\n").map((line, index) => (
                    <React.Fragment key={index}>
                      {line}
                      {index < msg.text.split("\n").length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
                <div className="chatbot-message-time">{msg.time}</div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="chatbot-message-row bot-row">
              <div className="chatbot-msg-avatar">
                <Bot size={14} />
              </div>
              <div className="chatbot-message-bubble bot-bubble typing-bubble">
                <div className="chatbot-typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          {/* Suggestions List (shown if showSuggestions is true) */}
          {showSuggestions && !isTyping && (
            <div className="chatbot-suggestions-container">
              <span className="chatbot-suggestions-title">Common Questions:</span>
              <div className="chatbot-suggestions-list">
                {suggestions.map((sug, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSuggestionClick(sug.query)}
                    className="chatbot-suggestion-btn"
                    aria-label={`Ask suggestion: ${sug.query}`}
                  >
                    {sug.label}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar Form */}
        <form onSubmit={handleSubmit} className="chatbot-input-bar">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message here..."
            className="chatbot-input"
            aria-label="Type message for AgriGuard Assistant"
            disabled={isTyping}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className="chatbot-send-btn"
            aria-label="Send message"
            title="Send"
          >
            {isTyping ? (
              <Loader2 size={18} className="animate-spin-slow" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
