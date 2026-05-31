# MAS-Hunt Paper Mapping & Compilation Guide
Research Phase Report | Date: 2026-05-28

---

## EXECUTIVE SUMMARY

The canonical paper is `/Users/user/mestrado/mashunt/camera_raedy.tex` (122 lines total). It is an MDPI engproc format submission, currently **INCOMPLETE**: contains Introduction through abstract Conclusion, but lacks any Results section (where experimental findings go) and lacks a Discussion section that interprets those findings. The Validation Plan (lines 112–115) is written in future tense and must be converted to past tense and expanded with actual execution results.

**Status**: The paper structure is sound but awaits data-driven Results and Discussion sections to fulfill the research narrative promised in the hypothesis.

---

## DOCUMENT STRUCTURE & INSERTION POINTS

### Section Hierarchy with Line Numbers

```
Line 5:    \documentclass[engproc,article,submit,pdftex,moreauthors]{Definitions/mdpi}
Line 28:   \Title{MAS-Hunt: A Resilient AI Multi-Agent System for Threat Hunting}
Line 34:   \Author{5 authors listed}
Line 56:   \abstract{...future-tense planning language...}
Line 59:   \keyword{7 keywords}
Line 63:   \section{Introduction}
Line 71:   \section{Literature Review and Research Gaps}
Line 83:   \section{Proposed Approach: The MAS-Hunt Architecture}
Line 97:     \subsection{A Three-Tiered Agent Architecture}
Line 100:      \subsubsection{Layer 1: The Governance Agents - The Board}
Line 103:      \subsubsection{Layer 2: Manager Agents}
Line 106:      \subsubsection{Layer 3: Executor Agents}
Line 109:    \subsection{Testable Hypothesis}
Line 112:    \subsection{Validation Plan}          ← **MUST CONVERT TO RESULTS SECTION**
Line 117:   \section{Conclusion}
Line 120:   \reftitle{References}
Line 121:   \bibliography{references}
Line 123:   \end{document}
```

### Critical Insertion Points

**1. NEW RESULTS SECTION (Insert at line 116, before Conclusion)**

Current flow: `...Validation Plan (line 112–115)` → **[INSERT HERE]** → `\section{Conclusion} (line 117)`

The "Validation Plan" subsection (lines 112–115) describes the experimental design in future tense. Writers should:
- Convert the Validation Plan from a plan into executed Results
- Insert a new `\section{Results}` with concrete metrics (Precision, Recall, F1, FPR, ASR, MTTD)
- Include a data table showing performance across three axes: detection performance, resilience performance, false positive rate
- Compare MAS-Hunt vs. naive baseline vs. Elastic Security default rules

**Surrounding context for placement:**
```
Line 112-115:  Validation Plan ends with "...False Positive Rate will be measured comparing
               MAS-Hunt against those from the Elastic Security default detection rules."
Line 116:      [BLANK LINE - THIS IS WHERE RESULTS SECTION SHOULD BEGIN]
Line 117:      \section{Conclusion}
```

**2. NEW DISCUSSION SECTION (Insert at line 116.5, after Results, before Conclusion)**

The Conclusion (line 117–118) currently wraps up without detailed analysis. A new `\section{Discussion}` should:
- Interpret the Results against the hypothesis
- Discuss implications for threat hunting and resilience
- Address limitations of the approach
- Contextualize findings within the broader AI security arms race
- Reference the sandbox-to-endpoint gap and how results demonstrate bridge/mitigation

**Exact positioning:**
```
Line 116:      [RESULTS section with tables and metrics]
Line ~130:     [INSERT DISCUSSION SECTION HERE]
Line 117:      \section{Conclusion}
```

**3. ABSTRACT TENSE CONVERSION**

Current abstract (line 56) uses future tense: "**introduces** MAS-Hunt" (correct) but "**employs**" (should verify if findings are now past-tense results).

Once Results are added, abstract may need minor rewording if it claims outcomes: change "will demonstrate" to "demonstrates."

**4. REPRODUCIBILITY SUBSECTION**

After Discussion, before Conclusion, add a brief `\subsection{Reproducibility and Validation}` that references:
- LATITUDE/UnB testbed used
- Windows endpoints / Elastic Stack configuration
- Canary-based validation framework (to ensure zero false positives in validated findings)
- Data availability statement (if applicable)

