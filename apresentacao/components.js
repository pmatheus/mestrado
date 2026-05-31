/**
 * ========================================
 * REUSABLE COMPONENTS LIBRARY
 * ========================================
 */

/**
 * Component Factory Class
 * Creates reusable UI components for the presentation
 */
class ComponentFactory {

    /**
     * Creates a basic slide structure
     * @param {Object} config - Slide configuration
     * @param {string} config.id - Slide ID
     * @param {string} config.className - Additional CSS classes
     * @param {string} config.content - HTML content for the slide
     * @returns {HTMLElement} - Complete slide element
     */
    static createSlide(config) {
        const slide = document.createElement('div');
        slide.className = `slide ${config.className || ''}`;
        if (config.id) slide.id = config.id;

        const slideContent = document.createElement('div');
        slideContent.className = 'slide-content';
        slideContent.innerHTML = config.content || '';

        slide.appendChild(slideContent);
        return slide;
    }

    /**
     * Creates a title slide with AI visualization
     * @param {Object} config - Title slide configuration
     * @returns {HTMLElement} - Title slide element
     */
    static createTitleSlide(config) {
        const content = `
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

        return this.createSlide({
            className: 'title-slide',
            content: content
        });
    }

    /**
     * Creates a glass card component
     * @param {Object} config - Card configuration
     * @returns {HTMLElement} - Glass card element
     */
    static createGlassCard(config) {
        const card = document.createElement('div');
        card.className = `glass-card ${config.className || ''}`;

        if (config.title) {
            const title = document.createElement('h3');
            title.textContent = config.title;
            card.appendChild(title);
        }

        if (config.content) {
            const content = document.createElement('div');
            content.innerHTML = config.content;
            card.appendChild(content);
        }

        return card;
    }

    /**
     * Creates a method card with icon
     * @param {Object} config - Method card configuration
     * @returns {HTMLElement} - Method card element
     */
    static createMethodCard(config) {
        const card = document.createElement('div');
        card.className = 'method-card';

        const content = `
            <div class="icon">${config.icon}</div>
            <h3>${config.title}</h3>
            <p>${config.description}</p>
        `;

        card.innerHTML = content;
        return card;
    }

    /**
     * Creates a flip card with front and back content
     * @param {Object} config - Flip card configuration
     * @returns {HTMLElement} - Flip card element
     */
    static createFlipCard(config) {
        const flipCard = document.createElement('div');
        flipCard.className = 'flip-card';

        const inner = document.createElement('div');
        inner.className = 'flip-card-inner';

        const front = document.createElement('div');
        front.className = 'flip-card-front';
        front.innerHTML = `
            <div class="icon">${config.frontIcon}</div>
            <h3>${config.frontTitle}</h3>
            <p>${config.frontContent}</p>
            <p class="flip-instruction">Clique para ver referências</p>
        `;

        const back = document.createElement('div');
        back.className = 'flip-card-back';
        back.innerHTML = `
            <h4>${config.backTitle}</h4>
            ${config.backContent}
        `;

        inner.appendChild(front);
        inner.appendChild(back);
        flipCard.appendChild(inner);

        return flipCard;
    }

    /**
     * Creates a reference link
     * @param {Object} config - Link configuration
     * @returns {HTMLElement} - Reference link element
     */
    static createReferenceLink(config) {
        const link = document.createElement('a');
        link.href = config.url;
        link.target = '_blank';
        link.className = 'reference-link';
        link.textContent = config.text;
        return link;
    }

    /**
     * Creates a feature list
     * @param {Array} items - List of feature items
     * @returns {HTMLElement} - Feature list element
     */
    static createFeatureList(items) {
        const list = document.createElement('ul');
        list.className = 'feature-list';

        items.forEach(item => {
            const listItem = document.createElement('li');
            listItem.innerHTML = item;
            list.appendChild(listItem);
        });

        return list;
    }

    /**
     * Creates a method grid with cards
     * @param {Array} methods - Array of method configurations
     * @param {number} columns - Number of columns (2 or 3)
     * @returns {HTMLElement} - Method grid element
     */
    static createMethodGrid(methods, columns = 2) {
        const grid = document.createElement('div');
        grid.className = 'method-grid';

        if (columns === 3) {
            grid.style.gridTemplateColumns = 'repeat(3, 1fr)';
        }

        methods.forEach(method => {
            const card = this.createMethodCard(method);
            grid.appendChild(card);
        });

        return grid;
    }

    /**
     * Creates a two-column layout
     * @param {string} leftContent - HTML content for left column
     * @param {string} rightContent - HTML content for right column
     * @returns {HTMLElement} - Two column layout element
     */
    static createTwoColumn(leftContent, rightContent) {
        const container = document.createElement('div');
        container.className = 'two-column';

        const leftColumn = document.createElement('div');
        leftColumn.innerHTML = leftContent;

        const rightColumn = document.createElement('div');
        rightColumn.innerHTML = rightContent;

        container.appendChild(leftColumn);
        container.appendChild(rightColumn);

        return container;
    }

    /**
     * Creates a threat visualization
     * @returns {HTMLElement} - Threat visual element
     */
    static createThreatVisual() {
        const container = document.createElement('div');
        container.className = 'threat-visual';

        for (let i = 1; i <= 3; i++) {
            const circle = document.createElement('div');
            circle.className = 'threat-circle';
            container.appendChild(circle);
        }

        return container;
    }

    /**
     * Creates a limitation item
     * @param {Object} config - Limitation configuration
     * @returns {HTMLElement} - Limitation item element
     */
    static createLimitationItem(config) {
        const item = document.createElement('div');
        item.className = 'limitation-item';

        const title = document.createElement('h3');
        title.textContent = config.title;

        const description = document.createElement('p');
        description.textContent = config.description;

        item.appendChild(title);
        item.appendChild(description);

        return item;
    }
}

/**
 * Slide Templates
 * Pre-configured slide templates for common layouts
 */
class SlideTemplates {

    /**
     * Creates a problem slide
     * @param {Object} config - Problem slide configuration
     */
    static createProblemSlide(config) {
        const leftContent = `
            <div class="glass-card">
                <h3 class="danger-text">${config.scenarioTitle}</h3>
                ${ComponentFactory.createFeatureList(config.problems).outerHTML}
            </div>
        `;

        const rightContent = ComponentFactory.createThreatVisual().outerHTML;

        const content = `
            <h2>${config.title}</h2>
            ${ComponentFactory.createTwoColumn(leftContent, rightContent).outerHTML}
        `;

        return ComponentFactory.createSlide({ content });
    }

    /**
     * Creates an objectives slide
     * @param {Object} config - Objectives configuration
     */
    static createObjectivesSlide(config) {
        const grid = ComponentFactory.createMethodGrid(config.objectives);

        const content = `
            <h2>${config.title}</h2>
            ${grid.outerHTML}
        `;

        return ComponentFactory.createSlide({ content });
    }

    /**
     * Creates a methodology slide
     * @param {Object} config - Methodology configuration
     */
    static createMethodologySlide(config) {
        const grid = ComponentFactory.createMethodGrid(config.phases, 3);

        const content = `
            <h2>${config.title}</h2>
            <div class="glass-card" style="margin-bottom: 1rem;">
                <h3>${config.subtitle}</h3>
            </div>
            ${grid.outerHTML}
        `;

        return ComponentFactory.createSlide({ content });
    }

    /**
     * Creates a results slide
     * @param {Object} config - Results configuration
     */
    static createResultsSlide(config) {
        const leftContent = ComponentFactory.createGlassCard({
            title: config.technicalTitle,
            content: ComponentFactory.createFeatureList(config.technicalContributions).outerHTML,
            className: 'highlight'
        }).outerHTML;

        const rightContent = ComponentFactory.createGlassCard({
            title: config.impactsTitle,
            content: ComponentFactory.createFeatureList(config.impacts).outerHTML,
            className: 'highlight'
        }).outerHTML;

        const content = `
            <h2>${config.title}</h2>
            ${ComponentFactory.createTwoColumn(leftContent, rightContent).outerHTML}
        `;

        return ComponentFactory.createSlide({ content });
    }

    /**
 * Creates a limitations slide
 * @param {Object} config - Limitations configuration
 */
    static createLimitationsSlide(config) {
        const limitationsContainer = document.createElement('div');
        limitationsContainer.style.maxWidth = '800px';
        limitationsContainer.style.margin = '0 auto';

        config.limitations.forEach(limitation => {
            const limitationItem = ComponentFactory.createLimitationItem(limitation);
            limitationsContainer.appendChild(limitationItem);
        });

        const conclusionCard = ComponentFactory.createGlassCard({
            content: `<p style="font-style: italic;">${config.conclusion}</p>`
        });
        conclusionCard.style.marginTop = '2rem';

        const content = `
            <h2>${config.title}</h2>
            ${limitationsContainer.outerHTML}
            ${conclusionCard.outerHTML}
        `;

        return ComponentFactory.createSlide({ content });
    }

    /**
     * Creates an agenda slide
     * @param {Object} config - Agenda configuration
     */
    static createAgendaSlide(config) {
        const grid = ComponentFactory.createMethodGrid(config.agendaItems, 2);

        const content = `
            <h2>📋 ${config.title}</h2>
            <div class="glass-card" style="max-width: 900px; margin: 2rem auto;">
                <h3 style="margin-bottom: 2rem; color: var(--accent);">${config.subtitle}</h3>
            </div>
            ${grid.outerHTML}
        `;

        return ComponentFactory.createSlide({ content });
    }

    /**
     * Creates a theme presentation slide
     * @param {Object} config - Theme presentation configuration
     */
    static createThemeSlide(config) {
        const leftContent = ComponentFactory.createGlassCard({
            content: `
                <h3 style="color: var(--accent); margin-bottom: 1.5rem;">${config.leftTitle}</h3>
                ${ComponentFactory.createFeatureList(config.leftItems).outerHTML}
            `
        }).outerHTML;

        const rightContent = ComponentFactory.createGlassCard({
            content: `
                <h3 style="color: var(--danger); margin-bottom: 1.5rem;">${config.rightTitle}</h3>
                ${ComponentFactory.createFeatureList(config.rightItems).outerHTML}
            `
        }).outerHTML;

        const conclusionCard = ComponentFactory.createGlassCard({
            content: `
                <p style="font-size: 1.3rem; line-height: 1.6; font-style: italic; text-align: center;">
                    ${config.conclusion}
                </p>
            `
        });
        conclusionCard.style.marginTop = '2rem';

        const content = `
            <h2>🎯 ${config.title}</h2>
            ${ComponentFactory.createTwoColumn(leftContent, rightContent).outerHTML}
            ${conclusionCard.outerHTML}
        `;

        return ComponentFactory.createSlide({ content });
    }
}

/**
 * Data Templates
 * Default data configurations for common slides
 */
const SlideData = {
    title: {
        title: "Threat Hunting de Spywares",
        subtitle: "Utilizando Agentes de Inteligência Artificial para Detecção Proativa de Ameaças",
        description: "MPC1 - Projeto de Pesquisa - Mestrado em Segurança Cibernética - PPEE - UnB",
        author: "Paulo Matheus Nicolau Silva - 251122852"
    },

    agenda: {
        title: "Agenda",
        subtitle: "Estrutura da Apresentação",
        agendaItems: [
            {
                icon: "🎯",
                title: "1. Apresentação do Tema",
                description: "Contextualização e relevância da pesquisa"
            },
            {
                icon: "❗",
                title: "2. Problema",
                description: "Desafios atuais em detecção de spywares"
            },
            {
                icon: "📚",
                title: "3. Trabalhos Correlatos",
                description: "Estado da arte em IA e cibersegurança"
            },
            {
                icon: "🎯",
                title: "4. Objetivo Geral",
                description: "Proposta de arquitetura multi-agente"
            },
            {
                icon: "📋",
                title: "5. Objetivos Específicos",
                description: "Metas detalhadas do projeto"
            },
            {
                icon: "💡",
                title: "6. Hipótese",
                description: "Premissa central da pesquisa"
            },
            {
                icon: "✅",
                title: "7. Justificativa",
                description: "Fundamentação teórica e prática"
            },
            {
                icon: "🔬",
                title: "8. Metodologia",
                description: "Fases de desenvolvimento e testes"
            },
            {
                icon: "📈",
                title: "9. Resultados Esperados",
                description: "Contribuições técnicas e impactos"
            },
            {
                icon: "⚠️",
                title: "10. Limitações",
                description: "Desafios e restrições identificadas"
            }
        ]
    },

    theme: {
        title: "Apresentação do Tema",
        leftTitle: "Threat Hunting Moderno",
        leftItems: [
            "🔍 <strong>Caça Proativa:</strong> Busca ativa por ameaças antes da detecção",
            "🤖 <strong>IA como Aliada:</strong> Automação e inteligência artificial",
            "🎯 <strong>Foco em Spywares:</strong> Ameaças persistentes avançadas",
            "🛡️ <strong>Defesa Adaptativa:</strong> Evolução contínua das estratégias"
        ],
        rightTitle: "Por que Agentes de IA?",
        rightItems: [
            "⚡ <strong>Velocidade:</strong> Resposta em tempo real a ameaças",
            "🧠 <strong>Aprendizado:</strong> Adaptação a novos padrões de ataque",
            "🔗 <strong>Colaboração:</strong> Múltiplos agentes especializados",
            "📊 <strong>Precisão:</strong> Redução de falsos positivos"
        ],
        conclusion: '<span class="highlight">"A convergência entre Inteligência Artificial e Cibersegurança"</span> representa o futuro da defesa digital, onde <span class="danger-text">agentes autônomos</span> trabalham colaborativamente para identificar e neutralizar ameaças sofisticadas.'
    },

    problem: {
        title: "Problema",
        scenarioTitle: "Cenário Atual",
        problems: [
            "📈 Crescimento exponencial de spywares sofisticados",
            "🎯 Técnicas avançadas de evasão e persistência",
            "🔒 Limitações dos métodos tradicionais de detecção",
            "⚡ Necessidade de resposta proativa e inteligente"
        ]
    },

    objectives: {
        title: "Objetivos Específicos",
        objectives: [
            {
                icon: "🎯",
                title: "Modelagem de Agentes",
                description: "Definir arquitetura e especialização dos agentes de IA"
            },
            {
                icon: "🛡️",
                title: "Modelar Ambiente",
                description: "Modelar ambiente de execução controlado para testes"
            },
            {
                icon: "🔬",
                title: "Detecção Inteligente",
                description: "Desenvolver e aplicar processo de identificação de spywares"
            },
            {
                icon: "📊",
                title: "Avaliação de Eficácia",
                description: "Validar o sistema em ambientes controlados"
            }
        ]
    },

    methodology: {
        title: "Metodologia",
        subtitle: "Fases do Desenvolvimento",
        phases: [
            {
                icon: "1️⃣",
                title: "Definição do Ambiente de Caça",
                description: "Desenvolvimento de VM que servirá de base replicável para testes"
            },
            {
                icon: "2️⃣",
                title: "Design da Arquitetura",
                description: "Modelagem do sistema multi-agente"
            },
            {
                icon: "3️⃣",
                title: "Implementação",
                description: "Desenvolvimento dos agentes de IA"
            },
            {
                icon: "4️⃣",
                title: "Treinamento",
                description: "Preparação com datasets de spyware"
            },
            {
                icon: "5️⃣",
                title: "Validação",
                description: "Testes em ambiente controlado"
            },
            {
                icon: "6️⃣",
                title: "Análise",
                description: "Avaliação de resultados e melhorias"
            }
        ]
    },

    results: {
        title: "Resultados Esperados",
        technicalTitle: "Contribuições Técnicas",
        technicalContributions: [
            "🏗️ Arquitetura inovadora de agentes especializados",
            "🔍 Melhoria na detecção de spywares avançados",
            "📈 Menor taxa de falsos positivos"
        ],
        impactsTitle: "Impactos Esperados",
        impacts: [
            "🛡️ <strong>Segurança:</strong> Proteção aprimorada contra ameaças",
            "🔬 <strong>Científico:</strong> Avanço no campo de IA em cibersegurança",
            "🏢 <strong>Prático:</strong> Aplicabilidade em ambientes reais",
            "📚 <strong>Acadêmico:</strong> Publicações e disseminação do conhecimento"
        ]
    },

    limitations: {
        title: "Limitações",
        limitations: [
            {
                title: "Complexidade Computacional",
                description: "Sistema multi-agente demanda recursos significativos de processamento"
            },
            {
                title: "Dependência de Dados",
                description: "Qualidade do treinamento depende da disponibilidade de amostras atualizadas"
            },
            {
                title: "Evolução das Ameaças",
                description: "Spywares em constante evolução podem exigir atualizações frequentes"
            },
            {
                title: "Escopo Inicial",
                description: "Foco específico em spywares, não abrangendo todo espectro de malware"
            }
        ],
        conclusion: "As limitações identificadas serão endereçadas através de pesquisa contínua e refinamento iterativo do sistema proposto."
    }
};

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ComponentFactory, SlideTemplates, SlideData };
}

// Roulette Component
function createRoulette(items, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let currentIndex = 0;

    const rouletteHTML = `
        <div class="roulette-container">
            <div class="roulette-wheel">
                <div class="roulette-items" id="roulette-items-${containerId}">
                    ${items.map((item, index) => `
                        <div class="roulette-item ${index === 0 ? 'active' : ''}" data-index="${index}">
                            <div class="item-icon">${item.icon}</div>
                            <h3>${item.title}</h3>
                            <p>${item.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="roulette-controls">
                <button class="roulette-btn roulette-up" id="roulette-up-${containerId}">
                    <span>↑</span>
                    <span>Anterior</span>
                </button>
                <div class="roulette-counter">
                    <span id="current-item-${containerId}">1</span> / <span id="total-items-${containerId}">${items.length}</span>
                </div>
                <button class="roulette-btn roulette-down" id="roulette-down-${containerId}">
                    <span>↓</span>
                    <span>Próximo</span>
                </button>
            </div>
        </div>
    `;

    container.innerHTML = rouletteHTML;

    const itemsContainer = document.getElementById(`roulette-items-${containerId}`);
    const upBtn = document.getElementById(`roulette-up-${containerId}`);
    const downBtn = document.getElementById(`roulette-down-${containerId}`);
    const currentItemSpan = document.getElementById(`current-item-${containerId}`);

    function updateRoulette(direction = 'none') {
        const allItems = itemsContainer.querySelectorAll('.roulette-item');

        // Add spinning animation
        itemsContainer.classList.add(`spinning-${direction}`);

        setTimeout(() => {
            // Update active item
            allItems.forEach((item, index) => {
                item.classList.toggle('active', index === currentIndex);
            });

            // Update counter
            currentItemSpan.textContent = currentIndex + 1;

            // Remove spinning animation
            itemsContainer.classList.remove(`spinning-${direction}`);
        }, 150);
    }

    function goUp() {
        if (currentIndex > 0) {
            currentIndex--;
            updateRoulette('up');
        }
    }

    function goDown() {
        if (currentIndex < items.length - 1) {
            currentIndex++;
            updateRoulette('down');
        }
    }

    // Event listeners
    upBtn.addEventListener('click', goUp);
    downBtn.addEventListener('click', goDown);

    // Keyboard navigation (only when focused on roulette)
    container.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            e.stopPropagation();
            goUp();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            e.stopPropagation();
            goDown();
        }
    });
    
