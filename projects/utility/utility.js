// ./projects/utility/utility.js
/* Main script for the Utility Scripts project page. 
   Assumes global.js is loaded first. */

document.addEventListener('DOMContentLoaded', function() {
    
    // ---- Initialize Global Features ----
    
    // Initialize Animate on Scroll
    initAOS();

    // Set the copyright year in the footer
    setCopyrightYear('copyright-year');

});