# 🚀 Threat Hunting Presentation

Uma apresentação interativa sobre **Threat Hunting de Spywares com Agentes de IA**, construída com HTML, CSS e JavaScript modulares.

## 📁 Estrutura do Projeto

```
apresentacao/
├── index.html          # Arquivo principal da apresentação
├── styles.css          # Estilos CSS separados e organizados
├── script.js           # Lógica JavaScript principal
├── components.js       # Biblioteca de componentes reutilizáveis
└── README.md          # Este arquivo
```

## 🎯 Características

### ✨ **Design Modular**
- **CSS separado**: Estilos organizados por seções com comentários claros
- **JavaScript modular**: Classes e componentes bem estruturados
- **Componentes reutilizáveis**: Biblioteca para criar elementos facilmente

### 🎮 **Interatividade**
- **Navegação**: Teclado (setas), touch/swipe, botões
- **Animações**: Transições suaves e efeitos visuais cyber
- **Cards interativos**: Flip cards com referências acadêmicas
- **Acessibilidade**: Suporte a leitores de tela e navegação por teclado
- **12 Slides**: Inclui novos slides de Agenda e Apresentação do Tema

### 🎨 **Visual**
- **Tema cyber**: Cores neon, gradientes e animações futurísticas
- **Glassmorphism**: Efeitos de vidro com blur e transparência
- **Responsivo**: Adaptável a diferentes tamanhos de tela

## 🛠️ Como Usar

### **Executar a Apresentação**
```bash
# Abra o index.html em qualquer navegador moderno
open index.html
```

### **Navegação**
- **Setas ← →**: Navegar entre slides
- **Home/End**: Ir para primeiro/último slide
- **Touch/Swipe**: Arraste para navegar (mobile)
- **Botões**: Use os botões na parte inferior

## 🧩 Componentes Reutilizáveis

### **ComponentFactory**
Cria elementos UI reutilizáveis:

```javascript
// Criar um slide básico
const slide = ComponentFactory.createSlide({
    className: 'custom-slide',
    content: '<h2>Meu Slide</h2>'
});

// Criar um card de método
const methodCard = ComponentFactory.createMethodCard({
    icon: '🔬',
    title: 'Análise Avançada',
    description: 'Descrição da metodologia'
});

// Criar um flip card
const flipCard = ComponentFactory.createFlipCard({
    frontIcon: '📊',
    frontTitle: 'Estatísticas',
    frontContent: 'Dados importantes',
    backTitle: 'Referências',
    backContent: '<a href="#">Link para estudo</a>'
});
```

### **SlideTemplates**
Templates prontos para slides comuns:

```javascript
// Slide de agenda
const agendaSlide = SlideTemplates.createAgendaSlide({
    title: 'Agenda',
    subtitle: 'Estrutura da Apresentação',
    agendaItems: [
        { icon: '🎯', title: '1. Tópico', description: 'Descrição' }
    ]
});

// Slide de apresentação do tema
const themeSlide = SlideTemplates.createThemeSlide({
    title: 'Meu Tema',
    leftTitle: 'Desafios',
    leftItems: ['Item 1', 'Item 2'],
    rightTitle: 'Soluções',
    rightItems: ['Solução 1', 'Solução 2'],
    conclusion: 'Texto de conclusão'
});

// Slide de problema
const problemSlide = SlideTemplates.createProblemSlide({
    title: 'Desafios Atuais',
    scenarioTitle: 'Cenário',
    problems: ['Item 1', 'Item 2', 'Item 3']
});

// Slide de metodologia
const methodSlide = SlideTemplates.createMethodologySlide({
    title: 'Nossa Abordagem',
    subtitle: 'Fases do Processo',
    phases: [
        { icon: '1️⃣', title: 'Fase 1', description: 'Descrição' }
    ]
});
```

## 🎨 Personalização de Estilos

### **Variáveis CSS**
Todas as cores e valores estão centralizados:

```css
:root {
    --primary: #0a0e27;      /* Cor de fundo principal */
    --secondary: #1a1f3a;    /* Cor secundária */
    --accent: #00ff88;       /* Cor de destaque (verde) */
    --danger: #ff0066;       /* Cor de alerta (rosa) */
    --warning: #ffaa00;      /* Cor de aviso (laranja) */
    --text: #ffffff;         /* Texto principal */
    --text-secondary: #a8b2d1; /* Texto secundário */
    --glass: rgba(255, 255, 255, 0.05); /* Efeito de vidro */
}
```

### **Classes Principais**
- `.glass-card`: Cards com efeito glassmorphism
- `.method-card`: Cards para metodologias/objetivos
- `.flip-card`: Cards que viram ao clicar
- `.feature-list`: Listas animadas com ícones
- `.two-column`: Layout de duas colunas
- `.highlight`: Texto com cor de destaque
- `.danger-text`: Texto com cor de alerta

## 🔧 Extensibilidade

### **Adicionar Novos Slides**
```javascript
// No HTML, adicione um novo slide
const newSlide = document.createElement('div');
newSlide.className = 'slide';
newSlide.innerHTML = `
    <div class="slide-content">
        <h2>Novo Tópico</h2>
        <!-- Conteúdo -->
    </div>
`;
document.querySelector('.slides-container').appendChild(newSlide);
```

### **Criar Componentes Personalizados**
```javascript
// Adicione ao ComponentFactory
static createCustomComponent(config) {
    const element = document.createElement('div');
    element.className = 'custom-component';
    element.innerHTML = config.content;
    return element;
}
```

### **Adicionar Novas Animações**
```css
/* No styles.css */
@keyframes newAnimation {
    from { transform: scale(0); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.new-element {
    animation: newAnimation 0.5s ease-out;
}
```

## 📱 Compatibilidade

- **Navegadores**: Chrome, Firefox, Safari, Edge (versões modernas)
- **Mobile**: Suporte completo com gestos touch
- **Acessibilidade**: ARIA labels, navegação por teclado, leitores de tela

## 🚀 Performance

- **Carregamento rápido**: CSS e JS otimizados
- **Animações suaves**: Uso de GPU quando possível
- **Reduced motion**: Respeita preferências de acessibilidade
- **Lazy loading**: Preparado para conteúdo pesado

## 🎯 Próximos Passos

### **Melhorias Possíveis**
1. **Temas**: Sistema de troca de temas
2. **Export**: Função para exportar como PDF
3. **Zoom**: Zoom em slides específicos
4. **Notas**: Sistema de notas do apresentador
5. **Transições**: Mais tipos de transições entre slides

### **Integração**
- **CMS**: Conectar com sistema de gerenciamento
- **API**: Carregar dados dinamicamente
- **Analytics**: Rastreamento de uso da apresentação

## 💡 Dicas de Desenvolvimento

### **Debugging**
```javascript
// Acesse o gerenciador globalmente
console.log(window.presentationManager);

// Ir para slide específico
window.presentationManager.goToSlide(3);
```

### **Adicionar Logs**
```javascript
// Os scripts já incluem logs úteis
console.log('🚀 Presentation initialized!');
```

### **Customizar Componentes**
```javascript
// Sobrescreva métodos se necessário
class CustomPresentationManager extends PresentationManager {
    changeSlide(direction) {
        // Lógica customizada
        console.log(`Mudando para slide: ${direction}`);
        super.changeSlide(direction);
    }
}
```

---

## 📧 Contato

**Paulo Matheus Nicolau Silva** - Mestrado em Segurança Cibernética - UnB

*"Construindo o futuro da detecção de ameaças com IA"* 🤖🛡️ 