import React from "react";

export default function Button({
  children,
  onClick,
  type = "button",
  variant = "primary", // primary, secondary, outline, outline-white
  size = "medium", // small, medium, large
  disabled = false,
  block = false,
  className = "",
  ...props
}) {
  const baseClass = "btn";
  const variantClass = `btn-${variant}`;
  const sizeClass = size === "large" ? "btn-large" : "";
  const blockClass = block ? "btn-block" : "";

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClass} ${variantClass} ${sizeClass} ${blockClass} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
