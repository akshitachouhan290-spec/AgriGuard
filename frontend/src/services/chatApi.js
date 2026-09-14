const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
export async function sendChatMessage(message) {
  const r = await fetch(`${API_BASE}/api/chat`, {
    method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({message})
  });
  if (!r.ok) throw new Error("Chat service unavailable");
  return r.json();
}
