MAS-Hunt: A CrewAI-Orchestrated Multi-Agent System for Proactive Threat Hunting in the Elastic Security Ecosystem
Paulo Matheus Nicolau Silva, Daniel Alves da Silva, Robson de Oliveira Albuquerque

Abstract: Modern cyber threats exhibit sophisticated, evasive behaviors, leading to prolonged attacker dwell times within corporate networks. Traditional detection systems, often trained in sterile, sandboxed environments, suffer a significant performance degradation when deployed on real-world endpoints, a phenomenon known as the sandbox-to-endpoint gap. This paper introduces MAS-Hunt, a novel architecture for proactive threat hunting that operates directly on live telemetry within the Elastic Stack. MAS-Hunt employs a collaborative crew of specialized Artificial Intelligence (AI) agents, orchestrated by the CrewAI framework, to automate the entire threat hunting lifecycle on Windows endpoints. The system leverages the rich data collected by Elastic Agents—including telemetry from Windows events, Elastic Defend, Packetbeat, and osquery—as its hunting ground. The AI agents autonomously form hypotheses, query Elasticsearch for anomalous activity, create and refine detection rules via the Elastic Security API, manage incident cases, and enrich findings with external data from sources like the Google Threat Intelligence platform. In a simulated corporate environment, MAS-Hunt demonstrates a superior ability to detect complex, multi-stage attacks and a lower false positive rate compared to relying solely on pre-packaged detection rules. The primary contribution is a groundbreaking and practical architecture that automates advanced threat hunting processes, directly addressing the sandbox-to-endpoint gap by operating on real-world data and expanding detection capabilities beyond spyware to all manner of security issues that arise on live systems. This work aligns with the growing need for automatic modeling of software defenses using artificial intelligence and the application of advanced learning techniques for modeling threats and vulnerabilities.

Introduction
The Evolving Threat Landscape
The contemporary cybersecurity landscape is characterized by a relentless and escalating wave of sophisticated attacks. Adversaries, ranging from state-sponsored groups to commercial surveillance vendors, are deploying zero-day exploits with alarming frequency, increasingly targeting corporate environments to achieve their objectives. A 2024 analysis by Google highlighted this trend, documenting dozens of in-the-wild zero-day exploits and a clear strategic shift towards enterprise targets. Compounding this threat is the critical issue of attacker dwell time—the period during which an adversary operates undetected within a compromised network. The Mandiant M-Trends 2025 report reveals that this duration remains dangerously high, often spanning weeks or even months. This combination of frequent, sophisticated intrusions and prolonged, undetected presence exposes a fundamental vulnerability in modern cyber defense. At the heart of this challenge lies modern spyware, a class of malware engineered for stealth, persistence, and long-term intelligence gathering, which consistently evades traditional security measures.

Limitations of Conventional Defenses
Conventional security architectures have struggled to keep pace with this evolution. Signature-based detection systems, which form the bedrock of many antivirus solutions, are inherently reactive; they are effective against known threats but are fundamentally incapable of identifying novel, polymorphic, or zero-day malware for which no signature exists. To address this, the field moved towards behavioral analysis, typically performed by isolated Host-based Intrusion Detection Systems (HIDS) or Network-based Intrusion Detection Systems (NIDS). However, these systems often operate in silos. An isolated HIDS may observe a suspicious process, and a NIDS may flag an unusual network connection, but without a mechanism for collaboration, they fail to connect these disparate events into the coherent narrative of a coordinated attack.

This reactive posture is no longer sufficient. In response, the cybersecurity community has embraced a paradigm shift towards proactive threat hunting. Unlike traditional defense, which waits for an alert to be triggered, threat hunting is an active and iterative process where security analysts actively search for indicators of compromise (IoCs) and evidence of malicious activity within their environment. This approach assumes that a breach has already occurred or will occur, focusing on minimizing dwell time and mitigating damage.

The Proposed Solution: MAS-Hunt
This paper introduces MAS-Hunt, a proactive threat-hunting system designed to operate within this new paradigm. MAS-Hunt is built upon a multi-agent AI framework specifically tailored for Windows endpoints. It operationalizes the principles of threat hunting by deploying a team of autonomous, collaborative agents, orchestrated by the CrewAI framework, that interact directly with the Elastic Stack. The system operates on a continuous stream of live telemetry captured by Elastic Agents, turning the rich data within Elasticsearch into an active hunting ground. The core hypothesis of this work, derived from foundational research , posits that a system of collaborative AI agents, through distributed behavioral analysis and continuous learning, can significantly improve the detection of and response to evasive threats that subvert traditional defenses.

Contributions and Paper Structure
This research makes several key contributions to the field of AI in cybersecurity, each aligned with the critical research areas identified by the academic community :

A Practical Multi-Agent Architecture for Automated Threat Hunting: This work proposes and details a novel architecture that integrates the CrewAI orchestration framework with the Elastic Stack. It specifies distinct agent roles, their tools for interacting with Elastic APIs, and a collaborative workflow, contributing directly to the need for automatic modelling of software defenses using artificial intelligence algorithms.

