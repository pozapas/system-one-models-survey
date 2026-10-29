# Second rating of the survey "System One Decision Models": guide for raters

You are one of ten independent raters. Your workbook (`second_rating_R01.xlsx` to `R10.xlsx`) holds your own share of the work. Each item goes to exactly one rater, and together the ten workbooks cover the whole second literature sweep of the survey. It takes about **5 hours**, which you can split over several sittings. Please return the workbook within **two days**.

## Who should rate

Every rater should fit this profile.

- **Background.** A PhD student, postdoc or faculty member in computer science, machine learning, NLP or data science, who can read an ML evaluation paper and judge its methods. For example, they know what a held-out test set, a confidence interval, a fine-tuned model and expected calibration error are.
- **Model architectures.** Enough to tell, from a model card or a few lines of code, whether a model reads answers from a classification head, from the language-model head or by generating text.
- **Independence.** Not an author of the survey or of its companion benchmark, and not involved in preparing either. Not an employee of TypeSafe, Microsoft, MachineFi, Cloudflare or Perplexity. If you are an author of a paper in your workbook, write "conflict" in its notes column and leave it unrated; we will reassign it.

## Rules

1. Work alone. Do not discuss items with the other raters until all workbooks are returned.
2. Do not open the survey manuscript, its tables, its companion repository or any answer key. Use only the paper, model card or code linked in your workbook.
3. Fill only the yellow cells. If you cannot decide, leave the cell empty and say why in the notes column. An honest blank is better than a guess.
4. Apply the written definitions literally, even where a study seems careful or careless overall.

## Sheet 1: Inclusion (about 25 papers, 25 minutes)

Read the title and abstract, and open the arXiv link if needed. Choose **include** or **exclude**.

**Include** a paper if it reports a measured result, a documented interface or a governing method for a *typed probabilistic decision model*. That is a model that:

- takes a state (the input evidence) and a question with a finite, declared set of answers;
- returns a probability for every declared answer in one forward pass;
- does not generate free text.

Examples are TypeSafe's Jev, Microsoft-Decision-1, Trio-Spark, Clef, pplx-decider, Laya, Kev, Nimble, decider and their open reproductions. A paper that builds its own model of this kind counts, and so does a paper that uses one inside a larger system and measures it.

**Exclude** a paper that only mentions such a model in passing, or that uses "decision model" in an unrelated sense, such as a decision tree, an economic choice model or a policy network.

## Sheet 2: RiskOfBias (about 22 studies by 5 domains, about 3.5 hours)

For each study, read the methods and the main results. Rate each domain **low**, **unclear** or **high**, and write one line of justification that cites a section, table or figure of the study, for example "Table 2 gives n and 95% CIs (Sec. 4.1)".

| Domain | Low | Unclear | High |
|---|---|---|---|
| 1. Reference-label independence | human-adjudicated labels or a task outcome | a human crowd, an administrative field, or headline results that mix label types | labels from an LLM teacher, a model consensus, a synthetic procedure or the vendor |
| 2. Sampling and reporting | n stated, sampling design described and intervals on the headline results | some but not all of these | none of these, or counts that do not add up |
| 3. Version pinning and run dates | an exact model version or revision and the run dates | a version or a date but not both, or a minor version only | no version identifier for an evaluated model |
| 4. Tuning-budget parity | every compared system gets the same instructions and budget, or only one system is studied | an asymmetry that is disclosed and bounded | one system tuned on test data, or a setting chosen after seeing the results |
| 5. Test-set exposure | new or private items | public items seen only through derived features or partly public data; also a study that mixes new items with public sets released before 2026 | verbatim public benchmark items with answer keys released before 2026 and no contamination check |

Notes on the anchors:

- Labels computed exactly by a program or a simulator count as a synthetic procedure, so domain 1 is high.
- A version alias such as "jev-latest" is not a version identifier.
- If the study evaluates several decision models, rate the domain by its weakest evaluated model.

## Sheet 3: Extraction (about 30 values, 45 minutes)

These values come from the same studies you grade in Sheet 2, so the paper is already open. Each row names the location, model, dataset, metric and the exact condition (detail column). Find the number and type it in the **value** column exactly as printed: same precision and no percent sign. Do not compute, round or convert anything. If the paper prints a range or two numbers, type what is printed and explain in the notes.

## Sheet 4: Heads (3 or 4 models, 10 minutes)

Open the Hugging Face card (and the repository code if the card is silent) and choose how the model reads a probability over the declared answers:

- **a fixed slots:** a head with a fixed number of output slots, with options mapped to slots.
- **b option markers:** each option gets a marker or pointer position whose hidden state a head scores, or a small head scores all options from the final hidden states in one pass.
- **c label logits:** the option letters or label tokens are read from the language-model head, or a Yes-minus-No readout, with no separate classification head beyond an adapter.
- **d pair scoring:** each state, question and option is scored in its own pass, as a cross-encoder or NLI model.
- **e constrained decoding:** the answer is generated under a grammar or option mask.
- **undisclosed:** neither the card nor the code says.

In the **evidence** column, paste a short quote (25 words or fewer) from the card or code that supports your choice.

## When you finish

Save the workbook under its own name and send it to Amir Rafe (amir.rafe@txstate.edu). We compare your answers with ours item by item, and settle every disagreement in a short adjudication note that you may be asked to answer. The paper reports agreement for the whole team, never per rater. With your permission, raters are thanked by name in the acknowledgements.