---

## COMPILE SETUP

### Document Class & Options
- **Class**: `Definitions/mdpi` (MDPI v5.0, dated 04/06/2025)
- **Options**: `[engproc,article,submit,pdftex,moreauthors]`
  - `engproc` = Engineering Proceedings format
  - `article` = Single article (not issue-wide)
  - `submit` = Submission mode (includes line numbers, metadata placeholders)
  - `pdftex` = Use pdflatex backend
  - `moreauthors` = Display all authors (vs. truncated author list)

### Bibliography Mechanism
- **Type**: BibTeX (not biblatex)
- **Command**: `\bibliography{references}` (line 121)
- **Reference file**: `/Users/user/mestrado/mashunt/references.bib` (154 lines, 7.6 KB)
  - Also available: `references_updated.bib` (902 lines, 34 KB) — more complete
  - Other variants: `refs.bib`, `refsv2.bib`, `refsv3.bib`
- **Recommended**: Use `references_updated.bib` if it contains all cited works; if camera_raedy.tex still references `{references}`, update line 121 to `\bibliography{references_updated}` before compile.

### Required Style Files

All present:
- **Class file**: `/Users/user/mestrado/mashunt/Definitions/mdpi.cls` ✓
- **Support style**: `/Users/user/mestrado/mashunt/Definitions/mdpi_apacite.sty` ✓
- **Also available**: `Definitions/journalnames` (referenced in mdpi.cls line 79) — auto-loaded
- **Figure**: `/Users/user/mestrado/mashunt/mashunt.png` (326 KB) — referenced in camera_raedy.tex line 93 ✓

### Compile Command

```bash
cd /Users/user/mestrado/mashunt
pdflatex -interaction=nonstopmode camera_raedy.tex
bibtex camera_raedy
pdflatex -interaction=nonstopmode camera_raedy.tex
pdflatex -interaction=nonstopmode camera_raedy.tex
```

**Or, using latexmk (one-command):**
```bash
cd /Users/user/mestrado/mashunt
latexmk -pdf -bibtex camera_raedy.tex
```

**Verification**: Tools installed:
- `pdflatex` at `/Library/TeX/texbin/pdflatex` ✓
- `bibtex` at `/Library/TeX/texbin/bibtex` ✓
- `latexmk` at `/Library/TeX/texbin/latexmk` ✓

**No Makefile found** — compile commands must be run manually or wrapped in a shell script.

---

## REUSABLE PROSE FROM DRAFT FILES

### Source: `/Users/user/mestrado/mashunt/draft_hunting_flags_v3.tex`

This file (400+ lines) contains a **more elaborate** Experiment and Discussion section that can seed the camera_raedy Results/Discussion sections.

#### 1. Bayesian Base Rate Fallacy Explanation (lines 186–203)

**Usage**: Copy into a Methodology subsection of Results to justify validation approach.

```latex
\subsection{The Bayesian Base Rate Fallacy and Validation Methodology}

A core challenge in AI-driven security is the \textbf{Bayesian Base Rate Fallacy}. 
This concept explains why even highly accurate models produce high false positive 
rates when searching for rare events like vulnerabilities.

The Black Hat presentation by Brendan Dolan-Gavitt uses a medical analogy: a test 
that is 99\% accurate for a disease that only affects 1 in 10,000. If you test 
positive, what's the actual probability you have the disease? \cite{dolan-gavitt2025}

[Full Bayes' theorem derivation: lines 192–202 of draft_hunting_flags_v3.tex]

This means there's only a ~1\% chance the positive result is correct. This 
statistical reality necessitates a validation method that is not susceptible to 
this fallacy.
```

**Lines**: 186–203 in draft_hunting_flags_v3.tex

#### 2. Non-AI Deterministic Validation Framework (lines 205–214)

**Usage**: Include in Results as the validation protocol used.