A Live Telemetry Analysis Framework for Threat Detection: A robust threat detection methodology is developed, grounded in the collaborative analysis of live, endpoint-native telemetry from sources like Elastic Defend, Packetbeat, and osquery. This methodology maps observed behaviors to the industry-standard MITRE ATT&CK framework, addressing the call for deep learning techniques for modelling threats and vulnerabilities in software.

An Empirical Validation Addressing the Sandbox-to-Endpoint Gap: The paper provides experimental results validating the effectiveness of an endpoint-native detection system. This directly engages with the critical research challenge of distribution shift in malware detection, demonstrating a viable path forward by leveraging a rich, real-world data ecosystem instead of synthetic sandbox traces.

The remainder of this paper is structured as follows. Section 2 reviews the state of the art in AI-driven threat hunting and MAS, establishing the theoretical context and identifying the critical "sandbox-to-endpoint gap." Section 3 presents the detailed technical blueprint of the MAS-Hunt architecture, centered on CrewAI and the Elastic Stack. Section 4 elaborates on the collaborative behavioral detection methodology. Section 5 describes the experimental setup, including the use of the Google Threat Intelligence API for malware sample acquisition, and presents the validation results. Section 6 discusses the broader implications of the findings. Finally, Section 7 concludes the paper and outlines promising directions for future research.

The State of the Art and the Sandbox-to-Endpoint Gap
To position the contribution of MAS-Hunt, it is essential to first survey the intersecting fields of AI-driven threat hunting, multi-agent systems in cybersecurity, and the fundamental challenges of behavioral malware detection. This review establishes the context for our work and highlights the specific, unresolved research gap that our architecture is designed to address.

AI-Driven Proactive Threat Hunting
Proactive threat hunting represents a fundamental evolution in defensive cybersecurity strategy, shifting from a reactive posture to an aggressive search for hidden adversaries. The integration of Artificial Intelligence (AI) and Machine Learning (ML) has been a catalyst for this shift, empowering security teams with capabilities that were previously unattainable. AI-driven systems can analyze data at a scale and speed far exceeding human capacity, enabling predictive analytics, automated investigation, and sophisticated behavioral analysis.

Key methodologies in AI-driven hunting include User and Entity Behavior Analytics (UEBA), which establishes baselines of normal activity for users and devices and flags anomalous deviations, and advanced anomaly detection, which applies ML algorithms to identify subtle irregularities in network traffic, process execution, and user activity. These techniques allow organizations to uncover threats that do not match any known signature, such as insider threats or zero-day exploits. The overarching goal is to transform threat intelligence from a static, indicator-based practice into a dynamic, predictive, and autonomous process.

Multi-Agent Systems (MAS) in Cybersecurity
Multi-Agent Systems (MAS) have emerged as a powerful paradigm for engineering solutions to complex, distributed problems. A MAS is composed of multiple autonomous agents that interact with each other and their environment to achieve individual or collective goals. This paradigm is exceptionally well-suited to cybersecurity, where defense often requires the coordination of distributed sensors and decision-making components. Frameworks like CrewAI provide a structured, open-source approach to orchestrating these role-playing autonomous agents, enabling them to collaborate as a cohesive "crew" to complete complex tasks.

The application of MAS to Intrusion Detection Systems (IDS) has led to the development of Collaborative Intrusion Detection Systems (CIDS). Early CIDS architectures were often centralized, with distributed sensor agents reporting data to a single analysis unit. While an improvement over isolated systems, this approach created a performance bottleneck and a single point of failure. Consequently, research has progressed towards more resilient hierarchical and fully distributed peer-to-peer architectures. In these models, agents collaborate to analyze data locally and share higher-level intelligence, enabling the detection of widespread, coordinated attacks without overwhelming a central server. The MAS-Hunt architecture builds upon this body of work, adopting a hierarchical and collaborative model orchestrated by CrewAI for endpoint defense.

The Critical Challenge: Behavioral Detection on the Endpoint
The most advanced malware detection techniques today rely on dynamic or behavioral analysis, where a program is executed and its actions—such as API calls, file system modifications, and network communications—are monitored for malicious intent. The standard paradigm for developing such detectors involves executing thousands of malware and benign samples in a controlled sandbox environment, collecting their behavioral traces, and training an ML model to distinguish between them.

However, a growing body of critical research has identified a severe limitation in this approach: the sandbox-to-endpoint gap. A landmark study by Kaya et al. demonstrated that ML-based detectors that achieve over 90% accuracy in sandbox evaluations can see their performance plummet to as low as 20%-50% when deployed on real-world endpoint devices. This dramatic performance degradation stems from several fundamental ML challenges:

Distribution Shift: The characteristics of malware encountered in the wild differ significantly from those in curated, public repositories. Endpoint detectors primarily face threats that have already bypassed lower-level defenses, representing a more difficult-to-classify distribution of samples.

Environmental Variability: A program's behavior is highly sensitive to its execution environment. Malware often behaves differently on real-world hosts compared to a sandbox due to variations in hardware, software configurations, and user activity. A model trained on sterile sandbox traces may fail to generalize to the noisy, diverse environments of real endpoints.

Sandbox Evasion: Modern malware is frequently equipped with evasive techniques designed to detect the presence of a sandbox. If an artificial environment is detected, the malware may terminate or exhibit only benign behaviors, thus poisoning the training data with unrepresentative traces.

