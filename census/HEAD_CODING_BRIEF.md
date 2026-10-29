# Decision-head coding brief (census version 1.2)

Every T1 original implementation of the census (first census and version 1.2) is coded by the way it reads a probability distribution over the declared options out of its backbone. The five classes are those of Figure 3 of the survey (`survey/src/f03_heads.py`, whose `CARD_PANELS` gives a coded example for each):

- `a` fixed slots: a head with a fixed number of output slots (for example 256 or 255), with options mapped to slots.
- `b` option markers or pointer: each option gets a marker or pointer position whose hidden state a head scores, or a small head scores all options from the final hidden states.
- `c` label logits: the option letters or label tokens are read from the language-model head (or a scalar Yes-minus-No readout) in one pass, with no separate trained classification head beyond an adapter.
- `d` pair scoring: each (state, question, option) is scored separately, as an NLI or cross-encoder or a sequence-classification head over pairs.
- `e` constrained decoding: the answer is generated under a grammar or option mask.
- `undisclosed`: the card and repository do not say how the distribution is read.

Each entry is coded from its own model card (`https://huggingface.co/<id>/raw/main/README.md`), from its `config.json` or code files when the card is silent, and from `cards/` or `cards/v12/` when an extracted card exists. The code carries a verbatim quote of at most 25 words that supports it, and the file it came from. A card that only claims compatibility with the hosted interface, without saying how it reads the distribution, is `undisclosed`.

Codes go to `head_check_H<n>.csv` with columns id, panel, quote, source, note.
