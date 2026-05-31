/**
 * ========================================
 * USAGE EXAMPLES FOR COMPONENT SYSTEM
 * ========================================
 * 
 * This file demonstrates how to use the modular component system
 * to create new slides and elements programmatically.
 */

// Example 1: Creating a new slide using ComponentFactory
function createExampleSlide() {
    const exampleSlide = ComponentFactory.createSlide({
        className: 'example-slide',
        content: `
            <h2>Slide Criado Dinamicamente! 🚀</h2>
            <div class="glass-card">
                <p>Este slide foi criado usando o sistema de componentes!</p>
            </div>
        `
    });

    // Add to presentation
    document.querySelector('.slides-container').appendChild(exampleSlide);
    console.log('✅ New slide created successfully!');
}

// Example 2: Creating cards programmatically
function createMethodCards() {
    const methodsData = [
        {
            icon: '🔥',
            title: 'Detecção em Tempo Real',
            description: 'Monitoramento contínuo de atividades suspeitas'
        },
        {
            icon: '🧠',
            title: 'Machine Learning',
            description: 'Algoritmos adaptativos para novos padrões'
        },
        {
            icon: '🛡️',
            title: 'Proteção Multicamada',
            description: 'Defesa em profundidade contra ameaças'
        },
        {
            icon: '📊',
            title: 'Analytics Avançado',
            description: 'Análise preditiva de comportamentos'
        }
    ];

    const grid = ComponentFactory.createMethodGrid(methodsData);

    // You can then append this grid to any slide
    return grid;
}

// Example 3: Creating a complete slide using templates
function createNewResearchSlide() {
    const researchData = {
        title: 'Pesquisas Futuras',
        objectives: [
            {
                icon: '🔬',
                title: 'IA Explicável',
                description: 'Desenvolvimento de modelos interpretáveis para decisões de segurança'
            },
            {
                icon: '🌐',
                title: 'Federação de Dados',
                description: 'Aprendizado federado para melhor privacidade'
            },
            {
                icon: '⚡',
                title: 'Edge Computing',
                description: 'Processamento local para redução de latência'
            },
            {
                icon: '🔮',
                title: 'Predição de Ameaças',
                description: 'Antecipação de novos tipos de ataques'
            }
        ]
    };

    return SlideTemplates.createObjectivesSlide(researchData);
}

// Example 3a: Creating an agenda slide using templates
function createCustomAgendaSlide() {
    const agendaData = {
        title: 'Minha Agenda Personalizada',
        subtitle: 'Tópicos da Apresentação',
        agendaItems: [
            {
                icon: '🚀',
                title: '1. Introdução',
                description: 'Visão geral do projeto'
            },
            {
                icon: '📊',
                title: '2. Análise de Dados',
                description: 'Estatísticas e métricas importantes'
            },
            {
                icon: '🎯',
                title: '3. Objetivos',
                description: 'Metas e resultados esperados'
            },
            {
                icon: '🔬',
                title: '4. Metodologia',
                description: 'Abordagem técnica utilizada'
            }
        ]
    };

    return SlideTemplates.createAgendaSlide(agendaData);
}

// Example 3b: Creating a theme presentation slide
function createCustomThemeSlide() {
    const themeData = {
        title: 'Meu Tema de Pesquisa',
        leftTitle: 'Desafios Identificados',
        leftItems: [
            '🔥 <strong>Escalabilidade:</strong> Sistemas que crescem com a demanda',
            '⚡ <strong>Performance:</strong> Resposta em tempo real',
            '🔒 <strong>Segurança:</strong> Proteção de dados sensíveis',
            '🌐 <strong>Interoperabilidade:</strong> Integração entre sistemas'
        ],
        rightTitle: 'Soluções Propostas',
        rightItems: [
            '🤖 <strong>Automação:</strong> Redução de intervenção manual',
            '📊 <strong>Analytics:</strong> Decisões baseadas em dados',
            '☁️ <strong>Cloud Native:</strong> Arquitetura distribuída',
            '🔄 <strong>DevOps:</strong> Integração contínua'
        ],
        conclusion: 'A <span class="highlight">inovação tecnológica</span> é fundamental para resolver os <span class="danger-text">desafios complexos</span> do mundo moderno.'
    };

    return SlideTemplates.createThemeSlide(themeData);
}

