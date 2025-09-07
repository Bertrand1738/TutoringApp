/**
 * Main JavaScript file for FrenchTutor Hub
 * Handles UI interactions and initializes API functionality
 */

// Main initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize form handlers
    initializeForms();
    
    // Initialize UI components
    initializeUI();
    
    // Check if we're on dashboard page and load data if needed
    loadPageSpecificData();
});

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize form handlers for login, registration, etc.
 */
function initializeForms() {
    // Login form handler - handled directly in login.html
    // to prevent endpoint confusion
    
    // Registration form handler - handled directly in register.html
    // to prevent endpoint confusion
    
    // Profile update form handler
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
    
    // Setup course enrollment buttons
    setupEnrollButtons();
    
    // Course filter form
    const courseFilterForm = document.getElementById('course-filter-form');
    if (courseFilterForm) {
        courseFilterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            loadCourseListings();
        });
        
        // Also listen to change events on select elements
        const filterSelects = courseFilterForm.querySelectorAll('select');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => loadCourseListings());
        });
    }
}

/**
 * Initialize UI components and event listeners
 */
function initializeUI() {
    // Handle logout button clicks
    const logoutButtons = document.querySelectorAll('.logout-button');
    if (logoutButtons.length > 0) {
        logoutButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                
                try {
                    // Get CSRF token for the logout request
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
                    
                    // Call logout endpoint to clear server-side session
                    await fetch('/api/auth/logout/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        },
                        credentials: 'same-origin'
                    });
                } catch (error) {
                    console.warn('Error during logout:', error);
                    // Continue with client-side logout even if server-side logout fails
                }
                
                // Clear all stored tokens
                localStorage.removeItem('token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('access_token');
                sessionStorage.removeItem('access_token');
                
                // Clear cookies
                document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
                document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
                
                // Redirect to login page
                window.location.href = '/login/';
            });
        });
    }
    
    // Check URL params for messages (like registration success)
    checkUrlParamsForMessages();
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        console.log('Navbar found:', navbar);
        // Make sure navbar is visible
        navbar.style.display = 'block';
        navbar.style.visibility = 'visible';
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    } else {
        console.warn('Navbar not found in the DOM');
    }
    
    // Add animation classes to elements based on viewport
    function animateElements() {
        // Apply slide-in-left to left side elements
        document.querySelectorAll('.animate-left').forEach(element => {
            if (isInViewport(element) && !element.classList.contains('slide-in-left')) {
                element.classList.add('slide-in-left');
            }
        });
        
        // Apply slide-in-right to right side elements
        document.querySelectorAll('.animate-right').forEach(element => {
            if (isInViewport(element) && !element.classList.contains('slide-in-right')) {
                element.classList.add('slide-in-right');
            }
        });
        
        // Apply fade-in to other elements
        document.querySelectorAll('.animate-fade').forEach(element => {
            if (isInViewport(element) && !element.classList.contains('fade-in')) {
                element.classList.add('fade-in');
            }
        });
    }
    
    // Helper function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.bottom >= 0
        );
    }
    
    // Run animations on page load and scroll
    animateElements();
    window.addEventListener('scroll', animateElements);
    
    // Add hover animations to cards
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('card-hover');
    });
    
    // Add hover animations to French flag elements
    document.querySelectorAll('.navbar-brand img').forEach(flag => {
        flag.classList.add('flag-wave');
    });
    
    // Add animated underline to navigation links
    document.querySelectorAll('.footer-links a').forEach(link => {
        link.classList.add('animated-link');
    });
    
    // Add float animation to CTA buttons
    document.querySelectorAll('.btn-french-primary, .btn-french-secondary').forEach(button => {
        button.classList.add('btn-float');
    });
}

/**
 * Load page-specific data
 */
function loadPageSpecificData() {
    // Check if we're on dashboard page
    const dashboardContainer = document.getElementById('dashboard-container');
    if (dashboardContainer && localStorage.getItem('token')) {
        loadDashboardData();
    }
    
    // Check if we're on courses page
    const courseListContainer = document.getElementById('course-list-container');
    if (courseListContainer) {
        loadCourseListings();
    }
}

