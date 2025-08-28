// Custom JS

// Mermaid configuration and initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Mermaid with theme support
    if (typeof mermaid !== 'undefined') {
        // Get the current theme
        const getTheme = () => {
            const palette = document.querySelector('[data-md-color-scheme]');
            return palette && palette.getAttribute('data-md-color-scheme') === 'slate' ? 'dark' : 'default';
        };

        // Configure Mermaid
        mermaid.initialize({
            startOnLoad: true,
            theme: getTheme(),
            themeVariables: {
                fontFamily: 'var(--md-text-font-family)',
                fontSize: '16px'
            },
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            },
            gantt: {
                useMaxWidth: true,
                leftPadding: 75,
                gridLineStartPadding: 35
            },
            mindmap: {
                useMaxWidth: true,
                padding: 10
            }
        });

        // Re-initialize Mermaid when theme changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
                    mermaid.initialize({
                        theme: getTheme(),
                        startOnLoad: true
                    });
                    // Re-render all mermaid diagrams
                    document.querySelectorAll('.mermaid').forEach(function(element) {
                        element.removeAttribute('data-processed');
                    });
                    mermaid.init();
                }
            });
        });

        // Observe theme changes
        const target = document.querySelector('[data-md-color-scheme]');
        if (target) {
            observer.observe(target, { attributes: true });
        }
    }
});
