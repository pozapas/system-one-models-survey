# Value repairs, group A

Scope: the 88 rows in value_repair_A.csv. Only excerpt and location were edited, except where the Value column below shows a change (rows L1861, L2415, L3113, L2932, L3649), which also edited value and, for L3649, metric. row_id and value_key are unchanged for all 88 rows (checked against a snapshot taken before the edits). Edits were made in the parts/ledger_V*.csv files only.

Method: the quoted sentence, or the table caption followed by the header cells and that row's cells joined with " | ", was copied from the saved full text (whitespace collapsed, non-breaking and thin spaces written as ordinary spaces). Rows from 2610.14112 come from a PDF text layer whose en dashes are saved as a replacement character, so ranges in that paper are written with " ... " in place of the dash.

After merge_ledger.py and verify_excerpts.py 1.2: every row below is ok or table_ok except L3116, which is marked "derived from:" and is exempt.

| row_id | what changed | value change |
|---|---|---|
| L1240 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L1669 | excerpt replaced; Excerpt now contains the printed value. Status ok. | none |
| L1673 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L1677 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L1703 | excerpt and location replaced; The count is printed as a numeral in the Table 7 headline row (the text sentence gives it in words); Table 7 caption and row used. Status ok. | none |
| L1861 | excerpt replaced; Paper prints the count only in words ("six"); value changed to the printed word. Status ok. | 6 -> six |
| L2224 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L2253 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2347 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2415 | excerpt replaced; Paper prints the count only in words ("all eight"); value changed to the printed word. Status ok. | 8 -> eight |
| L2619 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2672 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L2673 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L2674 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2691 | excerpt replaced; Excerpt now contains the printed value. Status ok. | none |
| L2693 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2822 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2824 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2828 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2832 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2833 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2834 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2835 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2836 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2837 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2838 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2839 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2840 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2841 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2842 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2843 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2844 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2845 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2846 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2847 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2848 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2849 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2852 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2853 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2854 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2855 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2856 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2857 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2860 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2891 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L2894 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L2895 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L2896 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L2897 | excerpt and location replaced; Range printed with a dash that the saved text garbles; the excerpt elides the dash with " ... ". Value kept (signed form of the printed 0.039 to 0.127). Status ok. | none |
| L2898 | excerpt and location replaced; Derived: 1 = 10 minus the printed "9 of 10" languages where the baseline falls short; Table 6 shows Buginese as the only finite B1-LR budget. Value kept (frozen value_key counts the languages that reach Jev). Status ok. | none |
| L2900 | excerpt and location replaced; Range printed with a garbled dash; excerpt elides it with " ... ". Value kept. Status ok. | none |
| L2901 | excerpt and location replaced; Ranges printed with a garbled dash; excerpt elides them with " ... ". Value kept. Status ok. | none |
| L2902 | excerpt and location replaced; Table 8 row; range cells elided with " ... ". Status ok. | none |
| L2903 | excerpt and location replaced; Ratio range printed with a garbled dash; excerpt elides it with " ... ". Value kept. Status ok. | none |
| L2904 | excerpt and location replaced; Table 8 row; range cells elided with " ... ". Status ok. | none |
| L2909 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2910 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2911 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2912 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2914 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2915 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2916 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2917 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2927 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L2932 | excerpt and location replaced; Paper prints no numeral for zero movement ("identical"); value changed from "0 (identical)" to "identical". Status ok. | 0 (identical) -> identical |
| L3113 | excerpt replaced; Paper prints the count only in words ("ten of the fourteen"); value changed to the printed word. Status ok. | 10 -> ten |
| L3116 | excerpt and location replaced; Derived: "no Jev replies" read as 0. Value kept. Status value_not_in_excerpt. | none |
| L3270 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L3649 | excerpt and metric replaced; Value carried the answer-order labels 1 and 2 as digits; value now exactly the printed "94.28% and 95.42%", order labels moved into metric. Status ok. | 94.28 (answer order 1), 95.42 (order 2) -> 94.28% and 95.42% |
| L3751 | excerpt replaced; Excerpt now contains the printed value. Status ok. | none |
| L3831 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L3877 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L3916 | excerpt replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4455 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4456 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4457 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4458 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4809 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4810 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4812 | excerpt replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4815 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4827 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4838 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4935 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L4944 | excerpt and location replaced; Excerpt now contains the printed value. Status ok. | none |
| L5086 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L5092 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |
| L5124 | excerpt and location replaced; Caption plus header and row cells from the table. Status ok. | none |

Values changed: 5 (L1861, L2415, L3113, L2932, L3649). Rows marked "derived from:": L2898 and L3116.

