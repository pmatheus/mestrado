# Strict IEEE/A1 Reference Review (2026-05-31)

Policy: prioritize IEEE and A1/A* peer-reviewed venues; verify every reference
against authoritative sources (CrossRef, DBLP, OpenAlex, ACL Anthology, PMLR,
AAAI, NeurIPS, IEEE Xplore); upgrade arXiv preprints to their published venues;
keep the 9 references already published in the MAS-Hunt article
(DOI 10.3390/engproc2026123026); retain legal/standards sources (no A1 option).

## IEEE candidate paper — mashunt/references.bib (13 entries, all verified)
Must-keep published refs retained; arXiv preprints upgraded to peer-reviewed venues:
- zhang2024breaking: arXiv 2407.20859 -> EMNLP 2025 Main (10.18653/v1/2025.emnlp-main.1771); real 7 authors.
- gu2024agent: arXiv 2402.08567 -> ICML 2024 (PMLR v235, pp 16647-16672); real 8 authors.
- huang2024resilience: arXiv 2408.00989 -> ICML 2025 (PMLR v267, pp 26202-26226); real 9 authors.
- zhan2024injecagent: arXiv 2403.02691 -> Findings of ACL 2024 (10.18653/v1/2024.findings-acl.624).
- liu2024crda: malformed @article -> @inproceedings IEEE IJCNN 2024 (10.1109/IJCNN60899.2024.10650172); full 7 authors.
- NEURIPS2024_eb113910: confirmed NeurIPS 2024 + DOI 10.52202/079017-4136.
- A1 journals verified/cleaned (full author lists): ucci2019, mcintosh2024cobit (Computers & Security), moreno2025analysis (Sensors).
- Grey/industry (must-keep, well-formed): mandiant2025mtrends, google2024zeroday, dolan-gavitt2025, verizon2025dbir
  (verizon flagged: not in published article, no A1 equivalent for breach stats — standard industry citation).
Result: paper compiles clean, 10 pp, 0 undefined.

## Dissertation — bibliografia.bib (32 entries) + shared references.bib
Upgraded arXiv -> published peer-reviewed venues:
- academia21 -> IEEE Security & Privacy 2025 (10.1109/MSEC.2024.3427640; title "Cyberdefense").
- academia11 -> IEEE ICT 2023 (10.1109/ICT60153.2023.10374044).
- bai2024 -> IEEE IIAI-AAI 2024 (10.1109/IIAI-AAI63651.2024.00073).
- vaswani2017attention -> NeurIPS 2017 (pp 5998-6008).
- arxiv250205171 (Geiping) -> NeurIPS 2025 Spotlight.
- Yuan_..._2023 -> AAAI 2023 (@inproceedings, 10.1609/aaai.v37i10.26388).
- ProAgent (DBLP:...abs-2308-11339) -> AAAI 2024 (10.1609/aaai.v38i16.29710; title "Agents").
- agashe2023llmcoordination -> Findings of NAACL 2025 (10.18653/v1/2025.findings-naacl.448).
- liu2023llm -> AAMAS 2024 (10.5555/3635637.3662979).
- doe2023emergent (BlockAgents) -> ACM TURC 2024 (@inproceedings, year fixed 2023->2024, pp 187-192).
- McIntosh2024 -> Computers & Security 2024 (A1; deduped with published version).
Incomplete IEEE entries fixed: 10616474 (IEEE ICKECS 2024), 10750987 (IEEE ICISS / ICT for Smart Society 2024; venue name corrected).
Integrity fixes:
- FGV2023 had FABRICATED placeholder authors ("Silva, João e Pereira, Ana") -> corrected to real authors
  (Goldoni, Rodrigues, Medeiros), year 2024, DOI 10.12660/cgpc.v29.90972.
- kirshteyn2024aif (SELF-PUBLISHED Amazon KDP book) REPLACED with Guo et al., "LLM Based Multi-Agents: A Survey",
  IJCAI 2024 (10.24963/ijcai.2024/890); citations updated in cap2/cap3/cap4 (key -> guo2024survey).
- academia10 reclassified to its true origin (Bromium Labs technical report, 2014), uncited.
Retained (verified live, no A1 equivalent): MarcoCivil2014, LGPD2018, Dieckmann2012, isaca2025leveraging, FGV2023.
Already strong (verified): 9791234 (IEEE Access), 10713082 (IEEE Comms Mag), 9931222 (ISCIT IEEE),
  HADDADPAJOUH201888 (Future Generation Computer Systems, A1), pmlr-v202-li23au (ICML 2023), durfee1993 (J. Intelligent Systems).
Residual arXiv-only (no published version exists — kept as clean preprints): academia20, academia22,
  qiu2024..., mahmud2025..., hillier2022..., ali2023huntgpt... .
Result: dissertation compiles clean, 79 pp, 0 undefined.

## Bottom line
No hallucinated/fabricated references remain in either document; every citation resolves to a verified
record. The candidate paper is now IEEE/A1/A* throughout (modulo the 4 must-keep industry threat reports
that have no peer-reviewed equivalent). The dissertation upgraded 11 preprints to IEEE/A*/A1 published
venues, fixed 2 incomplete IEEE entries, corrected 1 fabricated-author entry, and replaced 1 self-published
book with a peer-reviewed IJCAI survey.
