/**
 * Home page specific JavaScript functionality
 * Loads featured courses and other dynamic content
 */

/**
 * Load featured courses from API
 */
async function loadFeaturedCourses() {
    const featuredCoursesContainer = document.getElementById('featured-courses-container');
    const loadingIndicator = document.getElementById('featured-courses-loading');
    const errorElement = document.getElementById('featured-courses-error');
    
    if (!featuredCoursesContainer) return;
    
    // Show loading indicator
    if (loadingIndicator) loadingIndicator.classList.remove('d-none');
    if (errorElement) errorElement.classList.add('d-none');
    
    try {
        console.log('Attempting to load featured courses...');
        
        // Try to call API or use fallback data if API fails
        let courses;
        try {
            // Try direct fetch first for simplicity
            console.log('Attempting to fetch courses from API...');
            const response = await fetch('/api/courses/?featured=true&limit=3');
            console.log('API response status:', response.status);
            if (response.ok) {
                const data = await response.json();
                console.log('Direct fetch response data:', data);
                // Convert array response to expected format with results property
                courses = { results: Array.isArray(data) ? data : [data] };
                console.log('Processed courses data:', courses);
            } else {
                console.error('API error:', response.status);
                throw new Error(`API returned ${response.status}`);
            }
        } catch (apiError) {
            console.warn('API call failed, using fallback data', apiError);
            // Fallback data for demonstration
            courses = {
                results: [
                    {
                        id: 1,
                        title: 'French for Beginners',
                        description: 'Start your French journey with this comprehensive course designed for absolute beginners.',
                        price: 99.99,
                        level: 'Beginner',
                        category: 'General',
                        teacher: {
                            full_name: 'Marie Dupont',
                            username: 'marie.teacher'
                        },
                        image: '/static/images/course-default.jpg'
                    },
                    {
                        id: 2,
                        title: 'Business French',
                        description: 'Master professional French vocabulary and expressions for business environments.',
                        price: 149.99,
                        level: 'Intermediate',
                        category: 'Business',
                        teacher: {
                            full_name: 'Jean Leclerc',
                            username: 'jean.teacher'
                        },
                        image: '/static/images/course-default.jpg'
                    },
                    {
                        id: 3,
                        title: 'Advanced French Grammar',
                        description: 'Dive deep into complex French grammar concepts and take your fluency to the next level.',
                        price: 129.99,
                        level: 'Advanced',
                        category: 'Grammar',
                        teacher: {
                            full_name: 'Sophie Martin',
                            username: 'sophie.teacher'
                        },
                        image: '/static/images/course-default.jpg'
                    }
                ]
            };
        }
        
        // Check if there are courses to display
        if (!courses.results || courses.results.length === 0) {
            featuredCoursesContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        No featured courses available at the moment.
                    </div>
                </div>
            `;
        } else {
            // Render each course card
            console.log('Rendering course cards, count:', courses.results.length);
            let coursesHTML = '';
            courses.results.forEach(course => {
                console.log('Processing course:', course.title);
                const cardHTML = renderFeaturedCourseCard(course);
                console.log('Card HTML length:', cardHTML.length);
                coursesHTML += cardHTML;
            });
            console.log('Total HTML length:', coursesHTML.length);
            featuredCoursesContainer.innerHTML = coursesHTML;
        }
    } catch (error) {
        console.error('Error loading featured courses:', error);
        if (errorElement) {
            errorElement.classList.remove('d-none');
            const errorMessage = document.getElementById('featured-courses-error-message');
            if (errorMessage) {
                errorMessage.textContent = `Failed to load featured courses: ${error.message || 'Unknown error'}`;
            }
        } else {
            featuredCoursesContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        Failed to load featured courses. Please try again later.
                    </div>
                </div>
            `;
        }
    } finally {
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.classList.add('d-none');
    }
}

/**
 * Render featured course card HTML
 * @param {Object} course - Course data
 * @returns {string} HTML for course card
 */
function renderFeaturedCourseCard(course) {
    // Format the price
    const formattedPrice = new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(course.price);
    
    // Create teacher name display
    let teacherName = 'Unknown Teacher';
    if (course.teacher) {
        if (typeof course.teacher === 'object') {
            teacherName = course.teacher.full_name || course.teacher.username || 'Unknown Teacher';
        } else if (course.teacher_name && course.teacher_name !== "" && course.teacher_name !== "admin") {
            teacherName = course.teacher_name;
        } else {
            teacherName = `French Language Expert`;
        }
    }
    
    // Handle category display
    let categoryText = 'General';
    if (course.category) {
        if (typeof course.category === 'object') {
            categoryText = course.category.name || 'General';
        } else {
            categoryText = course.category;
        }
    }
    
    return `
        <div class="col-md-4">
            <div class="card course-card shadow-sm h-100">
                <span class="badge bg-primary featured-badge">Featured</span>
                <img src="${course.image || '/static/images/course-default.jpg'}" 
                     class="card-img-top" alt="${course.title}" 
                     style="height: 180px; object-fit: cover;">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${course.title}</h5>
                    <p class="text-muted">
                        <i class="bi bi-person-circle me-1"></i> ${teacherName}
                    </p>
                    <div class="mb-2">
                        <span class="badge rounded-pill bg-light text-dark">
                            ${course.level || 'All levels'}
                        </span>
                        <span class="badge rounded-pill bg-light text-dark">
                            ${categoryText}
                        </span>
                    </div>
                    <p class="card-text flex-grow-1">${course.description.length > 100 ? 
                        course.description.substring(0, 100) + '...' : 
                        course.description}
                    </p>
                    <div class="d-flex justify-content-between align-items-center mt-auto">
                        <span class="h5 mb-0">${formattedPrice}</span>
                        <a href="/courses/${course.id}/" class="btn btn-sm btn-outline-primary">
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
}
