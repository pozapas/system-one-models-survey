# Facts relayed by the benchmark harness on 2026-09-24 (to be verified against the model cards before use)

- Bespoke Nimble-9B: the main branch changed on 2026-09-24 to a new checkpoint that serves at T=1.0. The old checkpoint (T=2.179) is at revision `original-2676`. The proposal's 90.12% and T=2.18 figures belong to the old checkpoint.
- Kev serves temperature-scaled probabilities by default (T=2.30 for 9B and 2.41 for 0.8B). decider-2b serves at T=1.30. Laya serves at T=1.
- the benchmark harness will send the exact commit SHAs it runs once they are pinned. The census cards must record the revision they describe.

## Revisions pinned for the benchmark run (benchmark team note, 2026-09-24 afternoon)

laya 55cf4c4e (English root plus multilingual subfolder); kev-0.8b 54f4f877 (serves T=2.3511, read from head.pt); kev-9b 2629c06a; kev code 73504e51; decider-2b d61c1c16 (T=1.30); this-that-model-1.0 3d927195 (code FLock-io/this-that-model 542d445e); Bespoke-Nimble-9B main bd792f44 (the new checkpoint served at T=1.0, base Qwen3.5-9B c2022362); comparator gaunernst/gemma-3-27b-it-int4-awq 7cf8bdc8 through vLLM. These are short SHAs; the full SHAs are in every answer record under shared/answers/.
