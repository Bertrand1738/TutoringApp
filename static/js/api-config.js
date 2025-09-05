/**
 * API Configuration for FrenchTutor Hub
 * Centralized API endpoint configuration to ensure consistency
 */

// API base URL configuration
const API_CONFIG = {
    BASE_URL: '/api',
    AUTH: {
        REGISTER: '/api/auth/register/',
        LOGIN: '/api/auth/login/',
        REFRESH: '/api/auth/token/refresh/',
        PROFILE: '/api/auth/me/',
        ENROLLMENTS: '/api/auth/me/enrollments/',
        ORDERS: '/api/auth/me/orders/',
    },
    COURSES: {
        LIST: '/api/courses/',
        FEATURED: '/api/courses/?featured=true',
        DETAIL: (id) => `/api/courses/${id}/`,
        CONTENT: (id) => `/api/courses/${id}/content/`,
    },
    ENROLLMENTS: {
        CREATE: '/api/enrollments/',
        USER: '/api/enrollments/user/',
        UPDATE: (id) => `/api/enrollments/${id}/`,
    },
    PAYMENTS: {
        CREATE: '/api/payments/create/',
        VERIFY: '/api/payments/verify/',
        HISTORY: '/api/payments/history/',
    },
    LIVE: {
        UPCOMING: '/api/live/upcoming/',
        SESSION: (id) => `/api/live/sessions/${id}/`,
        JOIN: (id) => `/api/live/sessions/${id}/join/`,
    }
};

// Export for use in other files
window.API_CONFIG = API_CONFIG;
