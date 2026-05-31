CrewAI-Driven Autonomous Threat Hunting: A Multi-Agent System for Enterprise Security Operations on the Elastic Stack
Paulo Matheus Nicolau Silva, Daniel Alves da Silva, Robson de Oliveira Albuquerque

Abstract: The paradigm of cybersecurity is shifting from reactive defense to proactive, autonomous operations. However, a significant gap persists between the performance of threat detection models in sandboxed environments and their efficacy on real-world endpoints. This paper introduces a novel, multi-layered architecture that operationalizes autonomous security operations by integrating a multi-agent AI system, orchestrated by the CrewAI framework, with the enterprise-grade Elastic Stack. This system features a hierarchical command structure with a strategic Governance Board of AI agents overseeing a Manager Agent, which in turn directs crews of dynamically instantiated specialist agents. These agents transform the Elastic platform into a dynamic hunting ground, leveraging live telemetry to automate the entire threat management lifecycle. The system's analytical process is formally grounded in the Diamond Model of Intrusion Analysis, enabling agents to collaboratively map adversary, capability, infrastructure, and victim components of a threat. Key innovations include the autonomous generation of Elastic detection rules, dynamic creation of investigation playbooks, and the internalization of strategic knowledge from Google Threat Intelligence reports. This research is currently being validated in a hostile, real-world Windows network environment. This paper presents the complete architecture, its theoretical foundations, and the experimental methodology designed to test a wide range of open-source and proprietary AI models, positioning the work as a significant contribution to the automatic modeling of software defenses using artificial intelligence.

1. Introduction
1.1. The Imperative for Proactive, Autonomous Defense
The contemporary cybersecurity landscape is defined by an untenable asymmetry: adversaries operate with increasing sophistication and stealth, while defense teams remain overburdened by a flood of alerts and manual processes. State-sponsored actors and commercial surveillance vendors deploy zero-day exploits with alarming frequency, and attacker dwell times within compromised networks often extend for weeks or months. This prolonged, undetected presence exposes a critical failure in traditional, reactive security models. The core problem is no longer just about detecting known threats but about proactively and autonomously hunting for the unknown, hidden adversary before significant damage occurs. This requires a fundamental shift from human-centric security operations to a model where AI agents act as autonomous, collaborative members of the security team.   

1.2. The Sandbox-to-Endpoint Gap
A major obstacle to achieving effective proactive defense is the well-documented sandbox-to-endpoint gap. Machine learning models for behavioral malware detection, which report over 90% accuracy in controlled sandbox environments, often experience a catastrophic performance drop to as low as 20-50% when deployed on live enterprise endpoints. This is due to critical factors like distribution shift, environmental variability, and sophisticated sandbox evasion techniques employed by modern malware. This gap proves that effective threat hunting cannot rely on models trained on synthetic data; it must operate on the live, noisy, and complex telemetry of real-world systems.   

1.3. A Paradigm Shift: The Autonomous Agent Crew
This paper introduces an autonomous multi-agent AI system for advanced threat hunting that directly addresses these challenges. The architecture represents a paradigm shift by combining the agentic orchestration capabilities of the CrewAI framework with the comprehensive data collection and security analytics power of the Elastic Stack. A "crew" of specialized AI agents works collaboratively within the Elastic ecosystem, treating it as both their hunting ground and their operational environment.

These agents are not merely analytical tools; they are autonomous actors. They can query live telemetry, form hypotheses, enrich findings with external threat intelligence from the Google Threat Intelligence (GTI) platform, and, most critically, take action by programmatically interacting with Elastic's REST APIs. This includes autonomously writing and deploying new detection rules, creating and managing security cases, and initiating investigation playbooks.

1.4. Technical Contributions and Conference Alignment
This research makes several novel contributions that align directly with the core themes of the Cyber-AI 2025 conference:

An Architecture for Autonomous Security Operations: A first-of-its-kind integration between the CrewAI orchestration framework and the Elastic Security platform is presented. This serves as a practical blueprint for the "automatic modeling of software... defenses using artificial intelligence," a key topic of interest for the conference.   

A Framework for AI-Driven Detection Rule Generation: The system uses behavioral analysis of live telemetry to autonomously create and deploy custom detection rules. This directly applies "deep learning techniques for modeling threats and vulnerabilities" by translating observed malicious behaviors into codified, active defenses.   

