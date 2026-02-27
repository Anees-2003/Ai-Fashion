const isProd = import.meta.env.PROD;
export const API_URL = isProd ? "https://aifashion-backend.onrender.com/api" : "/api";
export const UPLOADS_URL = isProd ? "https://aifashion-backend.onrender.com/uploads" : "/uploads";
