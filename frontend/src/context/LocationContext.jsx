import React, { createContext, useContext, useState } from "react";
import { locationsList } from "../data/locations";

const LocationContext = createContext();

// Haversine formula to calculate distance in km
export function getHaversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c; // Distance in kilometers
}

export function LocationProvider({ children }) {
  // Default to Jaipur as initial mock data
  const [selectedLocation, setSelectedLocationState] = useState(() => {
    const saved = localStorage.getItem("selected_location_state");
    return saved ? JSON.parse(saved) : locationsList[0];
  });

  const setLocation = (loc) => {
    setSelectedLocationState(loc);
    localStorage.setItem("selected_location_state", JSON.stringify(loc));
    // Trigger custom event so storage shifts update other elements if needed
    window.dispatchEvent(new Event("selectedLocationChanged"));
  };

  const updateLocationByCoordinates = (lat, lon) => {
    let minDistance = Infinity;
    let closestCity = null;

    locationsList.forEach((city) => {
      const dist = getHaversineDistance(lat, lon, city.latitude, city.longitude);
      if (dist < minDistance) {
        minDistance = dist;
        closestCity = city;
      }
    });

    if (minDistance <= 150 && closestCity) {
      const matchedLoc = {
        city: closestCity.city,
        state: closestCity.state,
        country: closestCity.country,
        latitude: lat,
        longitude: lon
      };
      setLocation(matchedLoc);
      return matchedLoc;
    } else {
      const customLoc = {
        city: "Custom Location",
        state: "",
        country: "India",
        latitude: lat,
        longitude: lon
      };
      setLocation(customLoc);
      return customLoc;
    }
  };

  return (
    <LocationContext.Provider
      value={{
        selectedLocation,
        setLocation,
        updateLocationByCoordinates
      }}
    >
      {children}
    </LocationContext.Provider>
  );
}

export function useLocationContext() {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error("useLocationContext must be used within LocationProvider");
  }
  return context;
}