A Methodology for Proactive Vulnerability Discovery: By continuously hunting for anomalous patterns, the system embodies the use of "AI techniques for vulnerability prediction," aiming to find weaknesses and active threats before they are widely exploited.   

This paper details the technical architecture, the autonomous hunting process, and the ongoing experimental methodology.

2. State of the Art and Foundational Concepts
2.1. From Proactive Threat Hunting to Autonomous Operations
Proactive threat hunting has emerged as the new standard for mature security operations, moving beyond the limitations of reactive, alert-driven workflows. AI and ML have been central to this evolution, enabling the analysis of vast datasets to perform behavioral analysis and anomaly detection at a scale impossible for human analysts alone. Methodologies like User and Entity Behavior Analytics (UEBA) have become commonplace. However, most current AI-driven systems still serve as decision-support tools, identifying potential threats and leaving the critical tasks of rule creation, investigation, and response to human operators. The next frontier, which this work explores, is the move to fully autonomous operations, where AI agents not only detect but also act.   

2.2. Multi-Agent Systems and AI Orchestration
Multi-Agent Systems (MAS) provide a powerful paradigm for tackling complex, distributed problems like cybersecurity. Frameworks such as    

CrewAI have democratized the creation of sophisticated MAS, providing an open-source solution for orchestrating role-playing autonomous agents. CrewAI allows developers to define agents with specific roles, goals, and tools, and to manage their collaboration through structured processes (e.g., sequential, parallel, or hierarchical). This enables the creation of a cohesive "crew" where each agent contributes its specialized expertise to a larger objective, mirroring the structure of a human security operations center (SOC).

2.3. The Elastic Stack as a Unified Security Platform
Modern security operations require a unified platform that can ingest, store, and analyze data from across the enterprise. The Elastic Stack (ELK) has become an industry standard for this purpose, combining a powerful search and analytics engine (Elasticsearch) with a rich visualization and user interface (Kibana). Critically for this work, the Elastic Security solution integrates SIEM and Endpoint Security (XDR) capabilities, providing a comprehensive suite of tools for detection, investigation, and response. Elastic Agents, with their extensible set of plugins (windows, Elastic Defend, Packetbeat, osquery), can collect a vast array of live endpoint telemetry, from process execution and file system events to network traffic and low-level OS state information. This rich, real-time data stream makes the Elastic Stack the ideal environment for an autonomous threat hunting system to operate within.

3. An Architecture for Autonomous Security Operations
The proposed architecture is a practical and implementable framework designed to embed an autonomous AI agent crew directly into the Elastic Security ecosystem. The system's design is predicated on a multi-layered hierarchical structure, the seamless integration of CrewAI's orchestration logic, and the powerful data and API capabilities of the Elastic Stack.

3.1. Architectural Principles
Multi-Layered Hierarchical Governance: The system moves beyond a simple manager-worker model to a multi-layered structure. At the highest level, a Governance Board composed of multiple Governance Agents provides strategic oversight. This board directs a Manager Agent, which in turn orchestrates crews of specialist agents. This structure ensures strategic alignment, resilience, and sophisticated decision-making.   

Dynamic and Parallel Orchestration with CrewAI: The system is orchestrated by CrewAI, which manages a dynamic crew of agents. The workflow is a hybrid, combining sequential, parallel, and hierarchical processes to optimize efficiency. The Manager Agent can spawn multiple instances of the same agent type (e.g., three Threat Hunter Agents) to work in parallel on different facets of an investigation, converging their findings for a comprehensive analysis.   

Elastic as the Unified Environment: The Elastic Stack is the sole operational environment. Elasticsearch serves as the central knowledge base. Elastic Security provides the native detection engine and case management system. All agent actions are executed through secure, authenticated calls to the Elastic REST API, making the platform fully programmable.

Live Telemetry as Ground Truth: The system operates exclusively on real-time data collected by Elastic Agents. This rich data provides the ground truth for behavioral analysis, directly closing the sandbox-to-endpoint gap.   

3.2. The Autonomous Agent Crew: A Multi-Layered Hierarchy
The system is organized into three distinct layers, each with specific roles and responsibilities.

3.2.1. Layer 1: The Governance Board
At the apex of the architecture is the Governance Board, a collective of five identical Governance Agents. This board does not engage in day-to-day hunting but focuses on strategic objectives.

Role: Strategic Security Oversight Committee.

Goal: To define high-level security objectives, set threat hunting priorities, review the performance of the overall system, and ensure that the actions of the agent crews align with organizational security policy. The board makes decisions through a consensus mechanism.

