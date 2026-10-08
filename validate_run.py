"""Validate saved local run artifacts without copying any full book text."""
import argparse
import json
from pathlib import Path

from char_roles import classify_sentiment, read_char_adj_file
from common import sha256, write_json
from ner import calculate_mutual_information


def validate_run(run_dir):
    import spacy

    folder = Path(run_dir)
    read = lambda name: json.loads((folder / name).read_text(encoding="utf-8"))
    summary, counts, scores, roles = [read(name) for name in
        ["run_summary.json", "char_adj_dict.json", "mutual_info_dict.json", "char_senti.json"]]
    lines = (folder / "preprocessed.txt").read_text(encoding="utf-8").splitlines()
    if not lines or any(not line.strip() or not any(c.isalpha() for c in line) for line in lines):
        raise ValueError("Empty or nontext preprocessed sentence found.")
    if len(lines) != summary["preprocessing"]["accepted_sentences"]:
        raise ValueError("Preprocessed line count does not match run summary.")
    if scores != calculate_mutual_information(counts):
        raise ValueError("Saved PMI scores are inconsistent with pair counts.")
    top = read_char_adj_file(folder / "char_adj.txt")
    if set(top) != {name for name, adjectives in scores.items() if len(adjectives) >= 3}:
        raise ValueError("Top-three filtering is inconsistent with saved scores.")
    for name, words in top.items():
        if [scores[name][word] for word in words] != sorted(scores[name].values(), reverse=True)[:3]:
            raise ValueError("Saved adjectives are not the three highest PMI scores.")
    if summary["ner"]["pair_events"] != sum(sum(a.values()) for a in counts.values()):
        raise ValueError("Pair event count mismatch.")
    if len(top) != summary["ner"]["names_with_top_three"]:
        raise ValueError("Top-three count mismatch.")
    nlp = spacy.load("en_core_web_md", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])
    if roles != classify_sentiment(top, nlp):
        raise ValueError("Saved sentiment scores are inconsistent with the tested model.")
    if summary["sentiment"] != {label: sum(r["label"] == label for r in roles.values())
                                 for label in ["Positive", "Negative", "Neutral", "Unscored"]}:
        raise ValueError("Sentiment label counts do not match run summary.")
    names = read("characters.json")
    if summary["preprocessing"]["gutenberg_wrapper_removed"]:
        text = "\n".join(lines)
        forbidden = ["Project Gutenberg", "Judith Boss", "Al Haines", "*** START OF", "*** END OF"]
        if any(term.lower() in text.lower() for term in forbidden):
            raise ValueError("Known Gutenberg wrapper/production metadata survived.")
        if any("gutenberg" in name.lower() for name in names):
            raise ValueError("Gutenberg metadata found in character candidates.")
    artifacts = [p for p in sorted(folder.iterdir()) if p.is_file()]
    return {"passed": True, "book": summary["book"], "blank_lines": 0,
            "nontext_lines": 0, "pmi_recomputed": True, "top_three_checked": True,
            "sentiment_recomputed": True, "artifact_sha256": {p.name: sha256(p) for p in artifacts}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    result = validate_run(args.run_dir)
    write_json(args.report, result)
    print(result)
