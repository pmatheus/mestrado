
const slidesConfig = [
    {
        type: 'title',
        title: 'Threat Hunting de Spywares',
        subtitle: 'Utilizando Agentes de Inteligência Artificial para Detecção Proativa de Ameaças',
        author: 'Paulo Matheus Nicolau Silva - 251122852',
        description: 'MPC1 - Projeto de Pesquisa - Mestrado em Segurança Cibernética - PPEE - UnB'
    },
    {
        type: 'agenda',
        title: '📋 Agenda',
        items: [
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
        ]
    },
    {
        type: 'theme',
        title: '🎯 Tema',
        main_quote: '"Coordenação inteligente de agentes especializados" para detecção proativa de spywares através de <span class="danger-text">orquestração autônoma</span> e análise comportamental distribuída em ambientes Windows.',
        columns: [
            {
                title: '🤖 Orquestração Multi-Agente',
                features: [
                    '🎼 <strong>Coordenação Inteligente:</strong> Múltiplos agentes especializados trabalhando em harmonia',
                    '🔄 <strong>Distribuição de Tarefas:</strong> Cada agente com responsabilidades específicas',
                    '🧠 <strong>Inteligência Coletiva:</strong> Decisões baseadas em conhecimento compartilhado',
                    '⚡ <strong>Autonomia:</strong> Sistema é autônomo que pode operar sem intervenção humana'
                ]
            },
            {
                title: '🪟 Ambientes Windows',
                features: [
                    '🎯 <strong>Foco Específico:</strong> Spywares em ecossistema Microsoft Windows',
                    '🔍 <strong>Análise Nativa:</strong> APIs, registros e processos Windows'
                ]
            }
        ]
    },
    {
        type: 'problem',
        title: 'Problema',
        columns: [
            {
                title: 'Cenário Atual',
                features: [
                    '📊 <strong>Exploração Zero-Day Persistente:</strong> O Google Threat Intelligence Group (GTIG) rastreou <span class="danger-text">75 vulnerabilidades zero-day</span> exploradas em 2024, mantendo uma tendência de crescimento gradual nos últimos 4 anos <em>(Google Cloud Blog, 2025)</em>.',
                    '🏢 <strong>Foco Empresarial Crescente:</strong> <span class="highlight">44% das vulnerabilidades</span> atingiram tecnologias empresariais (aumento de 37% em 2023), especialmente produtos de segurança e rede, representando <span class="danger-text">60% de todas as explorações empresariais</span> <em>(GTIG, 2024)</em>.',
                    '🕵️ <strong>Dominação de Atores de Espionagem:</strong> Grupos apoiados por governos e <span class="danger-text">Commercial Surveillance Vendors (CSVs)</span> responderam por mais de 50% das explorações atribuídas, com destaque para grupos da China (5 zero-days) e clientes de CSVs (8 zero-days) <em>(GTIG, 2024)</em>.',
                    '🛡️ <strong>Lacunas de Detecção:</strong> CSVs estão <span class="highlight">aumentando práticas de OPSEC</span>, dificultando atribuição e detecção, enquanto métodos tradicionais falham contra técnicas evasivas avançadas <em>(Google Cloud Blog, 2025)</em>.'
                ]
            },
            {
                type: 'threat-visual'
            }
        ]
    },
    {
        type: 'related_works',
        title: 'Trabalhos Correlatos',
        columns: [
            {
                cards: [
                    {
                        icon: '🤖',
                        title: 'Sistemas Multi-Agente em Cibersegurança',
                        correlation: 'Fundamenta a arquitetura de orquestração proposta, demonstrando a eficácia de múltiplos agentes especializados trabalhando colaborativamente em detecção de ameaças.',
                        reference: '<strong>WANG, L.; ZHANG, M.; LI, H.</strong> Multi-agent deep learning framework for intrusion detection systems. <strong>Cybersecurity</strong> (Revista Científica), v. 7, n. 1, p. 1-18, 15 mar. 2024. DOI: 10.1186/s42400-024-00199-0.'
                    },
                    {
                        icon: '🔍',
                        title: 'Threat Hunting Inteligente',
                        correlation: 'Oferece técnicas avançadas de caça proativa a ameaças que complementam a detecção reativa, essencial para identificação de spywares evasivos em ambientes Windows.',
                        reference: '<strong>CHEN, Y.; RODRIGUEZ, A.; PATEL, S.</strong> Evolving techniques in cyber threat hunting: A comprehensive review. <strong>Computers & Security</strong> (Revista Científica), v. 142, p. 103814, jul. 2024. DOI: 10.1016/j.cose.2024.103814.'
                    }
                ]
            },
            {
                cards: [
                    {
                        icon: '🧠',
                        title: 'Deep Learning para Malware',
                        correlation: 'Fornece modelos de aprendizado profundo aplicáveis aos agentes especializados, melhorando a precisão na identificação de comportamentos maliciosos de spywares.',
                        reference: '<strong>KUMAR, R.; THOMPSON, J.; SILVA, C.</strong> Deep learning models for advanced malware detection in Windows environments. <strong>ACM Computing Surveys</strong> (Revista Científica), v. 57, n. 2, p. 1-35, fev. 2024. DOI: 10.1145/3638240.'
                    },
                    {
                        icon: '📊',
                        title: 'Análise Comportamental Distribuída',
                        correlation: 'Estabelece metodologias para análise de padrões comportamentais anômalos, base fundamental para a detecção de spywares através de múltiplos agentes observadores.',
                        reference: '<strong>MARTINEZ, E.; KIM, S.; JONES, M.</strong> Distributed behavioral analysis for advanced persistent threat detection. <strong>IEEE Transactions on Information Forensics and Security</strong> (Revista Científica), v. 19, p. 3247-3261, ago. 2024. DOI: 10.1109/TIFS.2024.3401289.'
                    }
                ]
            }
        ]
    },
    {
        type: 'general_objective',
        title: 'Objetivo Geral',
        main_goal: 'Desenvolver uma arquitetura de <span class="highlight">Agentes de IA</span> para <span class="danger-text">Threat Hunting</span>',
        description: 'Criar um sistema inteligente e autônomo capaz de identificar, analisar e responder a ameaças de spyware em ambientes windows através da colaboração entre múltiplos agentes especializados.'
    },
    {
        type: 'specific_objectives',
        title: 'Objetivos Específicos',
        items: [
            { icon: '🎯', title: 'Modelagem de Agentes', description: 'Definir arquitetura e especialização dos agentes de IA' },
            { icon: '🛡️', title: 'Modelar Ambiente', description: 'Modelar ambiente de execução controlado para testes' },
            { icon: '🔬', title: 'Detecção Inteligente', description: 'Desenvolver e aplicar processo de identificação de spywares' },
            { icon: '📊', title: 'Avaliação de Eficácia', description: 'Validar o sistema em ambientes controlados' }
        ]
    },
    {
        type: 'hypothesis',
        title: 'Hipótese',
        statement: '"A utilização de <span class="highlight">Agentes de IA colaborativos</span> pode melhorar significativamente a capacidade de detecção e resposta a <span class="danger-text">spywares avançados</span>, superando as limitações dos métodos tradicionais através de análise comportamental distribuída e aprendizado contínuo"'
    },
    {
        type: 'hypothesis_justification',
        title: 'Justificativa da Hipótese',
        columns: [
            {
                title: 'Vantagens Teóricas',
                features: [
                    '🧠 <strong>Inteligência Distribuída:</strong> Múltiplas perspectivas de análise',
                    '🔗 <strong>Aprendizado Constante:</strong> Evolução constante do sistema',
                    '🎯 <strong>Especialização:</strong> Agentes focados em aspectos específicos',
                    '🔒 <strong>Autonomia:</strong> O sistema é autônomo e pode operar sem intervenção humana'
                ]
            },
            {
                title: 'Base Científica',
                features: [
                    '📊 <strong>Eficácia Comprovada:</strong> Sistemas multi-agente superam métodos tradicionais em 40-60% na detecção de malware <em>(Zhang et al., IEEE Transactions on Information Security, 2024)</em>',
                    '🚀 <strong>Revolução da IA:</strong> Machine Learning reduziu falsos positivos em 75% em soluções de segurança <em>(Microsoft Security Intelligence Report, 2024)</em>',
                    '⏱️ <strong>Tempo de Resposta:</strong> Google GTIG reporta que automação reduz tempo médio de detecção de 200 para 30 dias <em>(Google Cloud Blog, 2025)</em>',
                    '🔒 <strong>Ameaças Emergentes:</strong> GTIG identificou 75 zero-days em 2024, com 44% afetando tecnologias empresariais <em>(Google Threat Intelligence, 2024)</em>'
                ]
            }
        ]
    },
    {
        type: 'methodology',
        title: 'Metodologia',
        subtitle: 'Fases do Desenvolvimento',
        phases: [
            { icon: '1️⃣', title: 'Definição do Ambiente de Caça', description: 'Desenvolvimento de VM que servirá de base replicável para testes' },
            { icon: '2️⃣', title: 'Design da Arquitetura', description: 'Modelagem do sistema multi-agente' },
            { icon: '3️⃣', title: 'Implementação', description: 'Desenvolvimento dos agentes de IA' },
            { icon: '4️⃣', title: 'Treinamento', description: 'Preparação com datasets de spyware' },
            { icon: '5️⃣', title: 'Validação', description: 'Testes em ambiente controlado' },
            { icon: '6️⃣', title: 'Análise', description: 'Avaliação de resultados e melhorias' }
        ]
    },
    {
        type: 'expected_results',
        title: 'Resultados Esperados',
        columns: [
            {
                title: 'Contribuições Técnicas',
                features: [
                    '🏗️ Arquitetura inovadora de agentes especializados',
                    '🔍 Melhoria na detecção de spywares avançados',
                    '📈 Menor taxa de falsos positivos'
                ]
            },
            {
                title: 'Impactos Esperados',
                features: [
                    '🛡️ <strong>Segurança:</strong> Proteção aprimorada contra ameaças',
                    '🔬 <strong>Científico:</strong> Avanço no campo de IA em cibersegurança',
                    '🏢 <strong>Prático:</strong> Aplicabilidade em ambientes reais',
                    '📚 <strong>Acadêmico:</strong> Publicações e disseminação do conhecimento'
                ]
            }
        ]
    },
    {
        type: 'limitations',
        title: 'Limitações',
        items: [
            { title: 'Complexidade Computacional', description: 'Sistema multi-agente demanda recursos significativos de processamento' },
            { title: 'Dependência de Dados', description: 'Qualidade do treinamento depende da disponibilidade de amostras atualizadas' },
            { title: 'Evolução das Ameaças', description: 'Spywares em constante evolução podem exigir atualizações frequentes' },
            { title: 'Escopo Inicial', description: 'Foco específico em spywares, não abrangendo todo espectro de malware' }
        ],
        conclusion: 'As limitações identificadas serão endereçadas através de pesquisa contínua e refinamento iterativo do sistema proposto.'
    }
];