Tools: Tools to review aggregated performance metrics, analyze long-term threat trends, and issue strategic directives to the Manager Agent.

3.2.2. Layer 2: The Manager Agent
This agent acts as the operational commander, translating the strategic goals from the Governance Board into tactical actions.

Role: SOC Operations Manager.

Goal: To orchestrate the crew of specialist agents to execute threat hunts. It decomposes complex tasks, delegates sub-tasks for parallel execution, and synthesizes the results from the specialist agents.

Tools: CrewAI's native delegation and task management tools.

3.2.3. Layer 3: Specialist Agents
These agents are the functional operators, spawned as needed by the Manager Agent to perform specific tasks.

Threat Hunter Agent:

Role: A senior threat hunter specializing in hypothesis-driven investigation.

Goal: To proactively search for evidence of advanced threats by forming hypotheses and querying live telemetry in Elasticsearch.

Tools: A tool that wraps the Elasticsearch Query API.

Detection Engineer Agent:

Role: A specialist in creating and tuning security detection logic.

Goal: To translate validated threat patterns into durable, automated detection rules within Elastic Security.

Tools: A tool that interacts with the Elastic Security Detections API to autonomously write, test, and deploy new detection rules.

Incident Responder Agent:

Role: A SOC coordinator responsible for managing the incident lifecycle.

Goal: To streamline the response process by creating, documenting, and managing security incidents.

Tools: A tool that uses the Elastic Security Cases API to programmatically open cases, add observables, and manage case status.

Threat Intel Agent:

Role: A cyber threat intelligence analyst.

Goal: To enrich internal findings with external context. This agent is capable of not only querying specific indicators but also reading and internalizing knowledge from full-text GTI threat reports to understand adversary TTPs and campaigns.

Tools: A tool that connects to the Google Threat Intelligence (VirusTotal) API and a tool for parsing and analyzing text from intelligence reports.

4. Analytical Framework: The Diamond Model in a Multi-Agent System
The system's analytical process is formally grounded in the Diamond Model of Intrusion Analysis, which structures threat intelligence around four core components: Adversary, Capability, Infrastructure, and Victim. Our multi-agent architecture operationalizes and extends this model.   

4.1. Operationalizing the Diamond Model
The specialist agents work in concert to populate and connect the vertices of the Diamond Model for each potential intrusion event.   

The Threat Intel Agent focuses on the Adversary and Capability vertices. By reading full GTI reports, it moves beyond simple IOCs to understand an adversary's motivations, typical TTPs, and the specific malware or exploits they employ.

The Threat Hunter Agent investigates the Infrastructure and its connection to the Victim. It queries Elastic data to identify C2 domains, malicious IP addresses, and compromised internal systems, linking them to targeted assets or users.   

The Manager Agent acts as the central analyst, synthesizing the findings from the specialist agents to construct a complete "event" in the Diamond Model. It connects the four vertices to form a coherent picture of the intrusion, creating "activity threads" by linking multiple events over time to map out an entire attack campaign.   

4.2. Extending the Model with Agentic Governance
Our architecture builds upon the Diamond Model by introducing a layer of autonomous strategic oversight. While the Diamond Model is excellent for analyzing individual intrusions, the Governance Board uses the aggregated intelligence from these analyses to inform long-term defensive strategy. It analyzes clusters of Diamond Models to identify recurring adversaries, common infrastructure patterns, or frequently exploited capabilities. Based on this strategic view, it can issue directives to the Manager Agent, such as "Prioritize hunts for TTPs associated with APT28" or "Develop a plan to harden defenses against credential dumping techniques," thus moving the organization from reactive incident analysis to proactive, intelligence-driven defense posture management.

5. Experimental Methodology and Future Work
This research is ongoing, and this paper presents the architecture and experimental design. The final results and performance metrics will be detailed in a future publication.

5.1. Test Environment
The experiments are being conducted within the Laboratório de Tecnologias da Tomada de Decisão (LATITUDE/UnB). This provides a unique and realistic testbed:

Real-World Conditions: The system is deployed on real physical machines, not virtual environments, providing authentic endpoint telemetry.

Hostile Network: The LATITUDE network is a Windows-based environment actively used by numerous students and researchers. The participants are volunteers who understand that the environment is hostile and may contain malware, and that sensitive information should not be stored on these systems. This creates a challenging and realistic environment for testing the system's detection and response capabilities against both simulated and potentially real, opportunistic threats.

