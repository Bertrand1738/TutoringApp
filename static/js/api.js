/**
 * FrenchTutor Hub API Service
 * Handles all API communication with the backend
 */
class ApiService {
    constructor() {
        // Use the centralized API configuration if available
        this.baseUrl = window.API_CONFIG ? window.API_CONFIG.BASE_URL : '/api';
        this.authTokenKey = 'frenchtutor_auth_token';
        
        console.log('API Service initialized with base URL:', this.baseUrl);
    }

    /**
     * Get the authorization header with JWT token
     * @returns {Object} Headers object with Authorization
     */
    getAuthHeader() {
        const token = localStorage.getItem(this.authTokenKey);
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isAuthenticated() {
        return localStorage.getItem(this.authTokenKey) !== null;
    }

    /**
     * Store JWT token in localStorage
     * @param {string} token - JWT token
     */
    setAuthToken(token) {
        localStorage.setItem(this.authTokenKey, token);
    }

    /**
     * Clear JWT token from localStorage
     */
    clearAuthToken() {
        localStorage.removeItem(this.authTokenKey);
    }

    /**
     * Make API request with proper error handling
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        console.log(`Making API request to: ${url}`, options);
        
        try {
            const response = await fetch(url, options);
            console.log(`Response status: ${response.status}`);
            
            // Parse JSON response if possible
            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
                console.log('Non-JSON response:', data);
            }
            
            // Check if response is successful
            if (!response.ok) {
                throw {
                    status: response.status,
                    data: data,
                    message: data.detail || 'Something went wrong'
                };
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Login user and get JWT token
     * @param {string} username - User's username
     * @param {string} password - User's password
     * @returns {Promise<Object>} User data with token
     */
    async login(username, password) {
        // Use the centralized API configuration for login endpoint
        const loginEndpoint = window.API_CONFIG ? window.API_CONFIG.AUTH.LOGIN : '/api/auth/login/';
        console.log('Using login endpoint:', loginEndpoint);
        
        // Login endpoint doesn't need auth header, so using custom headers
        const data = await this.request(loginEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (data.access) {
            this.setAuthToken(data.access);
        }
        
        return data;
    }

    /**
     * Register new user
     * @param {Object} userData - User registration data
     * @returns {Promise<Object>} Created user data
     */
    async register(userData) {
        // Use the centralized API configuration for register endpoint
        const registerEndpoint = window.API_CONFIG ? window.API_CONFIG.AUTH.REGISTER : '/api/auth/register/';
        console.log('Using register endpoint:', registerEndpoint);
        
        // Registration doesn't need auth header
        return await this.request(registerEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
    }

    /**
     * Logout user (client-side only)
     */
    logout() {
        this.clearAuthToken();
        window.location.href = '/login/';
    }

    /**
     * Get current user profile
     * @returns {Promise<Object>} User profile data
     */
    async getUserProfile() {
        return await this.get('/accounts/profile/');
    }

    /**
     * Update user profile
     * @param {Object} profileData - Updated profile data
     * @returns {Promise<Object>} Updated profile
     */
    async updateUserProfile(profileData) {
        return await this.patch('/accounts/profile/', profileData);
    }

    /**
     * Generic GET request to an endpoint
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async get(endpoint, options = {}) {
        const { params = {} } = options;
        const queryParams = new URLSearchParams(params).toString();
        const url = `${endpoint}${queryParams ? '?' + queryParams : ''}`;
        
        return await this.request(url, {
            method: 'GET',
            headers: this.getAuthHeader(),
        });
    }
    
    /**
     * Generic POST request to an endpoint
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to send
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async post(endpoint, data, options = {}) {
        return await this.request(endpoint, {
            method: 'POST',
            headers: this.getAuthHeader(),
            body: JSON.stringify(data),
            ...options
        });
    }
    
    /**
     * Generic PUT request to an endpoint
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to send
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async put(endpoint, data, options = {}) {
        return await this.request(endpoint, {
            method: 'PUT',
            headers: this.getAuthHeader(),
            body: JSON.stringify(data),
            ...options
        });
    }
    
    /**
     * Generic PATCH request to an endpoint
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to send
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async patch(endpoint, data, options = {}) {
        return await this.request(endpoint, {
            method: 'PATCH',
            headers: this.getAuthHeader(),
            body: JSON.stringify(data),
            ...options
        });
    }
    
    /**
     * Generic DELETE request to an endpoint
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async delete(endpoint, options = {}) {
        return await this.request(endpoint, {
            method: 'DELETE',
            headers: this.getAuthHeader(),
            ...options
        });
    }
    
    /**
     * Get list of all courses
     * @param {Object} filters - Optional filter parameters
     * @returns {Promise<Array>} List of courses
     */
    async getCourses(filters = {}) {
        return await this.get('/courses/', { params: filters });
    }

    /**
     * Get course details by ID
     * @param {number} courseId - Course ID
     * @returns {Promise<Object>} Course details
     */
    async getCourseById(courseId) {
        return await this.get(`/courses/${courseId}/`);
    }

    /**
     * Enroll in a course
     * @param {number} courseId - Course ID
     * @returns {Promise<Object>} Enrollment details
     */
    async enrollInCourse(courseId) {
        return await this.post(`/enrollments/`, { course: courseId });
    }

    /**
     * Get user enrollments
     * @returns {Promise<Array>} List of user enrollments
     */
    async getUserEnrollments() {
        return await this.get('/enrollments/user/');
    }

    /**
     * Update enrollment progress
     * @param {number} enrollmentId - Enrollment ID
     * @param {number} progress - Progress percentage (0-100)
     * @returns {Promise<Object>} Updated enrollment
     */
    async updateEnrollmentProgress(enrollmentId, progress) {
        return await this.patch(`/enrollments/${enrollmentId}/`, { progress });
    }

    /**
     * Get upcoming live sessions
     * @returns {Promise<Array>} List of upcoming sessions
     */
    async getUpcomingSessions() {
        return await this.get('/live-sessions/upcoming/');
    }
    
    /**
     * Get featured courses
     * @param {number} limit - Number of courses to return
     * @returns {Promise<Array>} List of featured courses
     */
    async getFeaturedCourses(limit = 3) {
        // Use the raw request method to bypass authentication for this public endpoint
        try {
            const featuredEndpoint = `/api/courses/?featured=true&limit=${limit}`;
            console.log('Fetching featured courses from:', featuredEndpoint);
            
            return await this.request(featuredEndpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error fetching featured courses:', error);
            throw error;
        }
    }
}

// Create global API service instance
const api = new ApiService();

// Export for use in other scripts
window.api = api;
