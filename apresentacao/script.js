/**
 * ========================================
 * THREAT HUNTING PRESENTATION SCRIPTS
 * ========================================
 */

/**
 * Presentation Manager Class
 * Handles slide navigation and overall presentation control
 */
class PresentationManager {
    constructor(slidesConfig) {
        this.slidesConfig = slidesConfig;
        this.slidesContainer = document.querySelector('.slides-container');
        this.currentSlide = 0;
        this.slides = [];
        this.totalSlides = 0;
        this.progressBar = document.getElementById('progress');
        this.currentSlideElement = document.getElementById('current-slide');
        this.totalSlidesElement = document.getElementById('total-slides');

        this.init();
    }

    init() {
        this.createSlides();
        this.totalSlides = this.slides.length;
        this.updateTotalSlides();
        this.updateSlide();
        this.bindEvents();
    }

    createSlides() {
        this.slidesConfig.forEach(config => {
            const slideElement = this.createSlideElement(config);
            this.slidesContainer.appendChild(slideElement);
            this.slides.push(slideElement);
        });
    }

    createSlideElement(config) {
        const slide = document.createElement('div');
        slide.className = 'slide';
        const slideContent = document.createElement('div');
        slideContent.className = 'slide-content';

        switch (config.type) {
            case 'title':
                slideContent.innerHTML = `
                    <div class="ai-visual">
                        <div class="ai-core"></div>
                        <div class="orbit"></div>
                    </div>
                    <h1>${config.title}</h1>
                    <p class="subtitle">${config.subtitle}</p>
                    <div class="glass-card" style="max-width: 600px; margin: 2rem auto;">
                        <p style="font-size: 1.2rem; margin-bottom: 1rem;">${config.description}</p>
                        <p style="color: var(--text-secondary);">${config.author}</p>
                    </div>
                `;
                break;
            case 'agenda':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div id="presentation-roulette"></div>
                `;
                break;
            case 'theme':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="glass-card" style="margin-top: 2rem;">
                        <p style="font-size: 1.3rem; line-height: 1.6; font-style: italic; text-align: center;">
                            ${config.main_quote}
                        </p>
                    </div>
                    <div class="two-column">
                        ${config.columns.map(col => `
                            <div>
                                <div class="glass-card">
                                    <h3 style="color: var(--accent); margin-bottom: 1.5rem;">${col.title}</h3>
                                    <ul class="feature-list">
                                        ${col.features.map(feat => `<li>${feat}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            case 'problem':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="two-column">
                        ${config.columns.map(col => {
                            if (col.type === 'threat-visual') {
                                return '<div><div class="threat-visual"><div class="threat-circle"></div><div class="threat-circle"></div><div class="threat-circle"></div></div></div>';
                            }
                            return `
                                <div>
                                    <div class="glass-card">
                                        <h3 class="danger-text">${col.title}</h3>
                                        <ul class="feature-list">
                                            ${col.features.map(feat => `<li>${feat}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
                break;
            case 'related_works':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="two-column" style="gap: 1.5rem;">
                        ${config.columns.map(col => `
                            <div>
                                ${col.cards.map(card => `
                                    <div class="glass-card" style="margin-bottom: 1.5rem;">
                                        <div class="icon" style="font-size: 2rem; margin-bottom: 1rem;">${card.icon}</div>
                                        <h3 style="color: var(--accent); margin-bottom: 1rem;">${card.title}</h3>
                                        <p style="font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.4;">${card.correlation}</p>
                                        <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.3;">${card.reference}</div>
                                    </div>
                                `).join('')}
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            case 'general_objective':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="glass-card" style="max-width: 800px; margin: 2rem auto;">
                        <h3 style="font-size: 2rem; margin-bottom: 1.5rem;">${config.main_goal}</h3>
                        <p style="font-size: 1.2rem; line-height: 1.8;">${config.description}</p>
                    </div>
                    <div class="ai-visual" style="margin-top: 2rem;">
                        <div class="ai-core"></div>
                        <div class="orbit"></div>
                    </div>
                `;
                break;
            case 'specific_objectives':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div id="objectives-roulette"></div>
                `;
                break;
            case 'hypothesis':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="glass-card" style="max-width: 900px; margin: 2rem auto; padding: 3rem;">
                        <h3 style="font-size: 1.8rem; margin-bottom: 2rem; color: var(--accent);">${config.statement}</h3>
                    </div>
                `;
                break;
            case 'hypothesis_justification':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="two-column">
                        ${config.columns.map(col => `
                            <div>
                                <div class="glass-card">
                                    <h3>${col.title}</h3>
                                    <ul class="feature-list">
                                        ${col.features.map(feat => `<li>${feat}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            case 'methodology':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="glass-card" style="margin-bottom: 1rem;">
                        <h3>${config.subtitle}</h3>
                    </div>
                    <div class="method-grid">
                        ${config.phases.map(phase => `
                            <div class="method-card">
                                <div class="icon">${phase.icon}</div>
                                <h4>${phase.title}</h4>
                                <p>${phase.description}</p>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            case 'expected_results':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div class="two-column">
                        ${config.columns.map(col => `
                            <div>
                                <div class="glass-card">
                                    <h3 class="highlight">${col.title}</h3>
                                    <ul class="feature-list">
                                        ${col.features.map(feat => `<li>${feat}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            case 'limitations':
                slideContent.innerHTML = `
                    <h2>${config.title}</h2>
                    <div style="max-width: 800px; margin: 0 auto;">
                        ${config.items.map(item => `
                            <div class="limitation-item">
                                <h3>${item.title}</h3>
                                <p>${item.description}</p>
                            </div>
                        `).join('')}
                    </div>
                    <div class="glass-card" style="margin-top: 2rem;">
                        <p style="font-style: italic;">${config.conclusion}</p>
                    </div>
                `;
                break;
        }

        slide.appendChild(slideContent);
        return slide;
    }

    updateTotalSlides() {
        if (this.totalSlidesElement) {
            this.totalSlidesElement.textContent = this.totalSlides;
        }
    }

    updateSlide() {
        // Update slide visibility
        this.slides.forEach((slide, index) => {
            slide.classList.remove('active', 'prev');
            if (index === this.currentSlide) {
                slide.classList.add('active');
            } else if (index < this.currentSlide) {
                slide.classList.add('prev');
            }
        });

        // Update slide indicator
        if (this.currentSlideElement) {
            this.currentSlideElement.textContent = this.currentSlide + 1;
        }

        // Update progress bar
        if (this.progressBar) {
            const progressPercentage = ((this.currentSlide + 1) / this.totalSlides * 100);
            this.progressBar.style.width = progressPercentage + '%';
        }
    }

    changeSlide(direction) {
        this.currentSlide += direction;

        // Handle wrap-around navigation
        if (this.currentSlide < 0) {
            this.currentSlide = this.totalSlides - 1;
        }
        if (this.currentSlide >= this.totalSlides) {
            this.currentSlide = 0;
        }

        this.updateSlide();
    }

    goToSlide(slideIndex) {
        if (slideIndex >= 0 && slideIndex < this.totalSlides) {
            this.currentSlide = slideIndex;
            this.updateSlide();
        }
    }

    bindEvents() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                    this.changeSlide(-1);
                    break;
                case 'ArrowRight':
                    this.changeSlide(1);
                    break;
                case 'Home':
                    this.goToSlide(0);
                    break;
                case 'End':
                    this.goToSlide(this.totalSlides - 1);
                    break;
                case 'Escape':
                    // Could be used for fullscreen toggle or exit
                    break;
            }
        });

        // Touch/swipe support
        this.bindTouchEvents();
    }

    bindTouchEvents() {
        let touchStartX = 0;
        let touchEndX = 0;
        const minSwipeDistance = 50;

        document.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe(touchStartX, touchEndX, minSwipeDistance);
        }, { passive: true });
    }

    handleSwipe(startX, endX, minDistance) {
        const deltaX = endX - startX;

        if (Math.abs(deltaX) > minDistance) {
            if (deltaX < 0) {
                // Swipe left - next slide
                this.changeSlide(1);
            } else {
                // Swipe right - previous slide
                this.changeSlide(-1);
            }
        }
    }
}

/**
 * Navigation Component
 * Handles navigation button interactions
 */
class NavigationComponent {
    constructor(presentationManager) {
        this.presentationManager = presentationManager;
        this.init();
    }

    init() {
        this.bindNavigationButtons();
    }

    bindNavigationButtons() {
        // Create navigation buttons if they don't exist
        this.createNavigationButtons();

        // Bind click events
        const prevBtn = document.querySelector('.nav-btn[data-action="prev"]');
        const nextBtn = document.querySelector('.nav-btn[data-action="next"]');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                this.presentationManager.changeSlide(-1);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                this.presentationManager.changeSlide(1);
            });
        }
    }

    createNavigationButtons() {
        const existingNavButtons = document.querySelector('.nav-buttons');
        if (!existingNavButtons) {
            const navContainer = document.createElement('div');
            navContainer.className = 'nav-buttons';

            const prevButton = document.createElement('button');
            prevButton.className = 'nav-btn';
            prevButton.setAttribute('data-action', 'prev');
            prevButton.textContent = '← Anterior';

            const nextButton = document.createElement('button');
            nextButton.className = 'nav-btn';
            nextButton.setAttribute('data-action', 'next');
            nextButton.textContent = 'Próximo →';

            navContainer.appendChild(prevButton);
            navContainer.appendChild(nextButton);
            document.body.appendChild(navContainer);
        }
    }
}

