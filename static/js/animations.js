/**
 * animations.js - Implements scroll-based animations for French Tutor Hub
 * This script adds scroll-triggered animations to elements with specific classes
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeScrollAnimations();
    initializeAnimationObserver();
});

/**
 * Initialize basic animations that don't require scroll observation
 */
function initializeScrollAnimations() {
    // Apply staggered animations to lists and grids
    applyStaggeredAnimations();
    
    // Add float animations to specific elements
    document.querySelectorAll('.flag-icon, .hero-badge, .testimonial-quote, .feature-icon').forEach((element, index) => {
        // Alternate between slow and fast float animations
        if (index % 2 === 0) {
            element.classList.add('float-slow');
        } else {
            element.classList.add('float-fast');
        }
    });
    
    // Add pulse effect to CTA buttons
    document.querySelectorAll('.btn-cta, .btn-french-primary').forEach(button => {
        button.classList.add('pulse-slow');
    });
    
    // Apply tricolor transition to decorative elements
    document.querySelectorAll('.french-tricolor-border, .section-divider').forEach(element => {
        element.classList.add('tricolor-transition');
    });
}

/**
 * Initialize the Intersection Observer for scroll-reveal animations
 */
function initializeAnimationObserver() {
    // Create options for the observer
    const observerOptions = {
        root: null, // Use viewport as root
        threshold: 0.1, // Trigger when at least 10% of the element is visible
        rootMargin: '0px 0px -50px 0px' // Trigger slightly before elements come into view
    };
    
    // Create an intersection observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add active class to trigger animations
                entry.target.classList.add('active');
                
                // Unobserve after animation is triggered
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all elements with reveal classes
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-bottom').forEach(element => {
        observer.observe(element);
    });
}

/**
 * Apply staggered animation delays to lists and grid items
 */
function applyStaggeredAnimations() {
    // Add staggered animations to feature items
    document.querySelectorAll('.features-section .col-md-4, .feature-item').forEach((item, index) => {
        item.classList.add('reveal-bottom');
        item.style.transitionDelay = `${0.1 * index}s`;
    });
    
    // Add staggered animations to course cards
    document.querySelectorAll('.course-card').forEach((card, index) => {
        card.classList.add('reveal');
        card.style.transitionDelay = `${0.1 * index}s`;
    });
    
    // Add staggered animations to testimonial items
    document.querySelectorAll('.testimonial-item').forEach((testimonial, index) => {
        testimonial.classList.add('reveal');
        testimonial.style.transitionDelay = `${0.15 * index}s`;
    });
    
    // Add staggered animations to timeline items
    document.querySelectorAll('.timeline-item').forEach((item, index) => {
        if (index % 2 === 0) {
            item.classList.add('reveal-left');
        } else {
            item.classList.add('reveal-right');
        }
        item.style.transitionDelay = `${0.1 * index}s`;
    });
    
    // Add staggered animations to FAQ items
    document.querySelectorAll('.faq-item, .accordion-item').forEach((item, index) => {
        item.classList.add('reveal-bottom');
        item.style.transitionDelay = `${0.1 * index}s`;
    });
}

/**
 * Add a parallax effect to background elements
 * @param {string} selector - CSS selector for parallax elements
 */
function initializeParallaxEffect(selector = '.parallax-bg') {
    const parallaxElements = document.querySelectorAll(selector);
    
    if (parallaxElements.length > 0) {
        window.addEventListener('scroll', () => {
            const scrollY = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.speed || 0.5;
                const yPos = -(scrollY * speed);
                element.style.transform = `translate3d(0px, ${yPos}px, 0px)`;
            });
        });
    }
}

// Add parallax effects if there are elements with the parallax-bg class
initializeParallaxEffect();

/**
 * Creates a typing animation for text elements
 * @param {string} selector - CSS selector for elements to animate
 */
function createTypingAnimation(selector = '.typing-text') {
    const elements = document.querySelectorAll(selector);
    
    elements.forEach(element => {
        const text = element.innerText;
        element.innerText = '';
        element.style.opacity = '1';
        
        let i = 0;
        const speed = element.dataset.speed || 50; // milliseconds per character
        
        function typeWriter() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, speed);
            }
        }
        
        // Use Intersection Observer to start typing when element comes into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    typeWriter();
                    observer.unobserve(element);
                }
            });
        }, { threshold: 0.3 });
        
        observer.observe(element);
    });
}

// Initialize typing animations
createTypingAnimation();

/**
 * Creates a counter animation for number elements
 * @param {string} selector - CSS selector for number counter elements
 */
function createCounterAnimation(selector = '.counter') {
    const counters = document.querySelectorAll(selector);
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = parseInt(counter.getAttribute('data-duration') || '2000');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    let startTime;
                    let startValue = 0;
                    
                    function updateCounter(timestamp) {
                        if (!startTime) startTime = timestamp;
                        const elapsed = timestamp - startTime;
                        
                        if (elapsed < duration) {
                            // Easing function for smooth counting
                            const progress = elapsed / duration;
                            const easedProgress = progress < 0.5
                                ? 2 * progress * progress
                                : 1 - Math.pow(-2 * progress + 2, 2) / 2; // easeInOutQuad
                                
                            const value = Math.floor(easedProgress * target);
                            counter.innerText = value;
                            requestAnimationFrame(updateCounter);
                        } else {
                            counter.innerText = target;
                        }
                    }
                    
                    requestAnimationFrame(updateCounter);
                    observer.unobserve(counter);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(counter);
    });
}

// Initialize counter animations
createCounterAnimation();