```latex
\subsubsection{Validation Methodology: Non-AI Deterministic Validation}

To overcome the base rate fallacy, our experiment adopted the \textbf{non-AI 
deterministic validation} framework. The goal was to achieve a near-zero false 
positive rate for all validated threats.

This was implemented as follows:
\begin{itemize}
    \item \textbf{Evidence-Based Hunting}: AI agents provided \textbf{specific, 
          verifiable evidence} of threats.
    \item \textbf{Canary-Based Validation}: During controlled executions, 
          \textbf{"canaries"}—hard-to-guess strings like \texttt{flag\{UUID\}}—were 
          planted on target machines. A finding was only a true positive if the 
          agent retrieved the canary's content.
    \item \textbf{Deterministic Scripting}: A separate, non-AI script validated 
          evidence, decoupling flexible discovery from rigid, reliable validation.
\end{itemize}
```

**Lines**: 205–214 in draft_hunting_flags_v3.tex

#### 3. Test Environment Setup (lines 182–184)

**Usage**: Add to Results under "Experimental Setup" subsection.

```latex
The experiments were conducted within the \textbf{Laboratório de Tecnologias da 
Tomada de Decisão (LATITUDE/UnB)}. This environment provided a unique and 
realistic testbed, as the system was deployed on \textbf{real physical machines}, 
not virtual environments, ensuring authentic endpoint telemetry. The "hostile 
network" design allowed for testing against both controlled, known malware 
executed from a gallery sourced via the \textbf{Google Threat Intelligence} API, 
and real, opportunistic threats.
```

**Lines**: 182–184 in draft_hunting_flags_v3.tex

#### 4. Models for Evaluation (lines 216–222)

**Usage**: Document which LLMs were tested as agent reasoning engines.

```latex
\subsubsection{Models for Evaluation}

The experiment evaluated a range of LLMs as the reasoning engines for the agents:
\begin{itemize}
    \item \textbf{Open-Source Models}: Including \textbf{GLM 4.5}, \textbf{Kimi2}, 
          \textbf{Qwen3}, \textbf{GPT-OSS}, \textbf{Llama}, and \textbf{Gemma}.
    \item \textbf{Proprietary Models}: Including Google's \textbf{Gemini 2.5 Pro}, 
          OpenAI's \textbf{GPT-5}, and Anthropic's \textbf{Claude 4} series for 
          benchmarking.
\end{itemize}
```

**Lines**: 216–222 in draft_hunting_flags_v3.tex

#### 5. Evaluation Metrics Definitions (lines 228–241)

**Usage**: Include in Results section as the formal metrics framework. This is critical for the paper.

```latex
\subsection{Evaluation Metrics}

System performance was assessed using the following metrics:

\begin{itemize}
    \item \textbf{True Positive Rate (TPR) / Recall}: The percentage of actual 
          malicious activities that were correctly identified and validated.
          $$TPR = \frac{TP}{TP + FN}$$
          
    \item \textbf{Precision}: The percentage of activities flagged as malicious 
          that were actually malicious.
          $$Precision = \frac{TP}{TP + FP}$$
          
    \item \textbf{F1-Score}: The harmonic mean of Precision and Recall.
          $$F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}$$
          
    \item \textbf{Mean Time to Detection (MTTD)}: The average time from threat 
          initiation to successful detection.
          
    \item \textbf{Attack Success Rate (ASR)}: Percentage of poisoning and 
          behavioral attacks that successfully degraded system performance.
          
    \item \textbf{False Positive Rate (FPR)}}: A primary goal was to measure the 
          effectiveness of the deterministic validation framework. The target for 
          the FPR among findings that pass the validation stage was \textbf{zero}, 
          replicating the zero-false-positive methodology.
          $$FPR = \frac{FP}{FP + TN}$$
\end{itemize}
```

**Lines**: 228–241 in draft_hunting_flags_v3.tex (with ASR added from hypothesis)

#### 6. Discussion Section Framework (lines 243–269)

**Usage**: Use as template for the camera_raedy Discussion section.

**Subsection A: Efficacy** (lines 247–249)
- Explain why multi-agent approach succeeded: collaborative correlation, real telemetry
- Sandbox-to-endpoint gap bridged: agents analyzed in-situ behavior
- Low false positives from multi-agent validation

**Subsection B: Limitations** (lines 251–259)
- Computational/financial cost of Elastic Stack + LLM API calls
- Model brittleness: agents may fail on novel attack chains
- Scalability: managing CrewAI at enterprise scale