/**
 * Interactive Cards Component
 * Handles flip card interactions and animations
 */
class InteractiveCardsComponent {
    constructor() {
        this.flipCards = document.querySelectorAll('.flip-card');
        this.init();
    }

    init() {
        this.bindFlipCardEvents();
        this.bindMethodCardHovers();
    }

    bindFlipCardEvents() {
        this.flipCards.forEach(card => {
            card.addEventListener('click', () => {
                card.classList.toggle('flipped');
            });

            // Add keyboard support for accessibility
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.classList.toggle('flipped');
                }
            });

            // Make it focusable for keyboard navigation
            card.setAttribute('tabindex', '0');
        });
    }

    bindMethodCardHovers() {
        const methodCards = document.querySelectorAll('.method-card');

        methodCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.addCardHoverEffect(card);
            });

            card.addEventListener('mouseleave', () => {
                this.removeCardHoverEffect(card);
            });
        });
    }

    addCardHoverEffect(card) {
        // Additional hover effects could be added here
        card.style.transform = 'translateY(-5px) scale(1.02)';
    }

    removeCardHoverEffect(card) {
        // Reset hover effects
        setTimeout(() => {
            if (!card.matches(':hover')) {
                card.style.transform = '';
            }
        }, 100);
    }
}

/**
 * Animation Controller
 * Manages various animations and visual effects
 */
