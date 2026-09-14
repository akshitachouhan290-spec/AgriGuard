const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const FARMER_ID = Number(localStorage.getItem("crop_health_farmer_id") || 1);

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const text = await response.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { detail: text }; }
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

const cropCache = {};
export const getFarmer = () => request(`/farmers/${FARMER_ID}`);
export const saveFarmer = (profileData) => request(`/farmers/${FARMER_ID}`, {
  method:"PATCH", headers:{"Content-Type":"application/json"},
  body: JSON.stringify(profileData)
});
export const getFields = () => request(`/fields/farmer/${FARMER_ID}`);
export async function createField(fieldData) {
  let crops = cropCache.list;
  if (!crops) { crops = await request("/crops/"); cropCache.list = crops; }
  const crop = crops.find(c => c.name.toLowerCase() === String(fieldData.crop || "").toLowerCase()) || crops[0];
  return request("/fields/", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      farmer_id:FARMER_ID, field_name:fieldData.name, crop_id:crop.id,
      area:parseFloat(fieldData.area) || 0,
      latitude:fieldData.latitude ?? undefined, longitude:fieldData.longitude ?? undefined,
      location:fieldData.location || ""
    })
  });
}
export async function analyzeCrop(photoData, cropType, fieldId) {
  const form = new FormData();
  form.append("farmer_id", FARMER_ID);
  form.append("field_id", fieldId);
  form.append("crop", cropType);
  if (photoData instanceof File) form.append("file", photoData);
  else {
    // Demo capture still needs a valid image; use a tiny generated PNG.
    const blob = await fetch("/favicon.svg").then(r=>r.blob());
    form.append("file", blob, "captured-crop.svg");
  }
  return request("/analyze/", {method:"POST", body:form});
}
export const getHistory = () => request(`/analyze/history/${FARMER_ID}`);
export const getAlerts = () => request(`/api/alerts/${FARMER_ID}`);
export const getWeather = (lat,lon) => request(`/api/weather?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
export const getRiskAnalysis = (_cropId,fieldId) => request(`/api/risk/${fieldId}`);