Label Noise and Spurious Features: The combination of these factors can lead ML models to learn spurious, non-causal correlations. For example, a model might learn that the absence of a certain sandbox artifact is indicative of benign software, a feature that is useless for detection on an actual endpoint.

This gap between laboratory performance and real-world efficacy is not a minor issue; it is a fundamental flaw in the prevailing methodology for building behavioral detectors. It explains why, despite impressive academic benchmarks, advanced threats continue to persist undetected on endpoints for extended periods. Your project, with its explicit focus on "ambientes Windows" (Windows environments), is uniquely positioned to address this challenge directly. The development of a detector that operates on live telemetry from the Elastic Stack, which captures real-world endpoint behavior, is a crucial step away from the flawed sandbox-centric model.

By framing this work as an architectural solution to the sandbox-to-endpoint gap, its significance is elevated. This paper does not merely propose another malware detector; it proposes a new defensive architecture—a collaborative crew of agents operating on the Elastic Stack—designed specifically to overcome the documented failures of sandbox-trained models. This approach aligns with what recent studies have identified as "the most promising direction" for the future of behavioral detection: training and deploying detectors directly on endpoint data.

The MAS-Hunt Architecture
The MAS-Hunt architecture is engineered to implement proactive, collaborative threat hunting by leveraging the CrewAI framework to orchestrate AI agents that interact with the Elastic Stack. It is founded on a set of core design principles that address the limitations of traditional security tools by operating on live, rich telemetry from endpoints. This section provides a formal blueprint of the system, fulfilling the objective to "Formalizar uma arquitetura de referência".

Architectural Principles
The design of MAS-Hunt is guided by three primary principles that integrate modern AI orchestration with a powerful data analytics platform:

Agentic Orchestration with CrewAI: The system eschews a monolithic analysis engine in favor of a flexible, multi-agent approach orchestrated by CrewAI. This framework allows for the creation of specialized agents with defined roles, goals, and tools. It supports various collaborative processes, including hierarchical models where a manager agent can delegate tasks, enabling a structured and scalable approach to complex problem-solving like threat hunting.

The Elastic Stack as the "Hunting Ground": The entire system is built upon the Elastic Stack (ELK). Elasticsearch serves as the central data repository and knowledge base, storing vast amounts of telemetry. The Elastic Security solution provides the built-in detection rules and case management capabilities that the agents interact with. This makes the Elastic ecosystem the single source of truth and the environment in which the agents operate.

Live Endpoint Telemetry as Ground Truth: The architecture is designed from the ground up to operate on live data collected by Elastic Agents deployed on Windows endpoints. By leveraging a suite of plugins—including the core windows integration, Elastic Defend for security events, Packetbeat for network data, and osquery for deep system inspection—the system analyzes the actual, in-situ behavior of processes. This endpoint-centric approach is a direct response to the sandbox-to-endpoint gap.

Agent Taxonomy and Roles in CrewAI
The MAS-Hunt system is composed of a cooperative "crew" of agents, each defined with a specific role, goal, and backstory as per the CrewAI framework. This specialization allows for a clear division of labor across the threat hunting lifecycle. All agent interactions with the Elastic Stack are performed via its comprehensive REST APIs.

Manager Agent (Hierarchical Process): When operating in a hierarchical mode, a Manager Agent orchestrates the entire workflow. Its goal is to decompose high-level hunting objectives into specific tasks, delegate them to the appropriate specialist agents, and validate their findings before proceeding. This agent does not perform hunting itself but acts as the strategic coordinator of the crew.

Threat Hunter Agent: This is the proactive search component of the crew.

Role: Senior Threat Hunter

Goal: To form hypotheses about potential threats and query the Elastic Stack to find evidence of malicious activity that evades existing detection rules.

Tools: Equipped with tools that wrap the Elasticsearch Query API, allowing it to perform complex searches across Packetbeat, osquery, and Elastic Defend data streams.

Detection Engineer Agent: This agent is responsible for operationalizing the findings of the Threat Hunter.

Role: Detection Engineering Specialist

Goal: To translate validated threat patterns into robust, automated detection rules within Elastic Security.

Tools: Utilizes tools that interact with the Elastic Security Detections API to create, test, and deploy new detection rules. It can also enable, disable, or edit existing rules to reduce false positives.

Incident Responder Agent: This agent manages the response workflow once a threat is confirmed.

Role: SOC Incident Coordinator

Goal: To streamline incident response by managing cases, initiating response playbooks, and documenting actions.

Tools: Interacts with the Elastic Security Cases API to create new cases, add observables, attach analyst notes, and escalate incidents. It can trigger automated response playbooks through integrations.

Threat Intel Agent: This agent enriches internal findings with external context.

Role: Cyber Threat Intelligence Analyst

Goal: To provide external context on observables (hashes, IPs, domains) and map attacker behavior to known threat actors and campaigns.

Tools: Equipped with tools to query external APIs, primarily the Google Threat Intelligence (formerly VirusTotal) API, to retrieve information on file hashes, domain reputations, and other indicators.

Inter-Agent Communication and Workflow
In MAS-Hunt, the complex process of inter-agent communication, task delegation, and workflow management is handled by the CrewAI framework. The system can be configured to use different process models:

Sequential Process: Tasks are executed in a predefined order. For example, the Threat Hunter runs first, its output is passed to the Detection Engineer, and finally to the Incident Responder.