class AnimationController {
    constructor() {
        this.init();
    }

    init() {
        this.initializeAnimations();
        this.bindVisibilityAPI();
    }

    initializeAnimations() {
        // Initialize any animations that need setup
        this.setupIntersectionObserver();
    }

    setupIntersectionObserver() {
        // Observer for animating elements when they come into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1
        });

        // Observe elements that should animate when visible
        const animatedElements = document.querySelectorAll('.feature-list li, .method-card, .glass-card');
        animatedElements.forEach(el => observer.observe(el));
    }

    bindVisibilityAPI() {
        // Pause animations when tab is not visible
        document.addEventListener('visibilitychange', () => {
            const animations = document.querySelectorAll('[style*="animation"]');

            if (document.hidden) {
                animations.forEach(el => {
                    el.style.animationPlayState = 'paused';
                });
            } else {
                animations.forEach(el => {
                    el.style.animationPlayState = 'running';
                });
            }
        });
    }
}

/**
 * Accessibility Manager
 * Handles accessibility features and keyboard navigation
 */
class AccessibilityManager {
    constructor(presentationManager) {
        this.presentationManager = presentationManager;
        this.init();
    }

    init() {
        this.setupAriaLabels();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
    }

    setupAriaLabels() {
        // Add ARIA labels to navigation elements
        const slides = document.querySelectorAll('.slide');
        slides.forEach((slide, index) => {
            slide.setAttribute('aria-label', `Slide ${index + 1} of ${slides.length}`);
            slide.setAttribute('role', 'region');
        });

        // Add ARIA labels to navigation buttons
        const prevBtn = document.querySelector('.nav-btn[data-action="prev"]');
        const nextBtn = document.querySelector('.nav-btn[data-action="next"]');

        if (prevBtn) {
            prevBtn.setAttribute('aria-label', 'Previous slide');
        }
        if (nextBtn) {
            nextBtn.setAttribute('aria-label', 'Next slide');
        }
    }

