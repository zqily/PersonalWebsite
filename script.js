// ./script.js
/* ---- script.js ---- */
/* Main script for the zqil homepage. 
   Initializes global features and runs page-specific logic.
   Assumes global.js is loaded first. */

document.addEventListener('DOMContentLoaded', function() {
    
    // ---- 1. Initialize Global Features ----
    
    // Initialize Animate on Scroll
    initAOS();

    // Set the copyright year in the footer
    setCopyrightYear('copyright-year');
    
    // Define particle configuration and initialize the background
    const particleConfig = {
        fpsLimit: 60,
        particles: {
            number: { value: 60, density: { enable: true, value_area: 800 } },
            color: { value: "#00F5D4" },
            shape: { type: "circle" },
            opacity: {
                value: 0.4,
                random: true,
                anim: { enable: true, speed: 0.5, opacity_min: 0.1, sync: false },
            },
            size: {
                value: 2.5,
                random: true,
                anim: { enable: false },
            },
            line_linked: { enable: false },
            move: {
                enable: true,
                speed: 0.3,
                direction: "none",
                random: true,
                straight: false,
                out_mode: "out",
                bounce: false,
            },
        },
        interactivity: {
            detect_on: "canvas",
            events: {
                onhover: { enable: false },
                onclick: { enable: false },
                resize: true,
            },
        },
        retina_detect: true,
    };
    initParticleBackground("particles-js", particleConfig);


    // ---- 2. Page-Specific Logic ----

    // YouTube Subscriber Count Fetch
    const apiKey = 'AIzaSyBBmkZoWC3BQ9DJwRmQfXlZdh3vDwWhFc0'; // Note: Exposing API keys client-side is a security risk.
    const channelId = 'UCLHNTGh4BmCHOgZ2MAZIqmw';
    const subscriberCountElement = document.getElementById('subscriber-count');

    function formatSubscriberCount(count) {
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + 'M';
        } else if (count >= 1000) {
            return (count / 1000).toFixed(0) + 'K';
        }
        return count;
    }

    fetch(`https://www.googleapis.com/youtube/v3/channels?part=statistics&id=${channelId}&key=${apiKey}`)
        .then(response => response.json())
        .then(data => {
            if (subscriberCountElement && data.items && data.items.length > 0) {
                const subscriberCount = data.items[0].statistics.subscriberCount;
                subscriberCountElement.textContent = formatSubscriberCount(subscriberCount);
            }
        })
        .catch(error => {
            console.error('Error fetching subscriber count:', error);
            // If the API fails, the default value '103K' from the HTML will remain.
        });

});