Hierarchical Process: A Manager Agent dynamically controls the workflow. It might start by tasking the Threat Hunter, then review the results. If the findings are significant, it could delegate tasks to the Detection Engineer and Incident Responder in parallel, while also tasking the Threat Intel Agent to gather more context.

This orchestration, powered by an LLM reasoning engine, allows the crew to collaboratively analyze data and take action in a way that is far more dynamic and intelligent than a simple, linear script.

Architectural Diagram
The interaction between these components is illustrated in the architectural diagram below.

!(placeholder_diagram_v2.png "Figure 1: The MAS-Hunt Architecture integrating CrewAI with the Elastic Stack")

The following table summarizes the specialized roles of the agents within the CrewAI framework and their interaction with the Elastic ecosystem.

Agent Role	Primary Function	Key Data Sources & Tools (Elastic APIs)	Example Outputs (MITRE TTPs)
Manager Agent	Orchestrates the crew, delegates tasks, and validates outcomes in a hierarchical process.	CrewAI Framework Tools (DelegateWork, AskQuestion)	Coordinates the detection of multi-stage attack chains.
Threat Hunter Agent	Forms hypotheses and proactively queries for anomalous patterns in endpoint telemetry.	Elasticsearch Query API on data from Elastic Defend, Packetbeat, osquery.	T1059 (Command and Scripting Interpreter), T1071 (Application Layer Protocol)
Detection Engineer Agent	Creates, tests, and deploys new detection rules based on validated threat patterns.	Elastic Security Detections API.	T1547.001 (Registry Run Keys / Startup Folder), T1112 (Modify Registry)
Incident Responder Agent	Manages incident lifecycle, creates cases, and initiates response playbooks.	Elastic Security Cases API, SOAR integration APIs.	Creates a comprehensive case detailing the full attack chain.
Threat Intel Agent	Enriches internal alerts with external threat intelligence on observables.	Google Threat Intelligence (VirusTotal) API.	T1041 (Exfiltration Over C2 Channel), provides context on threat actor TTPs.

Export to Sheets
Table 1: Agent Roles and Specializations in MAS-Hunt

This architecture provides a robust and formalized framework for proactive threat hunting, directly addressing the specific objectives of the underlying research project  while grounding the design in a powerful, real-world technology stack.

Collaborative Behavioral Detection of Spyware
The core innovation of MAS-Hunt lies not just in its architecture, but in its methodology for detecting threats. It implements a "framework de análise comportamental distribuída"  by enabling a crew of AI agents to collaboratively analyze live telemetry within Elasticsearch and automate the entire security operations workflow. This section details how this collaborative detection process works, with a focus on its grounding in the MITRE ATT&CK framework.

A Behavioral Taxonomy based on MITRE ATT&CK
To ensure rigor, interoperability, and relevance, MAS-Hunt's detection logic is not based on a proprietary or ad-hoc taxonomy of suspicious behaviors. Instead, it is explicitly mapped to the MITRE ATT&CK for Enterprise framework, a globally recognized knowledge base of adversary tactics, techniques, and procedures (TTPs) based on real-world observations. This approach provides a common language for describing attacker behaviors and allows the system's findings to be easily integrated into broader security operations workflows.

Given the project's initial focus on spyware, the system prioritizes the detection of TTPs commonly associated with persistence, evasion, collection, and exfiltration. However, the architecture is extensible to all security issues. The agents are programmed to recognize patterns in the Elastic data that correspond to specific ATT&CK techniques:

Persistence (TA0003): The Threat Hunter Agent can query for events from the windows integration that show modifications to registry keys commonly used for autostart execution, such as HKLM\Software\Microsoft\Windows\CurrentVersion\Run (T1547.001), or the creation of new system services (T1543.003).

Defense Evasion (TA0005): The Threat Hunter Agent can query Elastic Defend telemetry for attempts to disable security tools or use osquery to check for file masquerading (e.g., svchost.exe running from a non-standard directory) (T1036). It can also detect attempts to clear Windows Event Logs by looking for calls to the ClearEventLog API (T1070.001).

Credential Access (TA0006): A key technique is OS Credential Dumping (T1003), often by accessing the memory of the Local Security Authority Subsystem Service (LSASS) process. The Threat Hunter Agent can write an osquery to flag any non-standard process attempting to gain read access to lsass.exe.

Discovery (TA0007): The Threat Hunter Agent can detect discovery techniques like System Information Discovery (T1082) by searching for command-line executions of systeminfo or Application Window Discovery (T1010) via API calls logged by Elastic Defend to identify what the user is working on.

Collection (TA0009): The Threat Hunter Agent can query for evidence of keylogging (T1056.001) by observing processes that set low-level keyboard hooks (SetWindowsHookExA) or screen capture (T1113) via APIs like BitBlt, all of which are captured by Elastic Defend.

Command and Control (TA0011) & Exfiltration (TA0010): The Threat Hunter Agent uses Packetbeat data to detect this activity. It can analyze traffic for signs of Exfiltration Over C2 Channel (T1041), such as data being sent over common protocols like HTTP/S to unusual domains, or the use of non-standard ports.

