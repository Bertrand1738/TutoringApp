/**
 * Course-specific JavaScript functionality for FrenchTutor Hub
 * Handles course listings, filtering, enrollment, and course details
 */

/**
 * Load course listings with filters
 */
async function loadCourseListings() {
    const courseListContainer = document.getElementById('course-list-container');
    const loadingIndicator = document.getElementById('courses-loading');
    const paginationContainer = document.getElementById('pagination-container');
    
    if (!courseListContainer) return;
    
    // Show loading indicator
    if (loadingIndicator) loadingIndicator.classList.remove('d-none');
    if (courseListContainer) courseListContainer.innerHTML = '';
    if (paginationContainer) paginationContainer.innerHTML = '';
    
    // Get filter values
    const filters = {};
    
    // Search input
    const searchInput = document.getElementById('search-input');
    if (searchInput && searchInput.value) {
        filters.search = searchInput.value;
    }
    
    // Category filter
    const categorySelect = document.getElementById('category-filter');
    if (categorySelect && categorySelect.value) {
        filters.category = categorySelect.value;
    }
    
    // Level filter
    const levelSelect = document.getElementById('level-filter');
    if (levelSelect && levelSelect.value) {
        filters.level = levelSelect.value;
    }
    
    // Price range filters
    const priceMin = document.getElementById('price-min');
    if (priceMin && priceMin.value) {
        filters.price_min = priceMin.value;
    }
    
    const priceMax = document.getElementById('price-max');
    if (priceMax && priceMax.value) {
        filters.price_max = priceMax.value;
    }
    
    // Sort options
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect && sortSelect.value) {
        filters.ordering = sortSelect.value;
    }
    
    // Page number (for pagination)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('page')) {
        filters.page = urlParams.get('page');
    }
    
    try {
        // Call API to get courses
        const response = await apiRequest('/api/courses/', 'GET', null, filters);
        
        // Update courses count
        updateCoursesCount(response.count || response.results.length);
        
        // Check if there are courses to display
        if (!response.results || response.results.length === 0) {
            courseListContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="display-4 text-muted">
                        <i class="bi bi-search"></i>
                    </div>
                    <h4 class="mt-3">No courses found</h4>
                    <p class="text-muted">Try adjusting your search criteria or filters</p>
                </div>
            `;
        } else {
            // Render each course card
            let coursesHTML = '';
            response.results.forEach(course => {
                coursesHTML += renderCourseCard(course);
            });
            courseListContainer.innerHTML = coursesHTML;
            
            // Setup enroll buttons
            setupEnrollButtons();
            
            // Render pagination if available
            if (response.count > response.results.length) {
                renderPagination(response);
            }
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        courseListContainer.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    Failed to load courses. Please try again later.
                </div>
            </div>
        `;
    } finally {
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.classList.add('d-none');
    }
}

/**
 * Render pagination controls
 * @param {Object} response - API response with pagination data
 */
function renderPagination(response) {
    const paginationContainer = document.getElementById('pagination-container');
    if (!paginationContainer) return;
    
    const currentPage = response.current_page || 1;
    const totalPages = response.total_pages || Math.ceil(response.count / response.results.length);
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}" ${currentPage === 1 ? 'aria-disabled="true"' : ''}>
                <i class="bi bi-chevron-left"></i> Previous
            </a>
        </li>
    `;
    
    // Page numbers
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
    
    if (endPage - startPage + 1 < maxPagesToShow) {
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }
    
    // First page if not in range
    if (startPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="1">1</a>
            </li>
        `;
        
        if (startPage > 2) {
            paginationHTML += `
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            `;
        }
    }
    
    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
    }
    
    // Last page if not in range
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            `;
        }
        
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>
            </li>
        `;
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}" ${currentPage === totalPages ? 'aria-disabled="true"' : ''}>
                Next <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;
    
    paginationContainer.innerHTML = paginationHTML;
    
    // Add event listeners to pagination links
    const paginationLinks = paginationContainer.querySelectorAll('.page-link:not([aria-disabled="true"])');
    paginationLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) {
                // Update URL with new page parameter
                const url = new URL(window.location.href);
                url.searchParams.set('page', page);
                history.pushState({}, '', url);
                
                // Load courses with new page
                loadCourseListings();
            }
        });
    });
}

