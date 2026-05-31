# MAS-Hunt — Dissertação de Mestrado (ABNT, PT-BR) — Outline de Coordenação

Documento de coordenação para os redatores paralelos de capítulos. Objetivo: dissertação de mestrado nível acadêmico, ABNT, em português, sobre o MAS-Hunt. O artigo IEEE/MDPI (`mashunt/camera_raedy.tex`, EN) é a semente condensada; a dissertação expande.

## Convenções compartilhadas (USAR EXATAMENTE)
- Idioma: português (PT-BR), norma ABNT. Tom acadêmico, impessoal.
- Título do sistema: **MAS-Hunt** (Multi-Agent System for Threat Hunting).
- Mecanismos de governança: **M1** (Integridade de Memória), **M2** (Validação Cruzada), **M3** (Resistência a Injeção / framework de análise OBSERVAR→HIPOTETIZAR→EVIDÊNCIA→VALIDAÇÃO-CRUZADA→CLASSIFICAR), **M4** (Monitoramento Comportamental), **M5** (Quarentena).
- Arquitetura em 3 camadas: **Conselho de Governança (Board)** → **Gerentes (Managers)** → **Trabalhadores/Caçadores (Workers/Hunters)**.
- Condições experimentais (rótulos fixos): **C1-full** (MAS-Hunt completo, M1–M5), **C1-nohardening** (ablação: framework M3 sem o endurecimento M1/M2/M4/M5), **C2-naive** (LLM de passagem única, sem governança/orquestração), **C3-Elastic** (regras de detecção padrão do Elastic Security).
- Implementação: **plugin do Claude Code** — habilidades (skills), comandos de barra (slash commands) e hooks que orquestram subagentes via capacidades nativas do Claude Code (orquestração pelo agente principal). ESTA é a contribuição central: a governança/orquestração multiagente real, não scripts isolados.
- Métricas: Precisão, Revocação (Recall), F2 (ponderada por revocação, β=2), Taxa de Falsos Positivos (FPR), Attack Success Rate (ASR/NASR); intervalos de confiança por bootstrap (B=10000, 95%).
- Citações: usar `bibliografia.bib` (ABNT) na raiz; adicionar entradas reais somente (sem fabricar). Marcar `\cite{}` apenas para chaves que existam ou criar entradas verificáveis.

## Estrutura de arquivos (criar sob `/Users/user/mestrado/dissertacao/`)
- `main.tex` — documento mestre ABNT (classe abntex2 se disponível, senão article+capa.sty da raiz), capa, sumário, `\include` dos capítulos, `\bibliography{../bibliografia}`.
- `cap1-introducao.tex`, `cap2-fundamentacao.tex`, `cap3-trabalhos-relacionados.tex`, `cap4-arquitetura.tex`, `cap5-metodologia.tex`, `cap6-resultados.tex` (placeholder p/ R3), `cap7-discussao.tex` (placeholder), `cap8-conclusao.tex`.

## Capítulos ESTÁVEIS (escrever AGORA — não dependem dos números finais)
1. **Introdução**: contexto (caça a ameaças, evasão de spyware, LOLBins, sobrecarga do analista), problema, lacuna, objetivo geral + específicos, hipótese (governança multiagente melhora resiliência a injeção adversarial vs baselines), contribuições, organização do texto.
2. **Fundamentação Teórica**: caça a ameaças e detecção comportamental; LLMs e agentes; sistemas multiagente; segurança de agentes (envenenamento de memória, injeção de prompt, amplificação de mau funcionamento); Elastic Security/Sysmon/telemetria Windows; técnicas LOLBin (MITRE ATT&CK); injeção adversarial de logs.
3. **Trabalhos Relacionados**: panorama, comparação, lacunas que o MAS-Hunt preenche.
4. **Arquitetura MAS-Hunt**: visão geral 3 camadas; papéis dos agentes; M1–M5 detalhados; framework M3; o plugin Claude Code (skills/commands/hooks) e a orquestração de subagentes pelo agente principal; protocolos de mensagens tipadas/governança.
5. **Metodologia Experimental**: laboratório (Windows Server 2025 DC + Windows 11 no domínio, Dockur/QEMU/KVM, instrumentação Sysmon+Elastic Agent+auditoria, Elastic 9.3.4); corpus de 185 playbooks LOLBin (9 famílias, malicioso vs benigno); desenho adversarial (4 modos de injeção × 3 tiers); as 4 condições; pipeline de medição (janelas por playbook, extração de telemetria, health-gate de telemetria, reprodutibilidade); métricas e análise estatística (bootstrap CI). Documentar honestamente as limitações de telemetria (lacuna EID1) e como o health-gate as mitiga.

## Capítulos que DEPENDEM dos números (placeholders agora; preenchidos em R3)
6. Resultados, 7. Discussão, 8. Conclusão — criar com estrutura/seções e marcadores `% TODO-R3: preencher com números validados` mas NÃO inventar resultados.

## Fontes para reuso (ler)
- `mashunt/camera_raedy.tex` (artigo, EN — traduzir/expandir conceitos).
- `mashunt/draft_hunting_flags_v3.tex` (definições de métricas, setup, discussão).
- `pre-projeto.tex` (proposta PT/ABNT — contexto, objetivos, motivação).
- `.orchestration/reports/research-lab.md`, `research-framework.md`, `probe-P0.md`, `R1-telemetry-fix.md` (fatos do harness, arquitetura real, pipeline).
- `bibliografia.bib`, `revisao.bib`, `mashunt/references.bib` (referências).

## Regra de integridade
NUNCA inventar números experimentais. Capítulos de resultados ficam como placeholders até R3 preencher com os dados validados do re-run v2.