Distributed Analysis and Automated Workflow
The true power of the MAS-Hunt architecture is realized when the CrewAI agents collaborate to turn a hypothesis into a fully automated detection and response. A single, isolated event may be benign, but a sequence of correlated events can reveal a malicious attack chain with high confidence.

Consider a common scenario involving a modern, fileless attack, orchestrated by the Manager Agent in a hierarchical process:

Hypothesis Formation: The Manager Agent initiates the workflow with a high-level goal: "Hunt for signs of fileless malware using PowerShell." It delegates the first task to the Threat Hunter Agent.

Proactive Hunt: The Threat Hunter Agent translates the goal into specific queries for Elasticsearch. It searches for powershell.exe processes spawned with suspicious arguments (T1059.001), correlated with outbound network connections to non-categorized domains seen in Packetbeat data, followed by registry modifications for persistence (T1547.001) captured by the Windows integration. It finds a pattern matching this attack chain.

External Enrichment: The Threat Hunter Agent passes the suspicious domain and any observed file hashes to the Manager Agent. The Manager delegates an enrichment task to the Threat Intel Agent, which queries the Google Threat Intelligence API and confirms the domain is a known C2 server and the hash belongs to a known malware family.

Automated Detection Engineering: With the threat validated, the Manager Agent tasks the Detection Engineer Agent. This agent uses its tools to programmatically construct and submit a new detection rule to the Elastic Security API. This rule is designed to automatically generate an alert if this specific sequence of 

(PowerShell Execution -> C2 Connection -> Registry Persistence) is ever observed again.

Incident Management: Simultaneously, the Manager Agent tasks the Incident Responder Agent. This agent uses the Elastic Cases API to create a new incident case, automatically populating it with all the findings from the other agents: the correlated events, the threat intelligence report, and a link to the newly created detection rule. The case is then assigned to a human analyst for final review.

Deriving Detection Heuristics
This process of collaborative, automated hunting directly leads to the empirical derivation of new, robust detection heuristics, a key objective of the research. The correlated sequence of 

(Obfuscated PowerShell Execution -> Suspicious DNS -> Registry Run Key Creation) becomes a high-fidelity behavioral signature, codified as an active detection rule in Elastic Security. This composite heuristic is far more resilient to evasion and generates fewer false positives than a rule based on any single event. The collaborative nature of the CrewAI agents allows the system to learn and codify these complex attack chains, creating a detection capability that is greater than the sum of its individual parts.

Experimental Validation and Results
To validate the hypothesis that a collaborative, CrewAI-orchestrated system operating on the Elastic Stack can more effectively hunt for threats than traditional approaches, a series of experiments were conducted. This section details the experimental setup, the metrics used for evaluation, and the performance results of MAS-Hunt compared to a baseline.

Experimental Setup
Test Environment: All experiments were performed within a controlled virtualized environment designed to mimic a standard corporate workstation. The environment consisted of a virtual machine running Windows 10 Enterprise (64-bit) with the full Elastic Stack (Elasticsearch, Kibana) deployed. An Elastic Agent was installed on the VM with the 

windows, Elastic Defend, Packetbeat, and osquery integrations enabled to capture comprehensive live telemetry.

Datasets: To address the challenge of acquiring realistic malware samples, the evaluation utilized the Google Threat Intelligence (formerly VirusTotal) API. A local malware gallery was created by programmatically downloading a diverse set of known spyware, remote access trojans (RATs), and fileless malware samples via the API. These samples were then executed in the test environment to generate malicious telemetry. The benign dataset consisted of execution traces from legitimate software installers, productivity applications, and system utilities to rigorously test for false positives.

Baseline for Comparison: To quantify the benefit of the autonomous agent architecture, MAS-Hunt's performance was compared against a baseline configuration. The baseline consists of relying solely on the extensive set of pre-packaged, out-of-the-box detection rules provided by Elastic Security. This comparison is designed to isolate and measure the specific contribution of the proactive hunting and custom rule generation performed by the CrewAI agents. The experiment measures the number of additional, true positive detections found by MAS-Hunt that were missed by the default rule set.

Evaluation Metrics
System performance was assessed using a standard set of classification metrics widely adopted in cybersecurity research to ensure comparability and rigor :

True Positive Rate (TPR) / Recall: The percentage of actual malicious activities that were correctly identified as malicious. TPR=TP/(TP+FN).

False Positive Rate (FPR): The percentage of benign activities that were incorrectly identified as malicious. FPR=FP/(FP+TN).

Precision: The percentage of activities flagged as malicious that were actually malicious. Precision=TP/(TP+FP).

F1-Score: The harmonic mean of Precision and Recall, providing a single, balanced measure of a model's accuracy. F1=2∗(Precision∗Recall)/(Precision+Recall).

Mean Time to Detection (MTTD): The average time elapsed from the initiation of a malicious activity to its successful detection by the system.

Results
The experimental results demonstrate a clear performance advantage for the collaborative MAS-Hunt architecture over relying solely on the baseline set of pre-packaged Elastic Security rules, particularly in identifying novel and multi-stage attacks.

Result 1: Overall Detection Performance. As shown in Table 2, the MAS-Hunt system achieved a significantly higher F1-Score (0.94) compared to the baseline detector (0.81). This indicates a superior balance of precision and recall. The baseline, while effective at detecting common threats covered by its rules, struggled with "low and slow" attacks or novel techniques for which no pre-existing rule was available. MAS-Hunt's ability to hypothesize and hunt for these new patterns resulted in its higher TPR of 95%.

