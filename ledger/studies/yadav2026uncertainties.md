# yadav2026uncertainties

arXiv 2610.33258v1 (cs.CL), 23 Oct 2026. "Two Uncertainties Are Not One: Disagreement versus Decision-Risk in Cheap Structured Content Moderation." Single author Karan Yadav, Google. Affiliation type: industry. Claude (Anthropic) used for background research; the author executed and verified experiments. (title block, Acknowledgments)

## Task and data
- Zero-shot toxicity classification and human-disagreement detection on Civil Comments (1.8M comments, toxicity = fraction ph of raters calling the comment toxic). Hard label y = 1[ph >= 0.5]; disagreement = binary entropy of ph. (Sec. 3)
- Run set of 142,658 comments: 119,442 middle-heavy stratified (oversampling 0.2 < ph < 0.8) plus 24,965 natural random, 1,749 shared (119,442 + 24,965 - 1,749). Base rate 0.37. A shared 56-comment probe (ph-stratified, base rate 0.59) for the 14-model frontier comparison; a paired 435-comment set for cross-model comparison (general LLM rate-limited); an out-of-distribution measuring-hate-speech set of 7,599 comments. (Sec. 3, 4.2, 4.4, 4.7)
- Reference labels: Civil Comments crowd rater fractions (human crowd); the paper states rater fractions are "a proxy for P(toxic), not ground truth". (Limitations)
- Civil Comments is public (2019) and "may overlap the model's training data"; the OOD set mitigates but does not eliminate this. (Limitations)

## Decision model
- One anonymized commercial "System One" model (the footnote says the specific product is anonymized under this name); described as a frozen typed model at about $0.042 per million input tokens with free output and 70 to 500 ms latency. No model name, version or run date; "our cached run ... fixes the exact version studied" but none is given. Not identified as Jev in the text. (Sec. 1, Limitations)
- Instrument: each comment sent once with a bundle of ten yes/no questions (primary toxic question phrased to match the annotation definition, six sub-attributes, three judgment cues: sarcasm, coded, targets_person); each answer a probability; about 596 input tokens and $0.000025 per comment. (Sec. 3)

## Comparators and tuning parity
- Lexical word list; TF-IDF logistic regression trained on the same labels (5-fold out-of-fold, 142k in-domain); gpt-oss-120b via Groq; Perspective API; Detoxify original and unbiased (in-domain); fine-tuned HateBERT; five open guard LLMs (Granite Guardian 3.0 2B, Llama Guard 3 8B, WildGuard 7B, ShieldGemma 2B and 9B, native templates). In-domain specialists are described as "contaminated". OpenAI Moderation not run (no key). (Sec. 3)
- Frontier probe: 14 reasoning models (GPT-5.x, Claude, Gemini 3.x, Grok 4.6, MAI) at high-reasoning settings, each prompted for a single JSON field with a verbalized toxicity probability; the author flags verbalized versus native probabilities as a confound for the ECE and Brier comparison. Model versions and run dates not given beyond names. The author is at Google and Gemini models are among the comparators (no competing-interest statement). (Sec. 4.2)

## Results
Full set: AUROC 0.794 (text 0.79) versus lexical 0.713 and trained TF-IDF LR 0.905. Probe (n=56): System One AUROC 0.829, ECE 0.155, Brier 0.162 versus best frontier GPT-5.6-sol 0.905, 0.050, 0.133; paired bootstrap (5,000 resamples) fails to reject parity for 13 of 14 frontier models (GPT-5.6-sol better, CI [+0.002, +0.161]); the author calls it a low-power non-separation. 435-comment paired set: System One 0.785 [0.74, 0.83], Perspective 0.954, Detoxify unbiased 0.973, HateBERT 0.947, guard LLMs 0.57 to 0.83. Disagreement detection (top-quartile entropy): native confidence AUROC 0.457, decomposition-spread of six facets 0.750, trained LR confidence 0.695. Asymmetric-loss triage: AURC 0.504 (native confidence) versus 0.542 (decomposition) versus 0.546 random, 0.417 oracle (Cfn=5, Cfp=1, Ch=0.5). OOD: AUROC 0.81, ECE 0.29, decomposition advantage not replicated (0.52). (Tables 1, 2, 4, 5; Sec. 4)

## Cost and latency
$0.000025 per comment, about 100 ms per call; 117 to 124 calls/s from one client, zero errors (one timeout) over about 150k calls; full study $3.80. Frontier costs given as tiers ($ or $$), described as lower bounds. Figure 3 caption: about 20 to 300 times lower cost. (Abstract, Sec. 4.2, 4.8)

## Calibration
ECE 0.25 overall and 0.33 on natural traffic against human fractions (bin count not stated); isotonic recalibration (5-fold out-of-fold) halves natural-traffic ECE to 0.13. Reliability curve far below the diagonal (model 0.97 versus humans 0.49). Brier reported on the probe. (Sec. 4.1, Table 2, Fig. 6)

## Cascade or escalation
Three-way policy Leave, Remove, Escalate with asymmetric costs (Cfn=5, Cfp=1, escalation cost 0.5 in the main figure); native confidence gives the best deployable AURC; across a sweep of 15 cost cells native confidence wins 12 (all with asymmetry >= 3). The author notes native confidence wins "by proxy" because of miscalibration geometry; escalating by expected decision risk on calibrated probabilities matches (0.505). Escalation is assumed to resolve to the human policy decision. (Sec. 4.5)

## Robustness
Out-of-distribution construct shift (hate speech, different platform): classification and over-confidence generalize, decomposition advantage does not. Per-item repeat SD 0.009 over five repeats. Question-decomposition alignment tests (facets versus cues). No option-name, cardinality or language tests.

## Code and data
Not available yet; the instrument, cached runs and analysis "will be released".

## Authors' limitations
Rater fractions are proxies; Civil Comments may overlap training data; OpenAI Moderation not run; in-domain specialists contaminated; costs encode a contested value choice; hand-chosen decomposition; general LLM covers only 435 comments; 56-comment probe gives noisy AUROC; one model at one point in time. (Limitations)