5.2. AI Model Evaluation
A core objective of this research is to evaluate the performance of various Large Language Models (LLMs) as the reasoning engines for the agent crew. The modular design allows for testing a wide range of models to assess their capabilities in complex security reasoning tasks.

Open-Source and Locally-Runnable Models: The initial focus will be on models that can be run locally, ensuring data privacy and cost control. This includes models such as GLM 4.5, Kimi2, Qwen3, GPT-OSS, Llama, and Gemma.   

Proprietary and Closed-Source Models: For benchmarking purposes, the system will also be tested against leading proprietary models, including Google's Gemini-2.5-Pro, OpenAI's GPT-5, and Anthropic's Claude series (Sonnet 4, Opus 4.1, and Haiku 3). It should be noted that the extensive use of proprietary models, particularly from Anthropic, can become very expensive, and may require additional funding to be fully viable for large-scale, long-term experiments.

5.3. Future Work
The MAS-Hunt architecture serves as a robust foundation for a long-term research agenda.

Multi-Agent Reinforcement Learning (MARL): A significant advancement will be the integration of MARL to allow the entire hierarchical system to learn optimal policies autonomously. A Hierarchical MARL (H-MARL) model could be implemented, where the Governance Board learns a master policy to coordinate the sub-policies of the Manager and specialist agents, enabling adaptation to novel adversary behaviors in real time.   

Automated Response Capabilities: Future work will focus on equipping the Incident Responder Agent with a library of automated response actions that can be executed via the Elastic Agent API, such as quarantining files, terminating processes, or isolating hosts from the network.

Adversarial Resilience Testing: The system will be tested against AI-generated threats, such as those produced by frameworks like MalGEN, to evaluate its resilience in the emerging arms race of AI-driven attack and defense.   

6. Conclusion
This paper presented a novel, multi-layered architecture for an autonomous multi-agent AI system that transforms proactive threat hunting. By integrating the CrewAI orchestration framework with the Elastic Stack and grounding its analysis in the Diamond Model, we have demonstrated a practical and powerful model for automating the security operations lifecycle. The system's ability to leverage live endpoint telemetry, autonomously generate new detection rules, and operate within a strategic governance structure represents a significant advancement over traditional security postures. The ongoing research, conducted in a realistic, hostile environment, will provide crucial insights into the capabilities of modern AI models in executing complex cybersecurity tasks and will pave the way for a new generation of autonomous defense systems.

References
 First Summer School on Artificial Intelligence in Cybersecurity (Cyber-Al 2025). (2025).    

Flyer_Cyber-AI.pdf.
 Silva, P. M. N., da Silva, D. A., & Albuquerque, R. O. (2025).    

Trabalho de Metodologia em Produção Ciêntifica I. trabalho-mpc1.pdf.
 MalGEN: A Multi-Agent Framework for Realistic Malware Generation. (2025).    

Arxiv.
 A Multi-Agent Intrusion Detection System Optimized by a Deep Reinforcement Learning Approach. (2023).    

MDPI.
 Alignment of Master's Project with Cyber-AI 2025 Conference Themes. (Internal Analysis).   

 Alignment of Master's Project with Cyber-AI 2025 Conference Themes. (Internal Analysis).   

 MalGEN: A Multi-Agent Framework for Realistic Malware Generation. (2025).    

Arxiv.
 Autonomous Threat Hunting: A Future Paradigm for AI-Driven Threat Intelligence. (2024).    

Arxiv.
 A Multi-Agent System for Research with Parallel Sub-Agents. (2025).    

Anthropic Engineering.
 Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense. (2025).    

OpenReview.
 Multi Agent Systems Framework for Malware Modeling and Simulation (MASFMMS). (2008).    

ResearchGate.
 ML-Based Behavioral Malware Detection Is Far From a Solved Problem. (2025).    

Arxiv.
 Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense. (2025).    

OpenReview.
 Behavioral Model For Live Detection of Apps Based Attack. (2022).    

Arxiv.
 ML-Based Behavioral Malware Detection Is Far From a Solved Problem. (2025).    

Arxiv.
 Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense. (2025).    

CybORG CAGE 4.
 Multi-Agent Reinforcement Learning (MARL) in Cyber Defence. (2025).    

AAAI.
 Cybersecurity Intelligence Agent using CrewAI. (n.d.).    