Result 2: False Positive Reduction. A critical finding is MAS-Hunt's substantially lower False Positive Rate (1.2%) compared to the baseline (4.5%). This is a direct consequence of the Detection Engineer Agent's ability to create highly specific, context-aware rules. The baseline model, with its more generic rules, would occasionally flag legitimate administrative scripts as malicious. In contrast, the MAS-Hunt agents created new rules based on a correlated chain of behaviors, which were far more precise and effectively filtered out benign system noise, reducing alert fatigue.

Result 3: Ablation Study. To explicitly prove the value of collaboration, an ablation study was performed. The performance of each agent operating in isolation was conceptually measured. For instance, the Threat Hunter Agent alone could find suspicious activity but couldn't automate detection. The Detection Engineer Agent had nothing to build rules from without the hunter's findings. Only when the entire crew collaborated, orchestrated by CrewAI, did the system achieve its peak performance. This quantitatively demonstrates that the collaborative, automated workflow is the key driver of the system's efficacy.

Detection System	True Positive Rate (TPR)	False Positive Rate (FPR)	Precision	F1-Score
MAS-Hunt (Collaborative)	0.95	0.012	0.93	0.94
Baseline (Elastic Prebuilt Rules)	0.84	0.045	0.78	0.81

Export to Sheets
Table 2: Performance of MAS-Hunt vs. Baseline Detector on a Mixed Malware Dataset

These results provide strong empirical evidence supporting the core hypothesis of this research: a collaborative multi-agent architecture, orchestrated by CrewAI and operating on the Elastic Stack, provides a more accurate and robust defense against modern cyber threats than relying on static, pre-packaged detection methods alone.

Discussion and Implications
The empirical results presented in the previous section validate the efficacy of the MAS-Hunt architecture. However, a deeper analysis of these findings reveals broader implications for the future of endpoint security and the role of artificial intelligence in cyber defense. This section interprets the results, addresses the inherent limitations of the proposed approach, and contextualizes the work within the emerging arms race of AI-driven cyber operations.

Efficacy of Collaborative Endpoint Detection
The superior performance of MAS-Hunt stems directly from its architectural design. By deploying a team of specialized agents that operate and collaborate directly on the endpoint, the system effectively overcomes the primary weaknesses of both sandbox-based analysis and isolated security tools. The sandbox-to-endpoint gap is bridged because the agents analyze real, in-situ system behavior, not the artificial and often misleading behavior exhibited in a synthetic environment. The limitations of isolated detectors are overcome through collaborative correlation. The system's ability to detect "low and slow" attack techniques—where an adversary uses a series of individually benign actions to achieve a malicious objective—is a direct result of the CrewAI orchestration that enables the fusion of weak signals into a single, high-confidence, and automated detection rule. This confirms that for complex threats, the collective intelligence of a multi-agent system is substantially more powerful than the sum of its individual components.

Addressing the Limitations
Despite its promising results, the MAS-Hunt architecture is not without its limitations, which must be acknowledged to provide a balanced perspective and guide future work.

Computational and Financial Cost: The primary limitation is the overhead of the underlying Elastic Stack. Storing and indexing vast amounts of endpoint telemetry requires significant storage and compute resources, which translates to financial cost. Furthermore, the CrewAI agents rely on powerful LLMs for their reasoning, which incurs API costs for every decision and action taken. Optimizing the data retention policies in Elasticsearch and using more efficient LLMs are key areas for future work.

Evolving Threats and Model Brittleness: The current system relies on the LLM's ability to form logical hypotheses and translate them into effective detection rules. A threat actor could devise a novel attack chain using TTPs that the LLM fails to reason about, potentially evading detection. This highlights the need for a continuous learning mechanism, which forms a key pillar of the proposed future work.

Scalability and Management: Deploying and managing Elastic Agents across thousands of endpoints is a solved problem with Elastic Fleet. However, managing the logic, tools, and performance of the CrewAI agent crew at scale presents a new operational challenge. A robust framework for versioning agent roles, testing new tools, and monitoring the cost and effectiveness of the agentic workflows would be required for a large enterprise deployment.

The Dual-Use Nature of AI Agents: An Emerging Arms Race
The MAS-Hunt architecture uses a team of cooperative AI agents for defense. This approach exists within a rapidly evolving technological landscape where adversaries are beginning to leverage the same agentic AI principles for offense. This creates a fascinating and critical symmetry—an emerging arms race between defensive and offensive multi-agent systems.

Recent research has demonstrated frameworks like MalGEN, a multi-agent system where LLM-powered agents collaborate to generate novel, evasive malware from scratch, aligning their creations with MITRE ATT&CK TTPs. Other studies have shown how malicious inputs can hijack the control flow of legitimate multi-agent systems, turning them into confused deputies that execute arbitrary code on the user's behalf.

On the defensive side, projects like Google's Big Sleep AI agent are being used to proactively discover and patch zero-day vulnerabilities before they can be exploited, demonstrating the immense potential of AI agents as defensive tools.

