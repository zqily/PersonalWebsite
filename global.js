// ./global.js
/* ---- global.js ---- */
/* Defines reusable functions for initializing common libraries and features. */

/**
 * Initializes the Animate on Scroll (AOS) library with default settings.
 */
function initAOS() {
    AOS.init({
        duration: 800, // animation duration in ms
        once: true,    // whether animation should happen only once
        offset: 50,    // offset (in px) from the original trigger point
    });
}

/**
 * Initializes a tsParticles instance on a given element ID with a provided configuration.
 * @param {string} elementId The ID of the element to attach the particles to.
 * @param {object} config The tsParticles configuration object.
 */
function initParticleBackground(elementId, config) {
    if (document.getElementById(elementId)) {
        tsParticles.load(elementId, config);
    }
}

/**
 * Sets the text content of an element to the current year.
 * @param {string} elementId The ID of the element to update.
 */
function setCopyrightYear(elementId) {
    const yearSpan = document.getElementById(elementId);
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
}