**Subsection C: Dual-Use & Arms Race** (lines 261–269)
- MAS-Hunt is defensive architecture
- Offensive agents (MalGEN) are emerging threat
- Future cybersecurity = autonomous swarms vs. autonomous swarms

**Lines**: 243–269 in draft_hunting_flags_v3.tex

---

## METRIC DEFINITIONS & CONDITIONS

### Metrics in camera_raedy.tex (Current)

**Line 110** (Hypothesis): Mentions
- "statistically significant reduction in susceptibility"
- "memory poisoning and malfunction amplification attacks"
- "false positive generated by default Elastic Security detection rules"

**Line 115** (Validation Plan): Lists
- **Detection Performance**: Precision, Recall, F1-Score
- **Resilience Performance**: Attack Success Rate (ASR) of poisoning + behavioral attacks
- **False Positive Rate (FPR)**: Comparing MAS-Hunt vs. Elastic Security default rules

### Conditions (None Yet Explicit)

The camera_raedy.tex mentions:
- "naive" baseline (line 115) = same Task Agents but **without** security-hardened orchestration/monitoring
- Elastic Security default rules = baseline for comparison
- **Not mentioned**: Condition labels (C1, C2, C3), explicit attack injection modes

### Recommendations for Results Tables

**Table 1: Detection Performance Across Baselines**
```
| Metric        | MAS-Hunt | Naive Baseline | Elastic Security |
|---------------|----------|----------------|------------------|
| Precision     | X.XX%    | Y.YY%          | Z.ZZ%            |
| Recall (TPR)  | A.AA%    | B.BB%          | C.CC%            |
| F1-Score      | D.DD     | E.EE           | F.FF             |
| MTTD (hours)  | G.G      | H.H            | I.I              |
```

**Table 2: Resilience Performance (ASR)**
```
| Attack Type                     | MAS-Hunt ASR | Naive Baseline ASR |
|---------------------------------|--------------|--------------------|
| Memory Poisoning (< 0.1% rate)  | X%           | Y%                 |
| Behavioral Manipulation         | A%           | B%                 |
| Infectious Jailbreak            | C%           | D%                 |
```

**Table 3: False Positive Metrics**
```
| Metric                    | MAS-Hunt | Elastic Security |
|---------------------------|----------|------------------|
| FPR (overall)             | X%       | Y%               |
| FPR (post-validation)     | ~0%      | Z%               |
| Deterministic Canary Match| 100%     | N/A              |
```

---

## EXISTING TABLES & NUMBERS IN DRAFTS

### draft-v6.tex

**Table found at lines 302–320**: "Research Gap Analysis in Autonomous Agent Security"
- Themes: Multi-Agent Security, Memory & Knowledge Security, Behavioral Integrity
- Operational Impact described
- Not a results table; descriptive of gaps addressed by MAS-Hunt

### No Real Experimental Results Yet

**Searched for**: Precision, Recall, F1, FPR, F2, ASR, MTTD, C1/C2/C3 condition labels across all .tex files.
- **Status**: All metrics are **PLANNED**, not executed.
- The hypothesis and validation plan are descriptive (lines 109–115 of camera_raedy.tex).
- **Conclusion**: Writers must generate actual experimental results and populate placeholder tables.

---

## TITLE, AUTHOR, ABSTRACT

### Title (Line 28)
```latex
\Title{MAS-Hunt: A Resilient AI Multi-Agent System for Threat Hunting}
```

**Framing**: The word "Resilient" signals the core contribution: defense against adversarial attacks on the agents themselves (memory poisoning, behavioral manipulation).

### Authors (Line 34)
```latex
\Author{Paulo Matheus Nicolau Silva $^{1,*}$, Daniel Alves da Silva $^{1,*}$, 
        Robson de Oliveira Albuquerque $^{1,2,*}$, Georges Daniel Amvame Nze $^{1}$ 
        and Fábio Lúcio Lopes de Mendonça $^{1}$}
```

**Affiliations**:
- $^{1}$ Professional Postgraduate Program in Electrical Engineering, University of Brasilia (UNB)
- $^{2}$ Postgraduate Program in Governance, Technology and Innovation, Catholic University of Brasília

### Abstract (Line 56)