/**
 * Handle login form submission
 * @param {Event} e - Form submit event
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const form = e.target;
    const username = document.getElementById('id_username').value;
    const password = document.getElementById('id_password').value;
    const errorContainer = document.getElementById('login-error');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...';
    
    try {
        const response = await apiRequest('/api/auth/login/', 'POST', { username, password });
        
        if (response.access) {
            // Store tokens
            localStorage.setItem('token', response.access);
            localStorage.setItem('refresh_token', response.refresh);
            
            // Redirect to dashboard
            window.location.href = '/dashboard/';
        }
    } catch (error) {
        // Display error message
        errorContainer.textContent = 'Invalid username or password';
        errorContainer.classList.remove('d-none');
        
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = 'Login';
    }
}

/**
 * Handle registration form submission
 * @param {Event} e - Form submit event
 */
async function handleRegistration(e) {
    e.preventDefault();
    
    const form = e.target;
    const errorContainer = document.getElementById('register-error');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Get form data
    const formData = {
        username: document.getElementById('id_username').value,
        email: document.getElementById('id_email').value,
        password: document.getElementById('id_password').value,
        password2: document.getElementById('id_password2')?.value,
        first_name: document.getElementById('id_first_name').value,
        last_name: document.getElementById('id_last_name').value,
        user_type: document.querySelector('input[name="user_type"]:checked')?.value
    };
    
    // Validate passwords match if confirmation field exists
    if (formData.password2 && formData.password !== formData.password2) {
        errorContainer.textContent = 'Passwords do not match';
        errorContainer.classList.remove('d-none');
        return;
    }
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...';
    
    try {
        const response = await apiRequest('/api/auth/register/', 'POST', formData);
        
        if (response.id) {
            // Redirect to login page with success message
            window.location.href = '/login/?registered=true';
        }
    } catch (error) {
        // Display error message
        errorContainer.textContent = 'Registration failed. Please try again.';
        errorContainer.classList.remove('d-none');
        
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = 'Register';
    }
}

/**
 * Handle profile update form submission
 * @param {Event} e - Form submit event
 */
async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const form = e.target;
    const errorContainer = document.getElementById('profile-error');
    const successContainer = document.getElementById('profile-success');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Get form data
    const formData = {
        first_name: document.getElementById('id_first_name').value,
        last_name: document.getElementById('id_last_name').value,
        email: document.getElementById('id_email').value,
        bio: document.getElementById('id_bio')?.value,
        phone_number: document.getElementById('id_phone_number')?.value
    };
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    
    try {
        const response = await apiRequest('/api/accounts/profile/', 'PATCH', formData);
        
        // Hide error message if visible
        errorContainer.classList.add('d-none');
        
        // Show success message
        successContainer.textContent = 'Profile updated successfully!';
        successContainer.classList.remove('d-none');
        
        // Hide success message after 3 seconds
        setTimeout(() => {
            successContainer.classList.add('d-none');
        }, 3000);
    } catch (error) {
        // Hide success message if visible
        successContainer.classList.add('d-none');
        
        // Display error message
        errorContainer.textContent = 'Failed to update profile. Please try again.';
        errorContainer.classList.remove('d-none');
    }
    
    // Reset button
    submitButton.disabled = false;
    submitButton.innerHTML = 'Save Changes';
}

/**
 * Setup course enrollment buttons
 */
function setupEnrollButtons() {
    const enrollButtons = document.querySelectorAll('.enroll-button');
    
    enrollButtons.forEach(button => {
        button.addEventListener('click', async function() {
            // Check if user is authenticated
            if (!localStorage.getItem('token')) {
                // Redirect to login page
                const courseId = this.dataset.courseId;
                window.location.href = `/login/?next=/courses/${courseId}/`;
                return;
            }
            
            const courseId = this.dataset.courseId;
            
            // Disable button and show loading state
            this.disabled = true;
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enrolling...';
            
            try {
                const response = await apiRequest('/api/enrollments/', 'POST', {
                    course: courseId
                });
                
                if (response.id) {
                    // Change button to "Enrolled"
                    this.innerHTML = '<i class="bi bi-check-circle"></i> Enrolled';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    
                    // Show success message
                    showToast('Success', 'You have successfully enrolled in this course!', 'success');
                }
            } catch (error) {
                console.error('Enrollment failed:', error);
                
                // Reset button
                this.disabled = false;
                this.innerHTML = originalText;
                
                // Show error message
                showToast('Enrollment Failed', 'Failed to enroll in this course. Please try again.', 'danger');
            }
        });
    });
}

