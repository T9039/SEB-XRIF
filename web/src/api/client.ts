import axios from "axios";

/**
 * Shared Axios instance. In development Vite proxies `/api` to the FastAPI
 * service (see vite.config.ts). In production nginx proxies `/api` to the API
 * container. Set VITE_API_URL to override.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 10000,
});