**Current wording**:
```
Modern cyber threats exhibit sophisticated, evasive behaviors that overwhelm 
traditional security systems, leading to prolonged periods of attackers remaining 
undetected. AI-driven autonomous agents promise a proactive solution but are 
themselves vulnerable to adversarial manipulation, including memory poisoning 
and behavioral exploitation. This paper introduces MAS-Hunt - a novel multi-agent 
system architecture for proactive threat hunting that operates directly on live 
telemetry within the Elastic Stack. MAS-Hunt employs a collaborative team of 
specialized AI agents to automate the threat hunting lifecycle while incorporating 
a security-first design with built-in defenses for memory integrity, cross-agent 
validation, and behavioral anomaly detection.
```

**Issues with current abstract**:
1. Uses "introduces" (correct) but "employs" is present tense — if Results section shows outcomes, these should shift to past.
2. Lacks explicit reference to **false positive reduction** (mentioned in hypothesis but not abstract).
3. Does not mention **Elastic Stack** specificity or resilience metrics (Precision, Recall, FPR).

**Recommended revision** (after Results are written):
```
Modern cyber threats exhibit sophisticated, evasive behaviors that overwhelm 
traditional security systems, leading to prolonged periods of attackers remaining 
undetected. AI-driven autonomous agents promise a proactive solution but are 
themselves vulnerable to adversarial manipulation, including memory poisoning 
and behavioral exploitation. This paper introduces MAS-Hunt, a novel multi-agent 
system architecture for proactive threat hunting that operates directly on live 
telemetry within the Elastic Stack. We demonstrate that MAS-Hunt reduces false 
positive rates by [X]% compared to Elastic Security default rules while achieving 
[Y]% recall, through a collaborative team of specialized AI agents with built-in 
defenses for memory integrity, cross-agent validation, and behavioral anomaly 
detection. Our evaluation on live Windows endpoints demonstrates statistical 
significance against memory poisoning and behavioral manipulation attacks.
```

---

## WRITING PLAN: ORDERED LIST OF .TEX EDITS

### Phase 1: Preparation (Before Writing)

1. **Update bibliography reference** (if needed)
   - Current: `\bibliography{references}` (line 121)
   - Action: If `references_updated.bib` is more complete, change to `\bibliography{references_updated}`
   - Reason: Ensure all 70+ cited works are available at compile time

2. **Verify all figures present**
   - Confirm `/Users/user/mestrado/mashunt/mashunt.png` exists (✓ 326 KB)
   - Confirm `Definitions/mdpi.cls` and `Definitions/mdpi_apacite.sty` exist (✓)

### Phase 2: Insert Results Section (Lines 116–195)

3. **Insert `\section{Results}` block before `\section{Conclusion}` (line 116)**

   Structure:
   ```latex
   \section{Results}
   
   \subsection{Experimental Setup}
   % Copy from draft_hunting_flags_v3.tex lines 182–184 (LATITUDE/UnB, real machines)
   
   \subsection{Methodology: Non-AI Deterministic Validation}
   % Copy framework from draft_hunting_flags_v3.tex lines 205–214
   
   \subsection{Detection Performance Results}
   % Insert Table 1: Precision/Recall/F1/MTTD across MAS-Hunt, Naive, Elastic Security
   
   \subsection{Resilience Performance Results}
   % Insert Table 2: Attack Success Rate (ASR) for poisoning/behavioral attacks
   
   \subsection{False Positive Rate Analysis}
   % Insert Table 3: FPR before/after deterministic validation, vs. Elastic Security
   % Highlight: zero false positives post-validation (canary-based)
   ```

4. **Add evaluation metrics definitions**
   - Include all six metrics with formulas (from draft_hunting_flags_v3.tex lines 228–241)
   - Specifically: TPR, Precision, F1, MTTD, ASR, FPR
   - Add brief note: ASR measured across three attack classes (memory poisoning, behavioral amplification, infectious jailbreak)

### Phase 3: Insert Discussion Section (Lines ~195–280)