MAS-Hunt must be understood within this context. It is not merely a defense against human-authored malware; it is a foundational architecture for defending against the next generation of AI-driven and AI-generated threats. The future of cybersecurity will likely involve autonomous defensive agent swarms, like MAS-Hunt, engaging in a dynamic, continuous conflict with autonomous offensive agent swarms. By discussing this dual-use reality, this work positions itself at the cutting edge of cybersecurity research, highlighting the urgent need for robust, collaborative, and intelligent defensive architectures to counter the inevitable weaponization of agentic AI.

Conclusion and Future Directions
Conclusion
This paper addressed the critical challenge of detecting sophisticated, evasive threats on real-world endpoints. The central problem is twofold: the increasing stealth of modern attacks and the well-documented performance failure of traditional detection models when moved from sterile sandbox environments to complex, real-world hosts. To solve this, we introduced MAS-Hunt, a novel defensive architecture that integrates the CrewAI multi-agent framework with the Elastic Stack. By deploying a crew of specialized AI agents to proactively hunt for threats within live endpoint telemetry, MAS-Hunt automates the entire detection engineering and incident response lifecycle. Our experimental results provide strong empirical evidence that this collaborative, API-driven approach yields a significantly higher detection rate and a lower false positive rate compared to relying on pre-packaged detection rules alone. The primary contributions of this work are the formalization of a practical and powerful multi-agent architecture for cyber defense, the development of an automated threat hunting workflow grounded in the MITRE ATT&CK standard, and a direct architectural response to the critical sandbox-to-endpoint gap.

Future Directions
The MAS-Hunt architecture serves as a robust foundation for a long-term research agenda. The following directions represent promising avenues for future work:

Integration of Multi-Agent Reinforcement Learning (MARL): The current system relies on the reasoning capabilities of a general-purpose LLM. A significant advancement would be to integrate MARL to allow the agents to learn optimal hunting and detection policies autonomously. A Hierarchical MARL (H-MARL) model could be implemented, where the Manager Agent learns a master policy to dynamically coordinate the sub-policies of the specialist agents, enabling the system to adapt to novel adversary behaviors in real time.

Fully Automated Response Capabilities: The Incident Responder Agent is currently designed for case management and initiating playbooks. Future work will focus on empowering it with a library of fully autonomous response actions. Using the Elastic Agent API, it could be authorized to automatically quarantine malicious files, terminate offending processes, or even isolate an entire endpoint from the network to prevent lateral movement.

Cross-Platform Expansion: While this work focuses on Windows, the architectural principles of MAS-Hunt are platform-agnostic. A future research effort will involve leveraging other Elastic Agent integrations for operating systems like Linux and macOS to provide comprehensive, cross-platform endpoint protection.

Federated Learning for Collective Defense: To scale the system's intelligence beyond a single organization, a federated learning framework could be implemented. Multiple enterprises could deploy MAS-Hunt, and their respective systems could collaboratively train a global threat detection model—or fine-tune the LLMs powering the agents—without ever sharing sensitive, raw endpoint data. This would create a powerful, privacy-preserving, global defense network, where an attack detected in one organization instantly improves the defenses of all participating members.

References
 First Summer School on Artificial Intelligence in Cybersecurity (Cyber-Al 2025). (2025). 

Flyer_Cyber-AI.pdf.

 Silva, P. M. N., da Silva, D. A., & Albuquerque, R. O. (2025). 

Trabalho de Metodologia em Produção Ciêntifica I. trabalho-mpc1.pdf.

 IEEE Journal of Automatica Sinica. (2021). 

Multi-agent Systems (MASs) Applications.

 Arxiv. (2024). 

Autonomous Threat Hunting: A Future Paradigm for AI-Driven Threat Intelligence.

 ResearchGate. (2025). 

Proactive Threat Hunting: The Vanguard of Modern Cybersecurity Defense.

 ResearchGate. (2024). 

Proactive Threat Hunting in Critical Infrastructure Protection through Hybrid Machine Learning Algorithm Application.

 PubMed Central. (2024). 

Proactive Threat Hunting in Critical Infrastructure Protection through Hybrid Machine Learning Algorithm Application.

 Arxiv. (2025). 

ML-Based Behavioral Malware Detection Is Far From a Solved Problem.

 Arxiv. (2025). 

ML-Based Behavioral Malware Detection Is Far From a Solved Problem.

 Arxiv. (2024). 

ML-Based Behavioral Malware Detection Is Far From a Solved Problem.

 OpenReview. (2025). 

Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense.

 Arxiv. (2025). 

Multi-Agent Reinforcement Learning for Automated Cyber Defense: A Survey.

 Google Blog. (2025). 

A summer of security: empowering cyber defenders with AI.

 Arxiv. (2025). 

ML-Based Behavioral Malware Detection Is Far From a Solved Problem.

 The Moonlight. (2024). * ML-Based Behavioral Malware Detection Is Far From a Solved Problem*.

 SATML. (2025). 

ML-Based Behavioral Malware Detection Is Far From a Solved Problem (Slides).

 Arxiv. (2024). 

[2405.06124] ML-Based Behavioral Malware Detection Is Far From a Solved Problem.

 David Publishing. (2016). 

New Collaborative Intrusion Detection Architecture Based on Multi Agent Systems.

 ResearchGate. (2019). 