/**
 * Load dashboard data for the current user
 */
async function loadDashboardData() {
    const loadingIndicator = document.getElementById('dashboard-loading');
    const contentContainer = document.getElementById('dashboard-content');
    
    if (loadingIndicator) loadingIndicator.classList.remove('d-none');
    if (contentContainer) contentContainer.classList.add('d-none');
    
    try {
        // Load user profile
        const userProfile = await apiRequest('/api/accounts/profile/');
        
        // Load user enrollments
        const enrollments = await apiRequest('/api/enrollments/user/');
        
        // Load upcoming sessions (if API endpoint exists)
        let upcomingSessions = [];
        try {
            upcomingSessions = await apiRequest('/api/live-sessions/upcoming/');
        } catch (err) {
            console.log('Upcoming sessions endpoint not available');
        }
        
        // Update dashboard UI with data
        updateDashboardUI(userProfile, enrollments, upcomingSessions);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        
        // Show error message
        if (contentContainer) {
            contentContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> 
                    Failed to load dashboard data. Please refresh the page to try again.
                </div>
            `;
            contentContainer.classList.remove('d-none');
        }
    } finally {
        if (loadingIndicator) loadingIndicator.classList.add('d-none');
    }
}

/**
 * Update dashboard UI with data
 * @param {Object} profile - User profile data
 * @param {Array} enrollments - Enrollment data
 * @param {Array} sessions - Upcoming sessions data
 */
function updateDashboardUI(profile, enrollments, sessions) {
    // This function will need to be customized based on your specific dashboard UI structure
    console.log('Updating dashboard with:', { profile, enrollments, sessions });
    
    // Example: Update user name in dashboard
    const userNameElement = document.getElementById('user-name');
    if (userNameElement) {
        userNameElement.textContent = profile.first_name 
            ? `${profile.first_name} ${profile.last_name}`
            : profile.username;
    }
    
    // Example: Update enrollments list
    const enrollmentsList = document.getElementById('enrollments-list');
    if (enrollmentsList) {
        if (enrollments.length === 0) {
            enrollmentsList.innerHTML = `
                <div class="text-center py-4">
                    <p>You are not enrolled in any courses yet.</p>
                    <a href="/courses/" class="btn btn-primary">Browse Courses</a>
                </div>
            `;
        } else {
            enrollmentsList.innerHTML = '';
            enrollments.forEach(enrollment => {
                const enrollmentItem = document.createElement('div');
                enrollmentItem.className = 'card mb-3';
                enrollmentItem.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">${enrollment.course.title}</h5>
                        <p class="card-text">Progress: ${enrollment.progress}%</p>
                        <div class="progress mb-3">
                            <div class="progress-bar bg-success" role="progressbar" style="width: ${enrollment.progress}%"></div>
                        </div>
                        <a href="/courses/${enrollment.course.id}/" class="btn btn-primary">Continue</a>
                    </div>
                `;
                enrollmentsList.appendChild(enrollmentItem);
            });
        }
    }
    
    // Update the UI with any other dashboard data as needed
}

/**
 * Load course listings
 */
