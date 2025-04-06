import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

console.log("API Service Loaded. API Base URL:", API_BASE_URL);

export const fetchCryptoData = async (startDate = null, endDate = null) => {
  console.log("fetchCryptoData called with dates:", { startDate, endDate });
  try {
    const params = {};
    if (startDate) {
        try { params.from = startDate.toISOString().split('T')[0]; }
        catch (e) { console.error("Error formatting start date:", startDate, e); }
    }
    if (endDate) {
         try { params.to = endDate.toISOString().split('T')[0]; }
         catch (e) { console.error("Error formatting end date:", endDate, e); }
    }

    const targetUrl = `${API_BASE_URL}/crypto-data`;
    console.log(`Attempting to fetch crypto data from: ${targetUrl} with params:`, params);

    const response = await axios.get(targetUrl, { params });

    console.log("API Response Received:", response.data);
    return response.data;

  } catch (error) {
    console.error("Error fetching crypto data:", error);
    if (error.response) { console.error("Error data:", error.response.data); console.error("Error status:", error.response.status); console.error("Error headers:", error.response.headers); }
    else if (error.request) { console.error("Error request:", error.request); }
    else { console.error('Error message:', error.message); }
    return null;
  }
};