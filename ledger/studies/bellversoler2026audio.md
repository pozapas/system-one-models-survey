# bellversoler2026audio — Audio System One Model: Typed Probabilistic Perception of Emotion in Speech

arXiv:2610.22401v1 [cs.SD], 14 Oct 2026; CC BY-SA 4.0; "submitted to the ICASSP" (Section 1 footnote). HTML from https://arxiv.org/html/2610.22401. Extractor: batch V15.

## Authors and affiliation
Jaime Bellver-Soler, Ivan Martin-Fernandez, Anmol Guragain, Luis Fernando D'Haro. Speech Technology and Machine Learning Group (THAU), Information Processing and Telecommunications Center, E.T.S.I. de Telecomunicacion, Universidad Politecnica de Madrid, Spain (title page). Affiliation type: academic.

## Task and data
ASOM is a new typed probabilistic model for speech: a clip plus typed questions (choice, score, yes/no) written at request time; each option becomes a criterion text scored against one audio vector; softmax per question (Section 3, Eq. 1). Trained on listener vote distributions from MSP-Podcast 2.0 Train (169k clips), CREMA-D and Emozionalmente (Section 4). Evaluation: MSP-Podcast 2.0 Dev-select (28,759 clips, 553 speakers), all systems scored on a speaker-stratified subset of 3,113 clips and a nested 1,000-clip subset; transfer to 21 unseen corpora (20,585 clips, 13 languages, up to 1,200 per corpus, 17 from EmoBox), ten with gender (10,011 clips), EmoNet-Voice Bench (4,560 synthetic clips, 38 emotions) and EARS (2,760 clips, 23 emotions) (Section 4).

## Decision model
ASOM: 6.2M-parameter reader over frozen Whisper-large-v3 and Qwen2.5-1.5B (2.2B total; 2.6B with RoBERTa-large transcript stream), three seeds averaged, 32 cross-fitted auxiliary readers (Sections 3, 4; Table 1). No version or checkpoint identifier; "Code and model weights will be publicly released upon acceptance" (Section 1 footnote). Jev is mentioned only as the TypeSafe text-only System One model with no paper (Section 2); it is not evaluated.

## Comparators and tuning budget
Fixed-class classifiers trained by the authors on MSP-Podcast (WavLM-large fine-tuned, HTSAT-CLAP MLP, DeepSER) plus emotion2vec+ large off the shelf; six zero-shot audio LLMs (Qwen2.5-Omni 3B and 7B, Qwen2-Audio-7B-Instruct, Audio Flamingo 3, Phi-4-multimodal, Voxtral-Mini-3B) given ASOM's question and option texts with lettered options, probabilities read from answer tokens; Omni-3B fine-tuned with LoRA (rank 16) on 20k and 169k clips with ASOM's targets; CLAP models (ParaCLAP, MS-CLAP, LAION CLAP) (Section 4). Zero-shot ALMs get no tuning and the fine-tuned ALM and classifiers get the same training clips; ASOM's design choices were made by ablation on the same Dev-select benchmark used for model selection (Section 4 "Evaluation data"; Section 5.4), which favours ASOM relative to untuned ALMs.

## Reference labels
Listener annotations: 8-class macro-F1 is against the majority label, LL8 against the vote distribution (primary and secondary emotions per listener); arousal, valence and dominance on 7-point scales (Section 4). Other corpora use each corpus's own labels, many acted ("the emotion an actor was asked to portray"). EmoNet-Voice is synthetic. Coded human_crowd.

## n, sampling and intervals
95% speaker-clustered bootstrap, differences paired (Section 4). Table 1 gives intervals for macro-F1; Table 2 gives none.

## Test-data exposure
MSP-Podcast, CREMA-D, EmoBox corpora, EmoNet-Voice and EARS are public datasets; their release dates are not stated. Unseen corpora are unseen by ASOM but may be in the pretraining of the frozen encoders or audio LLMs; no contamination check.

## Cost and latency
Latency of 20 questions on a 5.9 s clip, warm median, one RTX 6000 Ada: ASOM 13.1 ms (Whisper encoder 10.6 ms), ParaCLAP 7.8 ms, WavLM-L 10.6 ms, audio LLMs 230 to 545 ms (17 to 41 times ASOM), DeepSER 329 ms (Table 1, Section 5.1). A new question runs the text encoder once, 129 ms for twenty questions; criteria cached.

## Calibration
No ECE or Brier. Calibration is expressed as log loss against the listeners' votes (LL8): ASOM 1.507, class prior 1.863, zero-shot ALMs at least 2.097 (Section 5.1; Table 1). A contrastive-loss ablation worsens LL8 by 0.369 (Section 5.4). Training uses cross-fitted ensemble distillation; no post-hoc recalibration.

## Cascade or escalation
None.

## Option-name, cardinality, language and robustness tests
Synonym renaming and paraphrased descriptions (F1 -0.038), reformulated question (-0.035), names-only options (-0.063), option removal by renormalisation, eight unseen emotion words as yes/no (AUC 0.714), EmoNet-Voice and EARS emotions outside training (AUC 0.721, F1 0.018), 21 corpora in 13 languages (Sections 5.2 to 5.4). Training used paraphrased questions in half of steps. No lettered-option order test of the ALM comparators.

## Code and data
Not yet available ("upon acceptance"). Code coded as no.

## Authors' stated limitations
Closed tests on affect only; ASOM answers only what its three vote-annotated corpora cover; labels outside training are ranked well but seldom chosen; gender trails Omni-7B; transcript still matters where words carry emotion; data is the bottleneck (Section 6). Estimates describe listener judgement, not the speaker's internal state (Section 7). Acknowledgments state Claude and GPT assisted with code, literature search and writing.
