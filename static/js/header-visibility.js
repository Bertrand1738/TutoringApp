/**
 * Simple Header Visibility Script
 * This script ensures the header is always visible and works properly
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get header element
    const header = document.querySelector('header');
    
    // Force header visibility
    if (header) {
        // Force visibility with !important style
        header.setAttribute('style', 'display: block !important; visibility: visible !important; z-index: 9999 !important');
        
        // Also ensure the login bar is visible
        const loginBar = document.querySelector('.login-bar');
        if (loginBar) {
            loginBar.setAttribute('style', 'display: block !important; visibility: visible !important');
        }
    }
    
    // Add a debug button to toggle header visibility (only for development)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const debugButton = document.createElement('button');
        debugButton.textContent = 'Toggle Header';
        debugButton.style.position = 'fixed';
        debugButton.style.bottom = '10px';
        debugButton.style.right = '10px';
        debugButton.style.zIndex = '10000';
        debugButton.style.background = '#ED2939';
        debugButton.style.color = 'white';
        debugButton.style.padding = '8px 16px';
        debugButton.style.borderRadius = '4px';
        debugButton.style.border = 'none';
        debugButton.style.cursor = 'pointer';
        
        debugButton.addEventListener('click', function() {
            if (header.style.display === 'none') {
                header.style.display = 'block';
            } else {
                header.style.display = 'none';
            }
        });
        
        document.body.appendChild(debugButton);
    }
});