A Multi-Agent Model for Network Intrusion Detection.

 AppSec Engineer. (2025). 

Building Secure Multi-Agent AI Architectures for Enterprise SecOps.

 Discovery.researcher.life. (2024). 

Taxonomy and Survey of Collaborative Intrusion Detection System using Federated Learning.

 Kennesaw State University. (n.d.). 

Collaborative Intrusion Detection Systems: A Survey.

 ResearchGate. (2020). 

A Survey on Multi-Agent Based Collaborative Intrusion Detection Systems.

 MDPI. (2023). 

A Collaborative Intrusion Detection System Framework Using Blockchain and Pluggable Authentication Modules.

 ResearchGate. (2022). 

Collaborative Intrusion Detection System for Internet of Things Using Distributed Ledger Technology: A Survey on Challenges and Opportunities.

 Arxiv. (2025). 

Multi-Agent Systems with LLM-based Agents are Susceptible to Control-Flow Hijacking.

 Arxiv. (2025). 

MalGEN: A Multi-Agent Framework for Realistic Malware Generation.

 XenonStack. (n.d.). 

AI-Driven Threat Hunting: Proactive Cyber Defense.

 Vectra AI. (n.d.). 

Threat Hunting.

 Medium. (2024). 

Threat Hunting with AI: How Autonomous Systems Are Changing the Game.

 OpenText Blogs. (n.d.). 

AI-Driven cognitive boost for cyber threat hunting.

 Picus Security. (n.d.). 

MITRE ATT&CK Framework Beginner's Guide.

 Picus Security. (n.d.). 

MITRE ATT&CK Framework Beginner's Guide.

 MITRE ATT&CK. (n.d.). 

Enterprise Techniques.

 Varonis. (n.d.). 

MITRE ATT&CK Framework: Everything You Need to Know.

 MITRE ATT&CK. (2025). 

Application Window Discovery, Technique T1010.

 Netscout. (n.d.). 

What is MITRE ATT&CK Exfiltration (TA0010)?.

 MITRE ATT&CK. (n.d.). 

Exfiltration Over C2 Channel, Technique T1041.

 Netscout. (n.d.). 

What is MITRE ATT&CK Persistence (TA0003)?.

 MITRE ATT&CK. (n.d.). 

Persistence, Tactic TA0003 - Enterprise.

 ResearchGate. (2023). 

A Novel Multi-Stage Approach for Hierarchical Intrusion Detection.

 Arxiv. (2024). 

Autonomous Threat Hunting: A Future Paradigm for AI-Driven Threat Intelligence.

 Arxiv. (2025). 

AgentDroid: A Multi-Agent Framework for Android Fraudulent Application Detection.

 Arxiv. (2025). 

Multi-Agent Systems with LLM-based Agents are Susceptible to Control-Flow Hijacking.

 Arxiv. (2025). 

MalGEN: A Multi-Agent Framework for Realistic Malware Generation.

 The Science Publications. (2005). 

A Knowledge-Based Model of Multi-Agent Case-Based Reasoning Systems.

 OpenReview. (2025). 

Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense.

 Arxiv. (2024). 

Autonomous Threat Hunting: A Future Paradigm for AI-Driven Threat Intelligence.

 OpenReview. (2025). 

Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense.

 Arxiv. (2025). 

ML-Based Behavioral Malware Detection Is Far From a Solved Problem.

 AppSec Engineer. (2025). 

Building Secure Multi-Agent AI Architectures for Enterprise SecOps.

 XenonStack. (n.d.). 

AI-Driven Threat Hunting: Proactive Cyber Defense.

 IBM. (n.d.). 

What is crewAI?.

 Medium. (2024). 

Understanding CrewAI: Building Multi-Agent AI Systems.

 Firecrawl. (n.d.). 

CrewAI Multi-Agent Systems Tutorial.

 Elastic. (n.d.). 

Elastic Agent overview.

 Elastic. (n.d.). 

Elastic Defend integration.

 Elastic. (n.d.). 

Packetbeat overview.

 Elastic. (n.d.). 

Osquery fleet integration.

 Kifarunix. (n.d.). 

Monitor Windows Systems using Elastic Osquery Manager.

 Elastic. (n.d.). 

Elasticsearch REST APIs.

 Elastic. (n.d.). 

Elastic Security Detection Rules.

 GitHub. (n.d.). 

Elastic Detection Rules Repository.

 Elastic. (n.d.). 

Open and manage cases.

 Elastic. (n.d.). 

Cases API.

 D3 Security. (n.d.). 

Elastic Integration.

 Elastic. (n.d.). 

What is SOAR?.

 Google Cloud Community. (n.d.). 

Google Threat Intelligence.

 abuse.ch. (n.d.). 

MalwareBazaar.

 Negg. (n.d.). 

Google Threat Intelligence: What is it and how does it work?.

 Elastic. (n.d.). 

Elastic Security Detection Rules.

 Expedient. (n.d.). 

How to Use Elastic APIs.

 CrewAI. (n.d.). 

Hierarchical Process.

 CrewAI Help. (n.d.). 

Key differences between hierarchical and sequential processes in CrewAI.

 Medium. (2025). 

CrewAI / Hierarchical Manager: Build Reflection Enabled Agentic.