// Example 4: Creating interactive flip cards with real data
function createReferenceFlipCards() {
    const referencesData = [
        {
            frontIcon: '📚',
            frontTitle: 'Deep Learning para Malware',
            frontContent: 'Técnicas avançadas usando redes neurais profundas',
            backTitle: 'Referências Atuais',
            backContent: `
                <a href="https://example.com/paper1" target="_blank" class="reference-link">
                    📄 Neural Networks for Malware Detection (2024)
                </a>
                <a href="https://example.com/paper2" target="_blank" class="reference-link">
                    📄 AI in Cybersecurity Applications (2024)
                </a>
            `
        },
        {
            frontIcon: '🤖',
            frontTitle: 'Sistemas Multi-Agente',
            frontContent: 'Arquiteturas distribuídas para segurança',
            backTitle: 'Estudos Relacionados',
            backContent: `
                <a href="https://example.com/paper3" target="_blank" class="reference-link">
                    📄 Multi-Agent Systems in Security (2024)
                </a>
                <a href="https://example.com/paper4" target="_blank" class="reference-link">
                    📄 Distributed AI for Threat Detection (2024)
                </a>
            `
        }
    ];

    const grid = document.createElement('div');
    grid.className = 'method-grid';

    referencesData.forEach(data => {
        const flipCard = ComponentFactory.createFlipCard(data);
        grid.appendChild(flipCard);
    });

    return grid;
}

// Example 5: Creating a custom component
function createCustomTimelineComponent(events) {
    const timeline = document.createElement('div');
    timeline.className = 'timeline-component';
    timeline.style.cssText = `
        position: relative;
        padding: 2rem 0;
    `;

    events.forEach((event, index) => {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item glass-card';
        timelineItem.style.cssText = `
            margin: 1rem 0;
            padding: 1rem 2rem;
            position: relative;
            border-left: 3px solid var(--accent);
            animation: slideInLeft 0.6s ease-out forwards;
            animation-delay: ${index * 0.2}s;
            opacity: 0;
        `;

        timelineItem.innerHTML = `
            <h4 style="color: var(--accent); margin-bottom: 0.5rem;">${event.date}</h4>
            <h3 style="margin-bottom: 0.5rem;">${event.title}</h3>
            <p>${event.description}</p>
        `;

        timeline.appendChild(timelineItem);
    });

    return timeline;
}

// Example 6: Creating a complete timeline slide
function createTimelineSlide() {
    const timelineEvents = [
        {
            date: 'Q1 2024',
            title: 'Início da Pesquisa',
            description: 'Levantamento bibliográfico e definição do escopo'
        },
        {
            date: 'Q2 2024',
            title: 'Desenvolvimento do Ambiente',
            description: 'Criação do ambiente virtualizado para testes'
        },
        {
            date: 'Q3 2024',
            title: 'Implementação dos Agentes',
            description: 'Desenvolvimento da arquitetura multi-agente'
        },
        {
            date: 'Q4 2024',
            title: 'Testes e Validação',
            description: 'Execução de experimentos e análise de resultados'
        }
    ];

    const timelineComponent = createCustomTimelineComponent(timelineEvents);

    const content = `
        <h2>Cronograma da Pesquisa</h2>
        ${timelineComponent.outerHTML}
    `;

    return ComponentFactory.createSlide({
        className: 'timeline-slide',
        content: content
    });
}

// Example 7: Function to demonstrate adding slides dynamically
function demonstrateComponentUsage() {
    console.log('🎯 Demonstrating component system usage...');

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addExampleSlides);
    } else {
        addExampleSlides();
    }
}

function addExampleSlides() {
    try {
        // Create and add new slides
        const container = document.querySelector('.slides-container');

        // Add research slide
        const researchSlide = createNewResearchSlide();
        container.appendChild(researchSlide);

        // Add timeline slide
        const timelineSlide = createTimelineSlide();
        container.appendChild(timelineSlide);

        // Update presentation manager
        if (window.presentationManager) {
            window.presentationManager.slides = document.querySelectorAll('.slide');
            window.presentationManager.totalSlides = window.presentationManager.slides.length;
            window.presentationManager.updateTotalSlides();
        }

        console.log('✅ Example slides added successfully!');
        console.log(`📊 Total slides: ${document.querySelectorAll('.slide').length}`);

    } catch (error) {
        console.error('❌ Error adding example slides:', error);
    }
}

// Example 8: Utility function to export slide data
function exportSlideData() {
    const slides = document.querySelectorAll('.slide');
    const slideData = [];

    slides.forEach((slide, index) => {
        const title = slide.querySelector('h1, h2')?.textContent || `Slide ${index + 1}`;
        const content = slide.querySelector('.slide-content')?.innerHTML || '';

        slideData.push({
            index: index + 1,
            title: title,
            className: slide.className,
            hasInteractiveElements: slide.querySelectorAll('.flip-card, .method-card').length > 0
        });
    });

    console.log('📋 Slide Data Export:', slideData);
    return slideData;
}

