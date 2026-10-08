"""Run the repaired course pipeline into a NEW local output directory.

Full preprocessed text and rejection logs stay local. Supply inputs acquired
legally; never publish Dune source, preprocessed text or rejected sentences.
"""
import argparse
import importlib.metadata
import platform
from pathlib import Path

from common import sha256, write_json
from preprocessing import preprocess
from ner import analyze as analyze_ner
from char_roles import analyze as analyze_roles


def versions():
    return {"python": platform.python_version(), **{
        name: importlib.metadata.version(name)
        for name in ["spacy", "nltk", "py3langid", "en-core-web-sm", "en-core-web-md"]}}


def run(input_path, output_dir, book):
    source, out = Path(input_path), Path(output_dir)
    if not source.is_file():
        raise FileNotFoundError("Input book file does not exist.")
    # Prevent accidental historical-output overwrite or placing full texts in
    # the portfolio tree. Publish only reviewed aggregate artifacts afterwards.
    project = Path(__file__).resolve().parent
    if out.resolve().is_relative_to(project):
        raise ValueError("Full pipeline outputs must be outside the public portfolio directory.")
    out.mkdir(parents=True, exist_ok=False)
    print(f"[{book}] preprocessing", flush=True)
    prep = preprocess(source, out / "preprocessed.txt", out / "rejected_sentences.json")
    print(f"[{book}] NER and PMI", flush=True)
    ner = analyze_ner(out / "preprocessed.txt", out)
    print(f"[{book}] vector sentiment", flush=True)
    sentiment = analyze_roles(out / "char_adj.txt", out)
    summary = {"edition": "2026-portfolio-repair", "book": book, "input_sha256": sha256(source),
               "versions": versions(), "preprocessing": prep, "ner": ner, "sentiment": sentiment,
               "method": "Punkt; py3langid English; spaCy PERSON/ADJ +/-2 tokens; pair-event PMI; md seed-vector mean"}
    write_json(out / "run_summary.json", summary)
    print(summary, flush=True)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output_dir")
    parser.add_argument("--book", required=True)
    args = parser.parse_args()
    run(args.input, args.output_dir, args.book)

