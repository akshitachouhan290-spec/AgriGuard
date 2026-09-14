import { cropsList } from "./crops";
import { locationsList } from "./locations";

// Export the centralized crop list mapped to select-dropdown value/label format
export const cropList = cropsList.map((c) => ({
  value: c.name,
  label: `${c.name} ${c.icon}`
}));

export const mockFarmer = {
  name: "Rajesh",
  phone: "9999999999",
  language: "Hindi",
  village: "Jaipur",
  district: "Jaipur",
  state: "Rajasthan"
};

// Initial fields setup - anchored to original location strings
export const mockFields = [
  {
    id: "field-1",
    name: "Tomato Field",
    crop: "Tomato",
    area: "2 acres",
    location: "Jaipur, Rajasthan",
    currentRisk: "High",
    lastAnalysis: "23 Aug",
    diseaseDetected: "Early Blight",
    severity: "Moderate"
  },
  {
    id: "field-2",
    name: "Wheat Field",
    crop: "Wheat",
    area: "3 acres",
    location: "Jaipur, Rajasthan",
    currentRisk: "Low",
    lastAnalysis: "22 Aug",
    diseaseDetected: "Healthy",
    severity: "None"
  }
];

export const mockWeather = {
  temp: 31,
  feelsLike: 33,
  humidity: 72,
  rainProbability: 60,
  windSpeed: 14,
  condition: "Rain expected"
};

export const mockHistory = [
  {
    id: "hist-1",
    date: "23 Aug",
    crop: "Tomato",
    disease: "Early Blight",
    confidence: 91,
    risk: "High",
    severity: "Moderate",
    why: [
      "Disease detected in photo",
      "High humidity in your region (72%)",
      "Rain expected within 24 hours (60%)",
      "Previous local case of Early Blight recorded"
    ],
    advice: [
      "Check nearby tomato plants immediately.",
      "Remove and carefully destroy badly affected leaves to prevent spreading.",
      "Avoid watering plants from overhead; water at the base of the soil to keep leaves dry.",
      "Follow locally recommended control practices for Early Blight."
    ]
  },
  {
    id: "hist-2",
    date: "20 Aug",
    crop: "Tomato",
    disease: "Early Symptoms",
    confidence: 82,
    risk: "Medium",
    severity: "Mild",
    why: [
      "Faint leaf spotting detected",
      "Warm temperatures and moderate humidity",
      "No recent rain recorded"
    ],
    advice: [
      "Monitor these plants daily for spots expanding.",
      "Ensure proper air circulation by pruning excess foliage.",
      "Keep field clear of weeds and crop debris."
    ]
  },
  {
    id: "hist-3",
    date: "15 Aug",
    crop: "Tomato",
    disease: "Healthy",
    confidence: 95,
    risk: "Low",
    severity: "None",
    why: [
      "No visible spots or pest damage detected",
      "Optimal weather conditions for growth"
    ],
    advice: [
      "Continue regular crop inspection twice a week.",
      "Maintain crop rotation protocols in the next season.",
      "Apply organic compost to support strong plant immunity."
    ]
  }
];

export const mockAlerts = [
  {
    id: "alert-1",
    title: "🚨 HIGH RISK",
    message: "Possible Early Blight detected in Tomato Field. High humidity and rain expected.",
    fieldId: "field-1",
    type: "disease",
    date: "23 Aug"
  },
  {
    id: "alert-2",
    title: "⚠️ WEATHER WARNING",
    message: "High probability of rainfall (60%) expected over the next 24 hours.",
    fieldId: "all",
    type: "weather",
    date: "24 Aug"
  }
];
