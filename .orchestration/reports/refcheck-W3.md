# TASK W3 — Bibliography Validation (MAS-Hunt paper)

- **Paper:** `/Users/user/mestrado/mashunt/camera_raedy.tex` → `\bibliography{references}` → `/Users/user/mestrado/mashunt/references.bib`
- **Validator:** `~/.claude/scripts/reference-check.py` (CrossRef / arXiv / OpenAlex / DOI.org, threshold-based, no LLM in loop). Raw output: `/Users/user/mestrado/.orchestration/reports/refcheck-raw.md`
- **Date:** 2026-05-28

## 1. Cite-key resolution

`camera_raedy.tex` references **11 distinct cite keys**. All 11 resolve to an entry in `references.bib` — **zero undefined citations**.

`references.bib` has **16 entries**; the **5 unused** entries are: `liu2024crda`, `louati2024intelligent`, `mcintosh2024cobit`, `smith2020gap`, `zhan2024injecagent`.

## 2. Per-cite verdict table

Verdicts come from the deterministic validator; the canonical-source column names the authority (`crossref`/`arxiv`/`openalex`) used to assert each fact.

| Cite key | Resolves in .bib? | Real publication? | Canonical src | Note |
|---|---|---|---|---|
| `dolan-gavitt2025` | Y | Y | url (HTTP 200) | Black Hat US-25 talk PDF, live. MANUAL_REVIEW (no DOI) — legitimate non-academic source. |
| `google2024zeroday` | Y | Y | url (HTTP 200) | GTIG "Hello 0-Days" blog, live. MANUAL_REVIEW — legitimate industry report. |
| `gu2024agent` | Y | Y | arxiv 2402.08567 | VERIFIED. "Agent Smith: A Single Image Can Jailbreak One Million Multimodal LLM Agents". |
| `huang2024resilience` | Y | Y (title drift) | arxiv 2408.00989 | NEEDS_FIX. arXiv ID real; canonical title is "On the Resilience of **LLM-Based Multi-Agent Collaboration with Faulty** Agents" — bib title paraphrased ("Multi-Agent Systems with Malicious Agents"). Fix title to match. |
| `mandiant2025mtrends` | Y | Y | url (HTTP 200) | M-Trends 2025, live. MANUAL_REVIEW — legitimate report. |
| `moreno2025analysis` | Y | Y | crossref 10.3390/s25010211 | VERIFIED. Sensors 2025, title/authors match. |
| `NEURIPS2024_eb113910` | Y | Y | crossref | VERIFIED. "AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases", NeurIPS 2024. (real canonical DOI 10.52202/079017-4136 exists if you want to add it.) |
| `perezmeana2023steganalysis` | Y | **N — FABRICATED** | crossref 10.3390/s23031231 | **DOI resolves to a DIFFERENT paper**: "ReinforSec: An Automatic Generator of Synthetic Malware Samples..." (Sensors 2023). The bib title "A Novel Steganalysis Method to Detect Steganographic Images of High-Embedding Rate..." returns **zero hits** on CrossRef/web/MDPI. Hallucinated title pinned to a real author cluster + wrong DOI. |
| `ucci2019` | Y | Y | crossref 10.1016/j.cose.2018.11.001 | VERIFIED. "Survey of machine learning techniques for malware analysis", Computers & Security 2019. |
| `verizon2025dbir` | Y | Y | url (HTTP 200) | 2025 DBIR, live. MANUAL_REVIEW — legitimate report. |
| `zhang2024breaking` | Y | Y | arxiv 2407.20859 | VERIFIED. "Breaking Agents: Compromising Autonomous LLM Agents Through Malfunction Amplification". |

### Unused entries (not cited; flagged for hygiene)
| Cite key | Real publication? | Note |
|---|---|---|
| `liu2024crda` | Y | VERIFIED via openalex. Unused. |
| `mcintosh2024cobit` | Y | VERIFIED via openalex (Computers & Security 2024). Unused. |
| `zhan2024injecagent` | Y | VERIFIED via arxiv 2403.02691. Unused. |
| `louati2024intelligent` | **N — likely fabricated** | NOT_FOUND. DOI `10.1016/j.eswa.2024.124653` does not resolve; title returns no hits. Unused — safe to delete. |
| `smith2020gap` | **N — likely fabricated** | NOT_FOUND. DOI `10.1109/TIFS.2020.2975849` does not resolve; "sandbox-to-endpoint gap" title returns no matching paper. Unused — safe to delete. |

## 3. Keys needing replacement / removal

1. **`perezmeana2023steganalysis` (CITED — must fix before submission).** The title is fabricated and the DOI belongs to a different paper. Options:
   - **Replace** with the real paper at that DOI — "ReinforSec: An Automatic Generator of Synthetic Malware Samples and Denial-of-Service Attacks through Reinforcement Learning" (Sensors 2023, 10.3390/s23031231) — only if that supports the sentence it backs (it is cited as an example of "specific, supervised tasks like steganalysis" — ReinforSec is RL malware generation, a poor fit), OR
   - **Substitute** a genuine CNN-steganalysis citation, OR
   - **Remove** the citation and the half-sentence example. Do NOT keep the current entry.
2. `louati2024intelligent`, `smith2020gap` — fabricated but **unused**; delete from `.bib` for hygiene (no `.tex` impact).
3. `huang2024resilience` (CITED) — real arXiv paper, only the title is paraphrased. Update the bib `title` to the canonical "On the Resilience of LLM-Based Multi-Agent Collaboration with Faulty Agents". Low severity but worth fixing for a camera-ready.

## 4. references_updated.bib switch recommendation

**Do NOT switch as-is.** `references_updated.bib` (93 entries) is **missing 2 keys that camera_raedy.tex cites**: `gu2024agent` and `ucci2019`. Switching `\bibliography{references}` → `references_updated` would produce two undefined-citation errors. It also carries the **identical fabricated `perezmeana2023steganalysis` entry** (same bad DOI/title), so it fixes nothing on the hallucination front. Recommendation: **stay on `references.bib`**, fix the 3 cited-entry issues in place. If the broader entry set is ever needed, merge `gu2024agent` + `ucci2019` into `references_updated.bib` first and fix `perezmeana2023steganalysis` there too.
