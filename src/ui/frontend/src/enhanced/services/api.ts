import { api as coreApi } from '../../services/api';

// Enhanced UI components expect an `api` object with certain method names.
// We re-export the existing frontend API to keep everything in sync with the real backend.
export const api = coreApi;

export default api;



