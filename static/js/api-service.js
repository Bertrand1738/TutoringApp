/**
 * API Service for FrenchTutor Hub
 * Handles all API calls using the centralized API configuration
 */

// Create API service object
const api = {
    // Authentication related methods
    auth: {
        // Register a new user
        register: async (userData) => {
            try {
                console.log('Starting registration process');
                
                const response = await fetch(API_CONFIG.AUTH.REGISTER, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData),
                    credentials: 'include', // Include cookies in request
                });
                
                // Handle different response types
                const contentType = response.headers.get('content-type');
                let data;
                
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    // Handle non-JSON responses
                    const text = await response.text();
                    data = { detail: text || 'Unknown response from server' };
                }
                
                // Check for specific validation errors
                if (!response.ok) {
                    console.error('Registration response not OK:', response.status, data);
                    
                    // Format validation errors for better display
                    if (data.username || data.email || data.password) {
                        let errorMessages = [];
                        
                        if (data.username) errorMessages.push(`Username: ${data.username.join(', ')}`);
                        if (data.email) errorMessages.push(`Email: ${data.email.join(', ')}`);
                        if (data.password) errorMessages.push(`Password: ${data.password.join(', ')}`);
                        if (data.non_field_errors) errorMessages.push(data.non_field_errors.join(', '));
                        
                        throw new Error(errorMessages.join('\n'));
                    }
                    
                    throw new Error(data.detail || 'Registration failed');
                }
                
                console.log('Registration successful');
                return data;
            } catch (error) {
                console.error('Registration error:', error);
                throw error;
            }
        },
        
        // Login user
        login: async (credentials) => {
            try {
                console.log('Attempting login for user:', credentials.username);
                
                const response = await fetch(API_CONFIG.AUTH.LOGIN, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(credentials),
                    credentials: 'include', // Include cookies in request
                });
                
                // Handle different response types
                const contentType = response.headers.get('content-type');
                let data;
                
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    // Handle non-JSON responses
                    const text = await response.text();
                    data = { detail: text || 'Unknown response from server' };
                }
                
                if (!response.ok) {
                    console.error('Login response not OK:', response.status, data);
                    throw new Error(data.detail || data.non_field_errors?.join(', ') || 'Login failed');
                }
                
                console.log('Login successful, received tokens');
                
                // Store tokens in local storage
                if (data.access) {
                    localStorage.setItem('access_token', data.access);
                    console.log('Access token stored');
                }
                if (data.refresh) {
                    localStorage.setItem('refresh_token', data.refresh);
                    console.log('Refresh token stored');
                }
                
                // Store user info if available
                if (data.user) {
                    localStorage.setItem('user_info', JSON.stringify(data.user));
                    console.log('User info stored');
                }
                
                return data;
            } catch (error) {
                console.error('Login error:', error);
                throw error;
            }
        },
        
        // Get user profile
        getProfile: async () => {
            try {
                const token = localStorage.getItem('access_token');
                
                if (!token) {
                    throw new Error('No authentication token found');
                }
                
                const response = await fetch(API_CONFIG.AUTH.PROFILE, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to get profile');
                }
                
                return data;
            } catch (error) {
                console.error('Get profile error:', error);
                throw error;
            }
        },
        
        // Logout user
        logout: () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        },
    },
    
    // Courses related methods
    courses: {
        // Get list of courses
        getAll: async (filters = {}) => {
            try {
                let url = new URL(window.location.origin + API_CONFIG.COURSES.LIST);
                
                // Add filters as query parameters
                Object.keys(filters).forEach(key => {
                    if (filters[key] !== null && filters[key] !== undefined) {
                        url.searchParams.append(key, filters[key]);
                    }
                });
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to get courses');
                }
                
                return data;
            } catch (error) {
                console.error('Get courses error:', error);
                throw error;
            }
        },
        
        // Get featured courses
        getFeatured: async (limit = 3) => {
            try {
                const url = new URL(window.location.origin + API_CONFIG.COURSES.FEATURED);
                url.searchParams.append('limit', limit);
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to get featured courses');
                }
                
                return data;
            } catch (error) {
                console.error('Get featured courses error:', error);
                throw error;
            }
        },
        
        // Get course details
        getById: async (courseId) => {
            try {
                const response = await fetch(API_CONFIG.COURSES.DETAIL(courseId));
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to get course details');
                }
                
                return data;
            } catch (error) {
                console.error(`Get course ${courseId} error:`, error);
                throw error;
            }
        },
        
        // Get course content
        getContent: async (courseId) => {
            try {
                const token = localStorage.getItem('access_token');
                
                if (!token) {
                    throw new Error('No authentication token found');
                }
                
                const response = await fetch(API_CONFIG.COURSES.CONTENT(courseId), {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to get course content');
                }
                
                return data;
            } catch (error) {
                console.error(`Get course ${courseId} content error:`, error);
                throw error;
            }
        },
    },
    
    // Enrollments related methods
    enrollments: {
        // Enroll in a course
        create: async (courseId) => {
            try {
                const token = localStorage.getItem('access_token');
                
                if (!token) {
                    throw new Error('No authentication token found');
                }
                
                const response = await fetch(API_CONFIG.ENROLLMENTS.CREATE, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                    body: JSON.stringify({ course: courseId }),
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to enroll in course');
                }
                
                return data;
            } catch (error) {
                console.error('Enrollment error:', error);
                throw error;
            }
        },
        
        // Get user enrollments
        getUserEnrollments: async () => {
            try {
                const token = localStorage.getItem('access_token');
                
                if (!token) {
                    throw new Error('No authentication token found');
                }
                
                const response = await fetch(API_CONFIG.ENROLLMENTS.USER, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to get enrollments');
                }
                
                return data;
            } catch (error) {
                console.error('Get enrollments error:', error);
                throw error;
            }
        },
        
        // Update enrollment progress
        updateProgress: async (enrollmentId, progress) => {
            try {
                const token = localStorage.getItem('access_token');
                
                if (!token) {
                    throw new Error('No authentication token found');
                }
                
                const response = await fetch(API_CONFIG.ENROLLMENTS.UPDATE(enrollmentId), {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                    body: JSON.stringify({ progress }),
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to update progress');
                }
                
                return data;
            } catch (error) {
                console.error('Update progress error:', error);
                throw error;
            }
        },
    },
};

// Define getFeaturedCourses as a wrapper for the courses.getFeatured method
api.getFeaturedCourses = api.courses.getFeatured;

// Export to window
window.api = api;
