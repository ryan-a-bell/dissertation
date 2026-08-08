// docs/javascripts/theme-switcher.js

(function() {
    'use strict';
    
    // Theme configuration
    const themes = {
        'nps': {
            name: 'NPS Classic',
            icon: '🏛️',
            css: 'stylesheets/nps_custom_css.css'
        },
        'modern': {
            name: 'Modern',
            icon: '✨',
            css: 'stylesheets/modern_mkdocs_css.css'
        }
    };
    
    // Create theme switcher UI
    function createThemeSwitcher() {
        const switcher = document.createElement('div');
        switcher.className = 'theme-switcher-widget';
        switcher.innerHTML = `
            <div class="theme-switcher-header">
                <span class="theme-switcher-icon">🎨</span>
                <span class="theme-switcher-title">Theme</span>
            </div>
            <div class="theme-switcher-buttons">
                ${Object.entries(themes).map(([key, theme]) => `
                    <button class="theme-btn" data-theme="${key}" title="${theme.name}">
                        <span class="theme-icon">${theme.icon}</span>
                        <span class="theme-name">${theme.name}</span>
                    </button>
                `).join('')}
            </div>
        `;
        
        return switcher;
    }
    
    // Add CSS styles for the switcher
    function addSwitcherStyles() {
        const styles = `
            .theme-switcher-widget {
                position: fixed;
                top: 100px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
                z-index: 2000;
                font-family: inherit;
                min-width: 180px;
                transition: all 0.3s ease;
            }
            
            .theme-switcher-widget:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            }
            
            .theme-switcher-header {
                padding: 0.75rem 1rem;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 600;
                font-size: 0.875rem;
                color: #374151;
            }
            
            .theme-switcher-buttons {
                padding: 0.5rem;
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }
            
            .theme-btn {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem 1rem;
                border: none;
                background: transparent;
                border-radius: 10px;
                cursor: pointer;
                font-family: inherit;
                font-size: 0.875rem;
                font-weight: 500;
                color: #374151;
                transition: all 0.2s ease;
                width: 100%;
                text-align: left;
            }
            
            .theme-btn:hover {
                background: rgba(139, 92, 246, 0.1);
                color: #8b5cf6;
                transform: translateX(2px);
            }
            
            .theme-btn.active {
                background: linear-gradient(135deg, #8b5cf6, #7c3aed);
                color: white;
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
            }
            
            .theme-btn.active:hover {
                transform: translateX(0);
                box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
            }
            
            .theme-icon {
                font-size: 1.1rem;
                min-width: 20px;
            }
            
            .theme-name {
                flex: 1;
            }
            
            /* Mobile responsive */
            @media (max-width: 768px) {
                .theme-switcher-widget {
                    top: auto;
                    bottom: 20px;
                    right: 20px;
                    min-width: 160px;
                }
                
                .theme-btn {
                    padding: 0.5rem 0.75rem;
                    font-size: 0.8rem;
                }
                
                .theme-name {
                    display: none;
                }
                
                .theme-switcher-buttons {
                    flex-direction: row;
                }
            }
            
            /* Dark mode support */
            [data-md-color-scheme="slate"] .theme-switcher-widget {
                background: rgba(31, 41, 55, 0.95);
                border-color: rgba(255, 255, 255, 0.1);
            }
            
            [data-md-color-scheme="slate"] .theme-switcher-header,
            [data-md-color-scheme="slate"] .theme-btn {
                color: #e5e7eb;
            }
            
            [data-md-color-scheme="slate"] .theme-btn:hover {
                background: rgba(139, 92, 246, 0.2);
                color: #a78bfa;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    // Switch theme function
    function switchTheme(themeName) {
        // Remove existing custom theme
        const existingTheme = document.getElementById('custom-theme');
        if (existingTheme) {
            existingTheme.remove();
        }
        
        // Add new theme if not default
        if (themeName && themes[themeName]) {
            const link = document.createElement('link');
            link.id = 'custom-theme';
            link.rel = 'stylesheet';
            // Use absolute path from site root
            const basePath = document.querySelector('base')?.href || window.location.origin + window.location.pathname.split('/').slice(0, -1).join('/') + '/';
            const siteRoot = basePath.includes('/dissertation-docs-example/') ? 
                basePath.split('/dissertation-docs-example/')[0] + '/dissertation-docs-example/' : 
                basePath;
            link.href = siteRoot + themes[themeName].css;
            document.head.appendChild(link);
        }
        
        // Update button states
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === themeName);
        });
        
        // Save preference
        localStorage.setItem('mkdocs-theme', themeName || 'default');
        
        // Dispatch custom event for other scripts
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: themeName } 
        }));
    }
    
    // Load saved theme
    function loadSavedTheme() {
        const savedTheme = localStorage.getItem('mkdocs-theme');
        if (savedTheme && themes[savedTheme]) {
            switchTheme(savedTheme);
        } else {
            // Set default theme as active
            const defaultBtn = document.querySelector('.theme-btn[data-theme="nps"]');
            if (defaultBtn) {
                defaultBtn.classList.add('active');
            }
        }
    }
    
    // Initialize theme switcher
    function initThemeSwitcher() {
        // Add styles
        addSwitcherStyles();
        
        // Create and append switcher
        const switcher = createThemeSwitcher();
        document.body.appendChild(switcher);
        
        // Add event listeners
        switcher.addEventListener('click', (e) => {
            const btn = e.target.closest('.theme-btn');
            if (btn) {
                const themeName = btn.dataset.theme;
                switchTheme(themeName);
            }
        });
        
        // Keyboard shortcut (Ctrl+Shift+T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                const currentActive = document.querySelector('.theme-btn.active');
                const currentTheme = currentActive?.dataset.theme || 'nps';
                const themeKeys = Object.keys(themes);
                const currentIndex = themeKeys.indexOf(currentTheme);
                const nextIndex = (currentIndex + 1) % themeKeys.length;
                const nextTheme = themeKeys[nextIndex];
                switchTheme(nextTheme);
            }
        });
        
        // Load saved theme
        loadSavedTheme();
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeSwitcher);
    } else {
        initThemeSwitcher();
    }
    
    // Handle page navigation in MkDocs
    if (typeof window.location$ !== 'undefined') {
        window.location$.subscribe(() => {
            // Re-apply theme after navigation
            setTimeout(loadSavedTheme, 100);
        });
    }
    
})();