    // Make container focusable
    container.setAttribute('tabindex', '0');

    return {
        goTo: (index) => {
            if (index >= 0 && index < items.length) {
                const direction = index > currentIndex ? 'down' : 'up';
                currentIndex = index;
                updateRoulette(direction);
            }
        },
        getCurrentIndex: () => currentIndex,
        getItems: () => items
    };
}

// Agenda Roulette Data
const agendaItems = [
    { icon: '🎯', title: 'Tema', description: 'Orquestração de Agentes de IA' },
    { icon: '❗', title: 'Problema', description: 'Cenário atual de ameaças' },
    { icon: '📚', title: 'Trabalhos Correlatos', description: 'Estado da arte' },
    { icon: '🎯', title: 'Objetivo Geral', description: 'Arquitetura multi-agente' },
    { icon: '📋', title: 'Objetivos Específicos', description: 'Metas detalhadas' },
    { icon: '💡', title: 'Hipótese', description: 'Premissa central' },
    { icon: '✅', title: 'Justificativa', description: 'Fundamentação teórica' },
    { icon: '🔬', title: 'Metodologia', description: 'Fases de desenvolvimento' },
    { icon: '📈', title: 'Resultados Esperados', description: 'Contribuições técnicas' },
    { icon: '⚠️', title: 'Limitações', description: 'Desafios identificados' }
]; 