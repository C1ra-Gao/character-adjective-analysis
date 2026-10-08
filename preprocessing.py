"""2026 repair: NLTK Punkt sentences and py3langid English filtering.

The 2023 course supplied the task and script framework. This repair was
implemented with Codex assistance; historical authorship is not inferred.
"""
import argparse
import re
from pathlib import Path

from common import distinct_paths, write_json

START = re.compile(r"^\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG\b.*?\*\*\*\s*$", re.M | re.I)
END = re.compile(r"^\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG\b.*?\*\*\*\s*$", re.M | re.I)
CREDITS = re.compile(r"\A\s*Produced by\b.*?(?:\n[ \t]*\n|\Z)", re.S | re.I)
END_NOTE = re.compile(r"(?:\n|\A)End of Project Gutenberg(?:'s|-tm)?[^\n]*(?:\n[ \t]*)*\Z", re.I)


def strip_gutenberg(text):
    """Remove wrapper only when a complete, ordered START/END pair exists."""
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    start, end = START.search(text), END.search(text)
    if start is None and end is None:
        return text, False
    if start is None or end is None or end.start() <= start.end():
        raise ValueError("Incomplete or reversed Project Gutenberg markers; inspect the input.")
    # Older editions put a production-credit paragraph inside the markers.
    # Remove only this leading metadata block, preserving title and preface.
    body = text[start.end():end.start()]
    body = CREDITS.sub("", body, count=1)
    return END_NOTE.sub("", body, count=1), True


def clean_sentences(sentences, classify):
    accepted, rejected = [], []
    for sentence in sentences:
        sentence = " ".join(sentence.split())
        if not sentence or not any(c.isalpha() for c in sentence):
            if sentence:
                rejected.append({"text": sentence, "reason": "no_letters"})
            continue
        language, score = classify(sentence)
        # No confidence threshold: the default langid score is not a probability.
        # Short English dialogue may still be falsely rejected; retain a local log.
        if language == "en":
            accepted.append(sentence)
        else:
            rejected.append({"text": sentence, "reason": "language", "language": language, "score": float(score)})
    return accepted, rejected


def preprocess(input_path, output_path, rejection_path=None):
    import nltk
    import py3langid

    distinct_paths(input_path, output_path)
    if rejection_path is not None:
        distinct_paths(input_path, rejection_path)
        distinct_paths(output_path, rejection_path)
    text, stripped = strip_gutenberg(Path(input_path).read_text(encoding="utf-8-sig"))
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    sentences = tokenizer.tokenize(text)
    accepted, rejected = clean_sentences(sentences, py3langid.classify)
    if not accepted:
        raise ValueError("No English sentences remain after preprocessing.")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(accepted) + "\n", encoding="utf-8")
    if rejection_path is not None:
        write_json(rejection_path, rejected)
    return {"gutenberg_wrapper_removed": stripped, "tokenized_sentences": len(sentences),
            "accepted_sentences": len(accepted), "rejected_sentences": len(rejected),
            "language_rejections": sum(r["reason"] == "language" for r in rejected),
            "nontext_rejections": sum(r["reason"] == "no_letters" for r in rejected)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--rejections")
    args = parser.parse_args()
    print(preprocess(args.input, args.output, args.rejections))
