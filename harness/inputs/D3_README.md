# D3: human-labelled CSS classification tasks

The D3 texts are not included in this repository, because their licenses do not grant redistribution (see `DATA_LICENSES.md`). `d3_item_ids.json` lists the item identifiers of every D3 condition. Run `src/s00b_prepare_d3.py` and then `src/s00_freeze_inputs.py` to rebuild the frozen files, and check each against its digest in `manifest.json`.

Four text-classification tasks drawn from the Ziems et al. (2024) "Can Large
Language Models Transform Computational Social Science?" (CSS) collection
(SALT-NLP/LLMs_for_CSS), with question and option wording taken from the
Ibrahim and Zaki (2026) replication package for arXiv 2609.24574,
"Evaluating Decision Models for Text Annotation in Computational Social
Science."

Two binary tasks and two multi-class tasks, so the option-name swap
experiment has binary questions to work with. All four are among the 18
tasks Ibrahim and Zaki report, so results here are directly comparable to
theirs.

## Replication package

- URL: https://github.com/hazemibrahim97/decision-models-css
- Commit: `311956c2d1096cabc0f09a1f248e7dc0e1c0c41e`
- License: MIT (covers the package's code; the task datasets themselves
  belong to their original creators per the package's own README)
- Question and option wording were read from `pilot_jev.py` at that commit
  (`parse_prompt`, `task_criteria`, `OPTION_TO_GOLD`, `BINARY_CRITERIA`),
  which is the exact code Ibrahim and Zaki used to build the Jev requests.
  We copied that logic by hand into a standalone script rather than
  importing `pilot_jev.py`, because importing it reads
  `~/.config/openrouter/api_key` at module load time.
- Underlying task data: the package reads `LLMs_for_CSS/css_data/<task>/test.json`,
  cloned from SALT-NLP/LLMs_for_CSS. We fetched the same files directly from
  that repository, commit `55183a64d7faaf6d5fc23eddf2bfc48ece4cacad`
  (no license file in that repo; task datasets carry their own upstream
  licenses, given per task below).
- Per-task Jev metrics below that are not printed in the paper's main text
  were read from the package's own derived CSVs,
  `analysis/cell_metrics.csv` and `analysis/calibration_cis.csv`, at the
  same commit, and are labelled as such rather than attributed to the paper.

## Task selection and a deviation from the mirror design

We originally considered `discourse` (Reddit CMV discourse acts, Coarse
Discourse corpus) as a multi-class task. We dropped it under the "only an
ID or hydration route exists -> skip" rule: the upstream Coarse Discourse
release (google-research-datasets/coarse-discourse) ships only thread/post
IDs, structure, and discourse-act labels, not the post text; its own
README says so explicitly and ships a separate script that re-pulls each
post's text from the live Reddit API to reconstruct the full item. Ziems
et al.'s `test.json` already contains that hydrated text, but the task
itself is ID-only at the source, which is the condition the task
instructions say to skip on. (`emotion`'s source, `dair-ai/emotion`, does
not have this problem: the tweet text itself, not just an ID, is what
upstream ships.) We substituted `wiki_politeness`, a 3-class
Wikipedia-talk-page task that is one of Ibrahim and Zaki's 15 headline
evaluation tasks (not a pilot task, unlike `discourse`), with a
CC BY 4.0 source that ships full text directly.

## Tasks

### conv_go_awry (binary)

- Source: Wikipedia "Conversations Gone Awry" corpus, distributed via
  ConvoKit. Zhang, Chang, Danescu-Niculescu-Mizil, Dixon, Hua, Thain, and
  Taraborelli, "Conversations Gone Awry: Detecting Early Signs of
  Conversational Failure," ACL 2018.
  https://convokit.cornell.edu/documentation/awry.html
- License: no separate license is stated on the ConvoKit page; the
  underlying text is Wikipedia talk-page content (CC BY-SA). We could not
  find an explicit corpus-level license statement beyond that; flagging
  this rather than asserting a specific license we did not see.
- Split: Ziems et al.'s released `test.json` (already a class-stratified
  sample of at most 500 items).
- n = 500. Label distribution: True 250, False 250.
- Question (fixed across items, one distinct prompt verified; unlike
  `wiki_corpus`, this instruction does not name a participant):
  `"Will the previouse conversation eventually derail into a personal
  attack?"` (the misspelling "previouse" is in the package's own prompt
  text and is kept verbatim).
- Option keys: `"True"` / `"False"`, with descriptions `"True: the previous
  conversation eventually derails into a personal attack."` and `"False:
  the previous conversation does not eventually derail into a personal
  attack."`, exactly as in `BINARY_CRITERIA` in the replication package.