    setupFocusManagement() {
        // Ensure proper focus management during slide transitions
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.manageFocus(e);
            }
        });
    }

    manageFocus(event) {
        const currentSlide = document.querySelector('.slide.active');
        const focusableElements = currentSlide?.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements && focusableElements.length > 0) {
            // Trap focus within current slide
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (event.shiftKey && document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
            } else if (!event.shiftKey && document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
            }
        }
    }

    setupScreenReaderSupport() {
        // Announce slide changes to screen readers
        const slideIndicator = document.getElementById('current-slide');
        if (slideIndicator) {
            slideIndicator.setAttribute('aria-live', 'polite');
            slideIndicator.setAttribute('aria-atomic', 'true');
        }
    }
}

/**
 * Performance Manager
 * Optimizes performance and handles resource management
 */
class PerformanceManager {
    constructor() {
        this.init();
    }

    init() {
        this.optimizeAnimations();
        this.setupLazyLoading();
    }

    optimizeAnimations() {
        // Reduce animations for users who prefer reduced motion
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.disableAnimations();
        }
    }

    disableAnimations() {
        const style = document.createElement('style');
        style.textContent = `
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        `;
        document.head.appendChild(style);
    }

    setupLazyLoading() {
        // Future: implement lazy loading for heavy content
        // This could be useful if adding images or videos
    }
}

/**
 * Utility Functions
 */
const Utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function () {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

/**
 * Initialize Application
 * Main initialization function that sets up all components
 */
function initializePresentation() {
    // Check if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startApplication);
    } else {
        startApplication();
    }
}

/**
 * Initialize Roulettes
 * Sets up interactive roulette components
 */
function initializeRoulettes() {
    // Objectives roulette data
    const objectivesItems = [
        {
            icon: '🎯',
            title: 'Modelagem de Agentes',
            description: 'Definir arquitetura e estruturas de governança para a orquestração de agentes de IA especializados em detecção de spywares'
        },
        {
            icon: '🛡️',
            title: 'Modelar Ambiente',
            description: 'Criar ambiente de execução controlado e replicável para testes e validação dos agentes de IA em cenários realísticos'
        },
        {
            icon: '🔬',
            title: 'Detecção Inteligente',
            description: 'Desenvolver e aplicar processo automatizado de identificação de spywares através de análise comportamental distribuída'
        }
    ];

    // Initialize objectives roulette if container exists
    const objectivesContainer = document.getElementById('objectives-roulette');
    if (objectivesContainer) {
        window.objectivesRoulette = createRoulette(objectivesItems, 'objectives-roulette');
    }

    // Initialize presentation roulette if container exists (from components.js agendaItems)
    const presentationContainer = document.getElementById('presentation-roulette');
    if (presentationContainer && typeof agendaItems !== 'undefined') {
        window.presentationRoulette = createRoulette(agendaItems, 'presentation-roulette');
    }
}

function startApplication() {
    try {
        // Initialize core presentation manager
        const presentationManager = new PresentationManager(slidesConfig);

        // Initialize components
        new NavigationComponent(presentationManager);
        new InteractiveCardsComponent();
        new AnimationController();
        new AccessibilityManager(presentationManager);
        new PerformanceManager();

        // Initialize roulettes
        initializeRoulettes();

        // Expose presentation manager globally for debugging
        window.presentationManager = presentationManager;

        console.log('🚀 Threat Hunting Presentation initialized successfully!');

    } catch (error) {
        console.error('❌ Error initializing presentation:', error);
    }
}


// Global functions for backward compatibility (if needed by HTML)
function changeSlide(direction) {
    if (window.presentationManager) {
        window.presentationManager.changeSlide(direction);
    }
}

// Start the application
initializePresentation(); 