// Example 9: Theme customization function
function applyCustomTheme(themeName) {
    const themes = {
        dark: {
            '--primary': '#000000',
            '--accent': '#ff6b6b',
            '--danger': '#4ecdc4'
        },
        ocean: {
            '--primary': '#0f3460',
            '--accent': '#16537e',
            '--danger': '#533a7b'
        },
        forest: {
            '--primary': '#2d5016',
            '--accent': '#4a7c59',
            '--danger': '#6b5b95'
        }
    };

    if (themes[themeName]) {
        const root = document.documentElement;
        Object.entries(themes[themeName]).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });
        console.log(`🎨 Applied theme: ${themeName}`);
    }
}

// Example 10: Performance monitoring
function monitorPerformance() {
    if ('performance' in window) {
        const navigation = performance.getEntriesByType('navigation')[0];
        console.log('⚡ Performance Metrics:');
        console.log(`📏 DOM Content Loaded: ${navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart}ms`);
        console.log(`🔄 Page Load: ${navigation.loadEventEnd - navigation.loadEventStart}ms`);

        // Monitor animation performance
        let animationFrames = 0;
        function countFrames() {
            animationFrames++;
            if (animationFrames < 60) {
                requestAnimationFrame(countFrames);
            } else {
                console.log('🎬 Animation performance: 60 frames measured');
            }
        }
        requestAnimationFrame(countFrames);
    }
}

// Auto-run examples when script loads (commented out by default)
// demonstrateComponentUsage();

// Export functions for manual testing
window.ComponentExamples = {
    createExampleSlide,
    createMethodCards,
    createNewResearchSlide,
    createCustomAgendaSlide,
    createCustomThemeSlide,
    createReferenceFlipCards,
    createTimelineSlide,
    demonstrateComponentUsage,
    exportSlideData,
    applyCustomTheme,
    monitorPerformance
};

console.log('📖 Component examples loaded! Try:');
console.log('ComponentExamples.demonstrateComponentUsage()');
console.log('ComponentExamples.applyCustomTheme("ocean")');
console.log('ComponentExamples.exportSlideData()');

// Example usage of the Roulette Component

// Example 1: Creating a basic roulette
const basicItems = [
    { icon: '🎯', title: 'Item 1', description: 'First item description' },
    { icon: '🔍', title: 'Item 2', description: 'Second item description' },
    { icon: '⚡', title: 'Item 3', description: 'Third item description' }
];

// Create a container for the roulette
function createRouletteExample() {
    const container = document.createElement('div');
    container.id = 'example-roulette';
    document.body.appendChild(container);

    // Initialize the roulette
    const roulette = createRoulette(basicItems, 'example-roulette');

    return roulette;
}

// Example 2: Advanced usage with custom controls
function advancedRouletteExample() {
    const advancedItems = [
        { icon: '🚀', title: 'Launch', description: 'Start your journey' },
        { icon: '🔧', title: 'Configure', description: 'Set up your system' },
        { icon: '📊', title: 'Analyze', description: 'Review the results' },
        { icon: '✨', title: 'Optimize', description: 'Improve performance' }
    ];

    const container = document.createElement('div');
    container.id = 'advanced-roulette';
    document.body.appendChild(container);

    const roulette = createRoulette(advancedItems, 'advanced-roulette');

    // Add custom controls
    const controlsDiv = document.createElement('div');
    controlsDiv.innerHTML = `
        <div style="text-align: center; margin-top: 1rem;">
            <button onclick="roulette.goTo(0)">Go to Start</button>
            <button onclick="roulette.goTo(${advancedItems.length - 1})">Go to End</button>
            <span>Current: <span id="current-index">0</span></span>
        </div>
    `;

    container.appendChild(controlsDiv);

    return roulette;
}

// Keyboard shortcuts guide
const keyboardGuide = `
🎰 ROULETTE KEYBOARD SHORTCUTS:
--------------------------------
↑ or ▲    - Previous item
↓ or ▼    - Next item
Click     - Use mouse buttons
Scroll    - Future feature

🎯 FEATURES:
-----------
✨ 3D rotation effects
🎨 Cyberpunk styling
📱 Responsive design
⌨️ Keyboard navigation
🖱️ Mouse controls
🔢 Item counter
🎪 Smooth animations
`;

console.log(keyboardGuide);

// Export for use in presentation
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createRouletteExample,
        advancedRouletteExample,
        basicItems
    };
} 