async function loadCourseListings() {
    const courseListContainer = document.getElementById('course-list-container');
    const loadingIndicator = document.getElementById('courses-loading');
    
    if (!courseListContainer) return;
    
    if (loadingIndicator) loadingIndicator.classList.remove('d-none');
    courseListContainer.innerHTML = '';
    
    // Get filter values
    const filters = {};
    const categorySelect = document.getElementById('category-filter');
    if (categorySelect && categorySelect.value) {
        filters.category = categorySelect.value;
    }
    
    const levelSelect = document.getElementById('level-filter');
    if (levelSelect && levelSelect.value) {
        filters.level = levelSelect.value;
    }
    
    const searchInput = document.getElementById('search-input');
    if (searchInput && searchInput.value) {
        filters.search = searchInput.value;
    }
    
    // Build query string
    const queryParams = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
    });
    const queryString = queryParams.toString();
    
    try {
        // Load courses with filters
        const courses = await apiRequest(`/api/courses/${queryString ? '?' + queryString : ''}`);
        
        if (courses.length === 0) {
            courseListContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-search display-4 text-muted"></i>
                    <h4 class="mt-3">No courses found</h4>
                    <p>Try adjusting your search filters</p>
                </div>
            `;
        } else {
            courses.forEach(course => {
                const courseCard = document.createElement('div');
                courseCard.className = 'col-md-4 mb-4';
                courseCard.innerHTML = `
                    <div class="card h-100">
                        <img src="${course.image || '/static/images/course-default.jpg'}" class="card-img-top" alt="${course.title}">
                        <div class="card-body">
                            <h5 class="card-title">${course.title}</h5>
                            <p class="card-text">${course.description.substring(0, 100)}...</p>
                            <div class="d-flex justify-content-between align-items-center mt-auto">
                                <span class="badge bg-primary">${course.level}</span>
                                <strong class="text-primary">€${course.price}</strong>
                            </div>
                        </div>
                        <div class="card-footer bg-white">
                            <a href="/courses/${course.id}/" class="btn btn-outline-primary d-block">View Details</a>
                        </div>
                    </div>
                `;
                courseListContainer.appendChild(courseCard);
            });
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        courseListContainer.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> Failed to load courses. Please try again.
                </div>
            </div>
        `;
    } finally {
        if (loadingIndicator) loadingIndicator.classList.add('d-none');
    }
}

/**
 * Check URL parameters for messages
 */
function checkUrlParamsForMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Check for registration success
    if (urlParams.has('registered') && urlParams.get('registered') === 'true') {
        const alertContainer = document.createElement('div');
        alertContainer.className = 'alert alert-success alert-dismissible fade show';
        alertContainer.innerHTML = `
            <strong>Registration successful!</strong> Please login with your new account.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.prepend(alertContainer);
        }
    }
}

/**
 * Helper function for making API requests with JWT token
 * @param {string} url - API endpoint URL
 * @param {string} method - HTTP method
 * @param {Object} data - Request data
 * @returns {Promise<Object>} Response data
 */
async function apiRequest(url, method = 'GET', data = null) {
    const token = localStorage.getItem('token');
    
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        // If unauthorized and we have a refresh token, try to refresh
        if (response.status === 401 && localStorage.getItem('refresh_token')) {
            const refreshed = await refreshToken();
            if (refreshed) {
                // Retry the original request with new token
                return apiRequest(url, method, data);
            }
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw {
                status: response.status,
                message: errorData.detail || `API request failed with status: ${response.status}`,
                data: errorData
            };
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

/**
 * Refresh JWT token using refresh token
 * @returns {Promise<boolean>} Success status
 */
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
        return false;
    }
    
    try {
        const response = await fetch('/api/auth/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (!response.ok) {
            throw new Error('Token refresh failed');
        }
        
        const data = await response.json();
        
        // Store the new token in all possible storage mechanisms
        localStorage.setItem('token', data.access);
        localStorage.setItem('access_token', data.access);
        sessionStorage.setItem('access_token', data.access);
        
        // Update cookie for middleware
        document.cookie = `access_token=${data.access}; path=/; max-age=${60*60}; SameSite=Lax`;
        
        // Sync with Django session
        try {
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            await fetch('/api/auth/sync-tokens/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    access_token: data.access,
                    refresh_token: refreshToken
                }),
                credentials: 'same-origin'
            });
        } catch (syncError) {
            console.warn('Failed to sync refreshed token with session:', syncError);
        }
        
        return true;
    } catch (error) {
        console.error('Token refresh failed:', error);
        
        // Clear tokens
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('access_token');
        
        // Clear cookies
        document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
        document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
        
        return false;
    }
}

/**
 * Show toast notification
 * @param {string} title - Toast title
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, danger, warning, info)
 */
function showToast(title, message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show the toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}