/**
 * Load course detail data
 * @param {number} courseId - Course ID
 */
async function loadCourseDetail(courseId) {
    const courseDetailContainer = document.getElementById('course-detail-container');
    const loadingIndicator = document.getElementById('course-loading');
    
    if (!courseDetailContainer) return;
    
    // Show loading indicator
    if (loadingIndicator) loadingIndicator.classList.remove('d-none');
    
    try {
        // Call API to get course details
        const course = await apiRequest(`/api/courses/${courseId}/`);
        
        // Update page title
        document.title = `${course.title} - French Tutor Hub`;
        
        // Update course details in UI
        updateCourseDetailUI(course);
        
        // Check if user is enrolled
        if (localStorage.getItem('token')) {
            checkEnrollmentStatus(courseId);
        }
    } catch (error) {
        console.error('Error loading course details:', error);
        courseDetailContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                Failed to load course details. Please try again later.
            </div>
        `;
    } finally {
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.classList.add('d-none');
    }
}

/**
 * Update course detail UI
 * @param {Object} course - Course data
 */
function updateCourseDetailUI(course) {
    // This function will update the UI with course details
    // Customize based on your course detail page structure
    
    // Example: Update course title
    const courseTitleElement = document.getElementById('course-title');
    if (courseTitleElement) {
        courseTitleElement.textContent = course.title;
    }
    
    // Example: Update course description
    const courseDescriptionElement = document.getElementById('course-description');
    if (courseDescriptionElement) {
        courseDescriptionElement.innerHTML = course.description;
    }
    
    // Example: Update course price
    const coursePriceElement = document.getElementById('course-price');
    if (coursePriceElement) {
        coursePriceElement.textContent = `€${course.price}`;
    }
    
    // Example: Update course image
    const courseImageElement = document.getElementById('course-image');
    if (courseImageElement) {
        courseImageElement.src = course.image || '/static/images/course-default.jpg';
        courseImageElement.alt = course.title;
    }
    
    // Example: Update teacher info
    const teacherNameElement = document.getElementById('teacher-name');
    if (teacherNameElement) {
        teacherNameElement.textContent = course.teacher;
    }
    
    // Update other course details as needed
}

/**
 * Check if user is enrolled in a course
 * @param {number} courseId - Course ID
 */
async function checkEnrollmentStatus(courseId) {
    const enrollButton = document.querySelector(`.enroll-button[data-course-id="${courseId}"]`);
    if (!enrollButton) return;
    
    try {
        // Call API to check enrollment status
        const enrollments = await apiRequest('/api/enrollments/user/');
        
        // Check if user is enrolled in this course
        const isEnrolled = enrollments.some(enrollment => enrollment.course.id === parseInt(courseId));
        
        if (isEnrolled) {
            // Update button to show enrolled status
            enrollButton.textContent = 'Enrolled';
            enrollButton.classList.remove('btn-primary');
            enrollButton.classList.add('btn-success');
            enrollButton.disabled = true;
            
            // Also show continue learning button if available
            const continueButton = document.getElementById('continue-learning-button');
            if (continueButton) {
                continueButton.classList.remove('d-none');
            }
        }
    } catch (error) {
        console.error('Error checking enrollment status:', error);
    }
}

/**
 * Helper function to make API requests
 * @param {string} endpoint - API endpoint
 * @param {string} method - HTTP method
 * @param {Object} data - Request data
 * @param {Object} queryParams - Query parameters
 * @returns {Promise<Object>} Response data
 */
async function apiRequest(endpoint, method = 'GET', data = null, queryParams = {}) {
    // Build URL with query parameters
    let url = endpoint;
    if (Object.keys(queryParams).length > 0) {
        const queryString = new URLSearchParams();
        for (const [key, value] of Object.entries(queryParams)) {
            if (value !== null && value !== undefined && value !== '') {
                queryString.append(key, value);
            }
        }
        
        if (queryString.toString()) {
            url += `?${queryString.toString()}`;
        }
    }
    
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    // Add authorization header if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add request body for non-GET requests
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    // Make the request
    const response = await fetch(url, options);
    
    // Check if response is OK
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
            status: response.status,
            message: errorData.detail || `Request failed with status: ${response.status}`,
            data: errorData
        };
    }
    
    // Return response data
    return await response.json();
}
