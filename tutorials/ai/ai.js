// ./tutorials/ai/ai.js
/* Main script for the AI tutorial page. 
   Assumes global.js is loaded first. */

document.addEventListener('DOMContentLoaded', function() {
    
    // ---- Initialize Global Features ----
    
    // Initialize Animate on Scroll
    initAOS();

    // Set the copyright year in the footer
    setCopyrightYear('copyright-year');


    // ---- Page-Specific Logic for AI Arena ----

    const selectors = document.querySelectorAll('.ai-selector');
    const cards = document.querySelectorAll('.ai-card');

    selectors.forEach(selector => {
        selector.addEventListener('click', () => {
            const targetId = selector.dataset.target;

            // Update selectors
            selectors.forEach(s => s.classList.remove('active'));
            selector.classList.add('active');

            // Update cards
            cards.forEach(card => {
                if (card.id === targetId) {
                    card.classList.add('active');
                } else {
                    card.classList.remove('active');
                }
            });
        });
    });
});