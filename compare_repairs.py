"""Controlled arithmetic comparison; never claims to reproduce 2023 labels.

Both arithmetic variants use the SAME repaired counts, adjective lists and
2026 model. Historical top-three files are compared separately as artifacts.
"""
import argparse
import json
import math
from pathlib import Path

from char_roles import positive_adj, negative_adj, read_char_adj_file
from common import write_json
from ner import calculate_mutual_information, top_adjectives


def compare(run_dir, historical_adjectives):
    import spacy

    folder = Path(run_dir)
    counts = json.loads((folder / "char_adj_dict.json").read_text(encoding="utf-8"))
    totals = {}
    for words in counts.values():
        for word, count in words.items():
            totals[word] = totals.get(word, 0) + count
    k = len(counts)
    n = sum(totals.values())
    legacy = {name: {word: round(math.log2(count * k / (sum(words.values()) * totals[word])), 5)
                     for word, count in words.items()} for name, words in counts.items()}
    fixed = calculate_mutual_information(counts)
    controlled_pmi = {"sample_space": "same 2026 pair counts", "pair_events": n, "character_keys": k,
                      "expected_fixed_minus_legacy_score": math.log2(n / k) if n else None,
                      "top_three_unchanged_same_counts_and_tie_order": top_adjectives(legacy) == top_adjectives(fixed)}
    new_top = read_char_adj_file(folder / "char_adj.txt")
    historical = read_char_adj_file(historical_adjectives)
    artifact_comparison = {"historical_top_three_rows": len(historical), "repaired_top_three_rows": len(new_top),
        "names_only_in_historical": sorted(set(historical) - set(new_top)),
        "names_only_in_repaired": sorted(set(new_top) - set(historical)),
        "common_names": {name: {"historical": historical[name], "repaired": new_top[name],
                                "same_adjectives_and_order": historical[name] == new_top[name]}
                         for name in sorted(set(historical) & set(new_top))}}
    nlp = spacy.load("en_core_web_md", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])
    seeds_pos, seeds_neg = [nlp.make_doc(w) for w in positive_adj], [nlp.make_doc(w) for w in negative_adj]
    repaired = json.loads((folder / "char_senti.json").read_text(encoding="utf-8"))
    rows = {}
    for name, words in new_top.items():
        if repaired[name]["label"] == "Unscored":
            rows[name] = {"comparison": "not_comparable_missing_vectors", "repaired_label": "Unscored"}
            continue
        pos, neg = 0, 0
        for word in words:
            doc = nlp.make_doc(word)
            pos += sum(doc.similarity(seed) for seed in seeds_pos)
            pos /= len(seeds_pos)
            neg += sum(doc.similarity(seed) for seed in seeds_neg)
            neg /= len(seeds_neg)
        old_label = "Positive" if pos > neg else "Negative" if pos < neg else "Neutral"
        rows[name] = {"legacy_arithmetic_label_on_2026_input": old_label,
                      "repaired_label": repaired[name]["label"], "label_changed": old_label != repaired[name]["label"]}
    return {"historical_artifact_comparison": artifact_comparison, "controlled_pmi_comparison": controlled_pmi,
            "controlled_sentiment_comparison": {"sample_space": "same repaired top-three lists and 2026 md model; NOT historical 2023 labels",
                "comparable_rows": sum("label_changed" in row for row in rows.values()),
                "labels_changed": sum(row.get("label_changed", False) for row in rows.values()), "rows": rows}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("historical_adjectives")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    result = compare(args.run_dir, args.historical_adjectives)
    write_json(args.report, result)
    print(result)
