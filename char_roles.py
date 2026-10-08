"""2026 repair: average static-vector similarity to course-provided seeds."""
import argparse
import math
from pathlib import Path

from common import write_json

positive_adj = ["good", "amazing", "happy", "trustworthy", "friendly"]
negative_adj = ["bad", "angry", "evil", "stubborn", "disgusting"]


def read_char_adj_file(file_path):
    result = {}
    for number, line in enumerate(Path(file_path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        name, separator, rest = line.partition(":")
        name, adjs = name.strip(), rest.split()
        if not separator or not name or len(adjs) != 3 or name in result:
            raise ValueError(f"Invalid or duplicate character-adjective record on line {number}.")
        result[name] = adjs
    return result


def mean_similarity(adjectives, seeds):
    if not adjectives or not seeds:
        raise ValueError("Cannot average an empty collection.")
    return math.fsum(adj.similarity(seed) for adj in adjectives for seed in seeds) / (len(adjectives) * len(seeds))


def classify_sentiment(char_adj_dict, nlp):
    # Single-word Doc vectors do not need tagging/NER; use the same md vectors.
    make_doc = nlp.make_doc if hasattr(nlp, "make_doc") else nlp
    seeds_pos, seeds_neg = [make_doc(a) for a in positive_adj], [make_doc(a) for a in negative_adj]
    if any(doc.vector_norm == 0 for doc in seeds_pos + seeds_neg):
        raise ValueError("A sentiment seed has no vector in this model.")
    result = {}
    for name, words in char_adj_dict.items():
        docs = [make_doc(word) for word in words]
        missing = [word for word, doc in zip(words, docs) if doc.vector_norm == 0]
        if not docs or missing:
            result[name] = {"label": "Unscored", "adjectives": words,
                            "positive_score": None, "negative_score": None,
                            "missing_vectors": missing, "reason": "empty_adjectives" if not docs else "missing_vectors"}
            continue
        pos, neg = mean_similarity(docs, seeds_pos), mean_similarity(docs, seeds_neg)
        if not math.isfinite(pos) or not math.isfinite(neg):
            raise ValueError("Non-finite sentiment similarity.")
        label = "Neutral" if math.isclose(pos, neg, rel_tol=0, abs_tol=1e-12) else "Positive" if pos > neg else "Negative"
        result[name] = {"label": label, "adjectives": words, "positive_score": pos,
                        "negative_score": neg, "missing_vectors": []}
    return result


def pretty_print(sentiment_dict, output_path):
    Path(output_path).write_text("".join(f"{name} is {r['label']}. Adjectives: {r['adjectives']}\n"
                                        for name, r in sorted(sentiment_dict.items())), encoding="utf-8")


def analyze(input_path, output_dir, nlp=None):
    import spacy

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if Path(input_path).resolve() in {(out / "char_senti.txt").resolve(), (out / "char_senti.json").resolve()}:
        raise ValueError("Input path collides with an output artifact.")
    nlp = nlp if nlp is not None else spacy.load("en_core_web_md", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])
    result = classify_sentiment(read_char_adj_file(input_path), nlp)
    write_json(out / "char_senti.json", result)
    pretty_print(result, out / "char_senti.txt")
    return {label: sum(r["label"] == label for r in result.values())
            for label in ["Positive", "Negative", "Neutral", "Unscored"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    print(analyze(args.input, args.output_dir))