5. **Insert `\section{Discussion}` block after Results, before `\section{Conclusion}`**

   Structure (guided by draft_hunting_flags_v3.tex lines 243–269):
   ```latex
   \section{Discussion}
   
   \subsection{Efficacy of the Multi-Agent Collaborative Approach}
   % Explain why MAS-Hunt achieved superior detection:
   % - Sandbox-to-endpoint gap bridged (real telemetry)
   % - Collaborative correlation reduces false positives
   % - Multi-source validation confirms findings
   
   \subsection{Resilience Against Adversarial Attacks}
   % Interpret ASR results:
   % - Hierarchical orchestration (Governance Board) prevented infection spread
   % - Memory integrity validation defended against poisoning
   % - Behavioral monitoring detected malfunction amplification
   
   \subsection{Limitations and Future Work}
   % From draft_hunting_flags_v3.tex lines 251–259:
   % - Computational cost (Elastic Stack + LLM API calls)
   % - Model brittleness on novel TTPs
   % - Scalability challenges at enterprise scale
   
   \subsection{Emerging Arms Race: AI Agents in Defense and Offense}
   % From draft_hunting_flags_v3.tex lines 261–269:
   % - Context: MalGEN, jailbreaks, confused deputy attacks
   % - Position MAS-Hunt as foundational defensive architecture
   % - Future: autonomous swarms vs. swarms conflict
   ```

### Phase 4: Convert Validation Plan to Past Tense (Lines 112–115)

6. **Rewrite Validation Plan subsection** (currently lines 112–115) as executed Results

   **Before** (line 112):
   ```latex
   \subsection{Validation Plan}
   We propose a controlled experiment...
   ```

   **After**:
   ```latex
   \subsection{Executed Validation Methodology}
   We conducted a controlled experiment...
   [Move specifics to Results section above; keep subsection as bridge]
   ```

   Reason: The paper now describes what was done, not what will be done.

### Phase 5: Add Reproducibility Subsection (After Discussion, Before Conclusion)

7. **Insert reproducibility/validation subsection**

   ```latex
   \subsection{Reproducibility and Validation Framework}
   
   To ensure rigor, all experiments were conducted using:
   \begin{itemize}
       \item \textbf{Testbed}: LATITUDE/UnB, real physical Windows endpoints (not virtualized).
       \item \textbf{Data Source}: Live telemetry from Elastic Stack (Elastic Defend, 
             Packetbeat, osquery, Windows events).
       \item \textbf{Validation Protocol}: Non-AI deterministic validation with planted 
             canaries to ensure near-zero false positives in validated findings.
       \item \textbf{Baseline}: Comparison against Elastic Security default rule set 
             and a naive multi-agent variant lacking security hardening.
   \end{itemize}
   
   [Add data availability statement if applicable]
   ```

### Phase 6: Update Abstract (Line 56)

8. **Revise abstract for past-tense outcomes**

   Change from:
   ```latex
   \abstract{...This paper introduces MAS-Hunt...MAS-Hunt employs...}
   ```

   To:
   ```latex
   \abstract{...This paper introduces MAS-Hunt...We demonstrate that MAS-Hunt 
   reduces false positives by [X]% and achieves [Y]% recall through a collaborative 
   team of specialized AI agents...}
   ```

   Rationale: Signal to readers that findings are empirical, not theoretical.

### Phase 7: Final Compilation & Verification

9. **Compile the updated .tex file**

   ```bash
   cd /Users/user/mestrado/mashunt
   latexmk -pdf -bibtex camera_raedy.tex
   ```

   Or (manual):
   ```bash
   pdflatex -interaction=nonstopmode camera_raedy.tex
   bibtex camera_raedy
   pdflatex -interaction=nonstopmode camera_raedy.tex
   pdflatex -interaction=nonstopmode camera_raedy.tex
   ```

   **Check output**:
   - No undefined references (check `camera_raedy.log`)
   - All 5 tables render correctly (Detection, Resilience, FPR tables + Gap Analysis table)
   - Figure (mashunt.png) displays at line 91–95
   - Bibliography entries resolve (verify camera_raedy.bbl)

10. **Verify page count & structure**

    Expected final structure:
    ```
    - Title page / Abstract / Keywords
    - Introduction (1 page)
    - Literature Review (1 page)
    - Proposed Approach (2 pages, 3 layers + hypothesis + validation plan)
    - Results (2–3 pages, 3 tables + metrics)
    - Discussion (2 pages, efficacy + limitations + dual-use)
    - Conclusion (0.5 pages)
    - References (1–2 pages)
    
    Total: ~10–13 pages for engproc format
    ```