ProjectPro.
Google Threat Intelligence: What is it and how does it work?. (n.d.). Negg.
 ML-Based Behavioral Malware Detection Is Far From a Solved Problem. (2024).    

The Moonlight.
 ML-Based Behavioral Malware Detection Is Far From a Solved Problem. (2024).    

Arxiv.
 ML-Based Behavioral Malware Detection Is Far From a Solved Problem. (2024).    

Arxiv.
CrewAI Hierarchical Manager. (2025). Medium.
 Tarallo: Evading Behavioral Malware Detectors in the Problem Space. (2025).    

Arxiv.
 Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense. (2025).    

OpenReview.
 Autonomous Threat Hunting: A Future Paradigm for AI-Driven Threat Intelligence. (2024).    

Arxiv.
 ML-Based Behavioral Malware Detection Is Far From a Solved Problem. (2025).    

Arxiv.
 Elasticsearch REST APIs. (n.d.).    

Elastic.
 AI-Driven cognitive boost for cyber threat hunting. (n.d.).    

OpenText Blogs.
 Proactive Cyber Threat Hunting With AI. (2025).    

ResearchGate.
 Multi-Agent Reinforcement Learning for Automated Cyber Defense: A Survey. (2025).    

Arxiv.
 Proactive Threat Hunting: The Vanguard of Modern Cybersecurity Defense. (2025).    

ResearchGate.
 Proactive Threat Hunting in Critical Infrastructure Protection. (2024).    

ResearchGate.
 Threat Hunting with AI: How Autonomous Systems Are Changing the Game. (2024).    

Medium.
Hierarchical Process in CrewAI. (n.d.). CrewAI Docs.
crewAI: An Open Source Multiagent Orchestration Framework. (n.d.). IBM.
Google Threat Intelligence API. (n.d.). Google Cloud Community.
 AI-Driven Threat Hunting: Proactive Cyber Defense. (n.d.).    

XenonStack.
 Threat Hunting with AI: How Autonomous Systems Are Changing the Game. (2024).    

Medium.
Understanding CrewAI: Building Multi-Agent AI Systems. (2024). Medium.
CrewAI Multi-Agent Systems Tutorial. (n.d.). Firecrawl.
Elastic Security Platform. (n.d.). Elastic.
Elastic Security Detection Rules Explorer. (n.d.). Elastic.
Elastic Security Detection Rules Repository. (n.d.). GitHub.
Elastic Security Cases API. (n.d.). Elastic.
Install Elastic Agents on Windows. (n.d.). Elastic.
Elastic Defend Integration Troubleshooting. (n.d.). Elastic.
Elastic Security Incident Response Scenario. (2022). YouTube.
Open and manage cases in Elastic Security. (n.d.). Elastic.
Elasticsearch Security API. (n.d.). Elastic.
Packetbeat Overview. (n.d.). Elastic.
Elasticsearch REST APIs. (n.d.). Elastic.
Elastic Security for SOAR. (n.d.). Elastic.
Elasticsearch Security API. (n.d.). Elastic.
Osquery in Elastic Security. (n.d.). Elastic.
How to Use Elastic APIs. (n.d.). Expedient.
Elastic for SecOps ServiceNow App. (n.d.). ServiceNow Store.
 Diamond Model of Intrusion Analysis. (n.d.).    

EC-Council.
 What is Diamond Model of Intrusion Analysis?. (n.d.).    

TeamT5.
 Diamond Model of Intrusion Analysis. (n.d.).    

Recorded Future.
 Understanding the Diamond Model of Intrusion Analysis. (n.d.).    

Threat Intelligence Lab.
 The Importance of the Diamond Model for Cyber Threat Intelligence. (n.d.).    

ThreatConnect.
 The Diamond Model of Intrusion Analysis Summary. (2020).    

Threat Intel Academy.
 GLM-4.5 Technical Report. (2025).    

Hugging Face.
 GLM-4.5: The Open-Source Model That Challenges Proprietary AI Dominance. (2025).    

UNU CRIS.
 Kimi K2 Model on GitHub. (n.d.).    

GitHub.
 Kimi K2: Open Agentic Intelligence. (n.d.).    

Moonshot AI.
 Qwen3-4B Model Card. (n.d.).    

Hugging Face.
 Qwen3 Models on Ollama. (n.d.).    

Ollama.
 Qwen3 Blog Post. (n.d.).    

QwenLM.
 gpt-oss is Phi-5. (n.d.).    

seangoedecke.com.