- `positive`: `"True"` (the conversation derails). The task's instruction
  asserts the derailment outcome, matching the "sarcastic" /
  "yes"-style convention of naming the asserted condition as positive; the
  classes are balanced, so this is a semantic choice, not a prevalence one.
- Jev per-task result: macro-F1 = 50.2 (paper Table 1, row "Toxicity", the
  conversation-level toxicity-prediction task in Section 3.1's task list),
  n = 500. From the package's `analysis/cell_metrics.csv`: accuracy =
  0.572, macro-F1 = 0.50153 (matches Table 1 at ×100, rounding), ECE
  (on Jev's returned confidence) = 0.3017, ECE on the chosen option's
  probability = 0.34238, Brier = 0.71654. Paper Section 4.4 separately
  reports accuracy on the confidence-≥0.9 subset for this task ("toxicity
  prediction 0.611"), matching `acc0.9` in the CSV.

### wiki_corpus (binary)

- Source: Wikipedia Talk Pages Corpus / "Echoes of Power," distributed via
  ConvoKit. Danescu-Niculescu-Mizil, Lee, Pang, and Kleinberg, "Echoes of
  Power: Language Effects and Power Differences in Social Interaction,"
  WWW 2012. https://convokit.cornell.edu/documentation/wiki.html
- License: CC BY-SA 4.0 (stated on the ConvoKit dataset page).
- Split: Ziems et al.'s released `test.json`.
- n = 500. Label distribution: True 250, False 250.
- Question (per item, names the user): `"Based on the conversation is
  <user> in a position of power?"`.
- Option keys: `"True"` / `"False"`, descriptions `"True: the named user is
  in a position of power in the conversation."` / `"False: the named user
  is not in a position of power in the conversation."`, verbatim from
  `BINARY_CRITERIA`.
- `positive`: `"True"` (the named user holds power) for the same reason as
  above: it is the asserted condition in the question, and the classes are
  balanced.
- Jev per-task result: macro-F1 = 58.1 (paper Table 1, row "Power"), n =
  500. From `analysis/cell_metrics.csv`: accuracy = 0.610, macro-F1 =
  0.58126, ECE = 0.23284, ECE on top-option probability = 0.24836, Brier =
  0.60893. Paper Section 4.4 separately reports accuracy on the
  confidence-≥0.9 subset for this task ("Wikipedia corpus power 0.644"),
  which is a routing-curve figure (matches `acc0.9` in the CSV), not the
  overall accuracy or ECE above.

### emotion (6-class)

- Source: Saravia, Liu, Huang, Wu, and Chen, "CARER: Contextualized Affect
  Representations for Emotion Recognition," EMNLP 2018 (the
  `dair-ai/emotion` dataset). Twitter-derived, six Ekman emotions.
- License: dataset card states "for educational and research purposes
  only."
- Split: Ziems et al.'s released `test.json`.
- n = 498. Label distribution: A 83, B 83, C 83, D 83, E 83, F 83 (perfectly
  balanced).
- Question (fixed across items, one distinct prompt verified): `"If a
  mental health professional saw the above text, what emotion would they
  categorize it to be (using the following six basic emotions according to
  Paul Ekman)?"`.
- Option keys are the package's own letter labels `"A"`.."F"`, since the
  dataset's gold labels are the letters themselves rather than named
  emotions; kept as-is for comparability with the replication package.
  `option_desc`: A "Fear", B "Anger", C "Joy", D "Sadness", E "Love", F
  "Surprise".
- `positive`: `null` (multi-class).
- Jev per-task result: macro-F1 = 48.4 (paper Table 1, row "Emotion"),
  n = 498. From `analysis/cell_metrics.csv`: accuracy = 0.494, macro-F1 =
  0.48358, ECE = 0.28124, ECE on top-option probability = 0.32112, Brier =
  0.75210.

### wiki_politeness (3-class)

- Source: Stanford Politeness Corpus (Wikipedia requests), distributed via
  ConvoKit. Danescu-Niculescu-Mizil, Sudhof, Jurafsky, Leskovec, and Potts,
  "A Computational Approach to Politeness with Application to Social
  Factors," ACL 2013.
  https://convokit.cornell.edu/documentation/wiki_politeness.html
- License: CC BY 4.0 (stated on the ConvoKit dataset page).
- Split: Ziems et al.'s released `test.json`.
- n = 498. Label distribution: 1 (Polite) 166, 0 (Neutral) 166, -1
  (Impolite) 166.
- Question (fixed across items): `"Based on formal workplace social norms,
  which of the following best describes the above conversation?"`.
- Option keys are the package's numeric gold codes as strings, `"1"`,
  `"0"`, `"-1"`, matching `OPTION_TO_GOLD["wiki_politeness"]`.
  `option_desc`: "1" "Polite", "0" "Neutral", "-1" "Impolite".
- `positive`: `null` (multi-class).
- Jev per-task result: macro-F1 = 57.3 (paper Table 1, row "Politeness",
  Section 4.1), n = 498. From `analysis/cell_metrics.csv`: accuracy =
  0.608, macro-F1 = 0.57296, ECE = 0.10092, ECE on top-option probability =
  0.13884, Brier = 0.52942. This is the task on which Jev's calibration
  error is lowest among the four tasks here.

## Sampling

Seed 20260924. Ziems et al.'s released `test.json` for each task is
already a class-stratified sample of at most 500 items (this is stated in
the Ibrahim and Zaki paper, Section 3.1), and every task here has n ≤ 500
(500, 500, 498, 498). The seeded draw therefore selects every available
item; the seed fixes only a deterministic per-label shuffle-then-concatenate
write order, not which items are included. No further stratification was
needed since no class is rare in any of the four tasks (all four are
perfectly or near-perfectly balanced).

## Rebuilding from source

`shared/src/s00b_prepare_d3.py` rebuilds all four `.jsonl` files and
`manifest.json` byte-for-byte from the two pinned public GitHub commits
above, over plain HTTP, with no local state. Verified to reproduce the
checked-in files' exact SHA-256 hashes on this workstation; it is written
to run the same way in a fresh Linux environment (e.g. a Colab notebook)
with only `requests` installed.

## Fields

Each line of `<task>.jsonl` has: `id` (the item id from Ziems et al.'s
`test.json`), `task`, `text` (the state string, i.e. `context[id]`, kept
verbatim), `gold` (the option key of the correct answer), `options`
(ordered list of option keys), `option_desc` (dict from key to
description, in the replication package's wording), `question` (the
instruction text, kept verbatim, including per-item substitutions such as
the named Wikipedia user or spelling artifacts like "previouse"), `binary`
(true for `conv_go_awry` and `wiki_corpus`, false for `emotion` and
`wiki_politeness`), and `positive` (the option key of the marked/asserted
class for binary tasks, `"True"` for both of ours; `null` for multi-class
tasks).

## Option-key naming and a note for the swap script

`conv_go_awry` and `wiki_corpus` use `"True"` / `"False"` as their option
keys rather than task-specific pairs like "derails"/"does_not_derail". This
is deliberate, not a default: `"True"` and `"False"` are the replication
package's own gold label names (`BINARY_CRITERIA` keys them this way) and
the exact criteria keys Jev was given in the original study, so keeping
them lets the unswapped baseline run here be compared directly against the
package's and the paper's Table 1 numbers for these two tasks.

This has one consequence the option-name swap script must handle. Every
binary option description in this dataset restates its own key at the
front of the text, e.g. `"True": "True: the previous conversation
eventually derails into a personal attack."` and `"False": "False: the
named user is not in a position of power..."`. If the swap script renames
the keys (e.g. `"True"` -> `"yes"`) without also rewriting or stripping
that leading `"<Key>: "` fragment from each description, the swapped
option's description will still assert the original key's name and
contradict the new key, confounding the swap manipulation. The swap script
should either strip the `"^<OldKey>:\s*"` prefix before renaming, or
regenerate the sentence from scratch rather than doing a bare key
substitution.

## Deviations from the package's exact text

- `discourse` was dropped and `wiki_politeness` substituted, for the
  redistribution reason given above.
- Option descriptions were right-stripped of a single trailing space that
  the package's own `parse_prompt` regex artifact leaves on the last
  option line of a prompt (e.g. `"Surprise "` -> `"Surprise"`,
  `"Impolite "` -> `"Impolite"`); no other whitespace or content was
  changed.
- The package's prompts append a `"Constraint: ..."` line instructing the
  model to answer with only the option letter/word. This is not a
  deviation: the package's own `parse_prompt` (which we reproduced
  verbatim) already discards this line when building the `instructions`
  text sent to Jev (`elif line.startswith("Constraint:"): cur = None`), so
  our `question` field matches what Jev itself was given. The TypeSafe
  wire format has no field for output-format instructions in any case; the
  criteria/options themselves enforce the closed answer set.
- For `wiki_corpus`, the instruction line is not identical across items
  (it names the conversation's participant), so `question` varies
  row-by-row for that task. For `conv_go_awry`, `emotion`, and
  `wiki_politeness` we verified there is exactly one distinct prompt
  string across all items before treating the question as task-fixed (all
  three are in fact identical row to row in the output).