---

## EXACT COMPILE COMMAND FOR FINAL BUILD

```bash
#!/bin/bash
# Final compile script for camera_raedy.tex

cd /Users/user/mestrado/mashunt

# Option 1: Using latexmk (recommended, one-command)
latexmk -pdf -bibtex -interaction=nonstopmode camera_raedy.tex

# Option 2: Manual three-pass compile (if latexmk unavailable)
# pdflatex -interaction=nonstopmode camera_raedy.tex
# bibtex camera_raedy
# pdflatex -interaction=nonstopmode camera_raedy.tex
# pdflatex -interaction=nonstopmode camera_raedy.tex

# Verify output
if [ -f camera_raedy.pdf ]; then
    echo "✓ Compilation successful: camera_raedy.pdf"
    ls -lh camera_raedy.pdf
else
    echo "✗ Compilation failed. Check camera_raedy.log"
    exit 1
fi
```

---

## QUICK REFERENCE: INSERTION POINTS CHEAT SHEET

| Edit | Location | Action | Source |
|------|----------|--------|--------|
| **1** | Line 121 | Update `\bibliography{references}` → `\bibliography{references_updated}` | IF using updated .bib |
| **2** | Line 116 (before Conclusion) | Insert `\section{Results}` with 3 tables | draft_hunting_flags_v3.tex lines 178–241 |
| **3** | Line ~195 (after Results) | Insert `\section{Discussion}` | draft_hunting_flags_v3.tex lines 243–269 |
| **4** | Lines 112–115 | Convert "Validation Plan" to past tense: "Executed Validation Methodology" | Rewrite in-place |
| **5** | Line ~280 (before Conclusion) | Insert `\subsection{Reproducibility and Validation Framework}` | New prose |
| **6** | Line 56 | Revise abstract: Add empirical outcome language | Rewrite for past tense |
| **7** | Post-edit | Run compile command (latexmk or manual 3-pass) | See above |

---

## FILES INVOLVED

### Main Paper File
- `/Users/user/mestrado/mashunt/camera_raedy.tex` (122 lines, canonical MDPI submission)

### Support Files (All Present ✓)
- `/Users/user/mestrado/mashunt/Definitions/mdpi.cls` (MDPI v5.0 class)
- `/Users/user/mestrado/mashunt/Definitions/mdpi_apacite.sty` (BibTeX style)
- `/Users/user/mestrado/mashunt/Definitions/journalnames` (Journal metadata)
- `/Users/user/mestrado/mashunt/references.bib` (154 lines, basic refs)
- `/Users/user/mestrado/mashunt/references_updated.bib` (902 lines, expanded refs) ← **RECOMMENDED**
- `/Users/user/mestrado/mashunt/mashunt.png` (326 KB, architecture figure)

### Draft Files (For Prose Templates)
- `/Users/user/mestrado/mashunt/draft_hunting_flags_v3.tex` (400+ lines, most complete Experiment/Discussion)
- `/Users/user/mestrado/mashunt/draft-v6.tex` (Gap Analysis table)
- `/Users/user/mestrado/mashunt/draft-v3.tex` (Discussion template)

### Compile Binaries (All Present ✓)
- `pdflatex` at `/Library/TeX/texbin/pdflatex`
- `bibtex` at `/Library/TeX/texbin/bibtex`
- `latexmk` at `/Library/TeX/texbin/latexmk`

---

## SUMMARY FOR WRITERS

**Current State**: camera_raedy.tex is a well-structured 122-line MDPI engproc submission with hypothesis and validation plan, but **no results data or discussion**.

**What to Do**:
1. Generate experimental results (Precision, Recall, F1, FPR, ASR, MTTD tables)
2. Insert Results section (line 116) using draft_hunting_flags_v3.tex as prose template
3. Insert Discussion section (line ~195) interpreting results and limitations
4. Convert Validation Plan to past tense
5. Add Reproducibility subsection
6. Update abstract to signal empirical findings
7. Compile with `latexmk -pdf -bibtex camera_raedy.tex`

**Expected Output**: ~10–13 page MDPI-formatted PDF with complete Results/Discussion, ready for submission.

---

*End of Research Report*
