"""2026 repair: PERSON/ADJ windows and pointwise mutual information.

Retains the course's en_core_web_sm and two tokens on either side of the entity.
No alias merging, lemmatization, dependency attribution or new model is added.
"""
import argparse
import math
from collections import Counter, defaultdict
from pathlib import Path

from common import write_json


def calculate_mutual_information(char_adj_dict):
    """PMI over observed character-adjective co-occurrence events.

    N is the total number of pair events, not the number of characters.
    A token counted in overlapping windows creates one event per window.
    """
    totals = Counter()
    for adjectives in char_adj_dict.values():
        for adj, count in adjectives.items():
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise ValueError("Counts must be non-negative integers.")
            totals[adj] += count
    n = sum(totals.values())
    if n == 0:
        return {}
    scores = {}
    for character, adjectives in char_adj_dict.items():
        marginal = sum(adjectives.values())
        if marginal:
            scores[character] = {
                adj: round(math.log2(count * n / (marginal * totals[adj])), 5)
                for adj, count in adjectives.items() if count > 0
            }
    return scores


def extract_character_adjectives(doc):
    counts, characters = defaultdict(Counter), set()
    for ent in doc.ents:
        if ent.label_ != "PERSON":
            continue
        characters.add(ent.text)
        for token in doc[max(ent.start - 2, 0):min(ent.end + 2, len(doc))]:
            if token.pos_ == "ADJ":
                counts[ent.text][token.text.lower()] += 1
    return dict(counts), sorted(characters)


def top_adjectives(scores):
    # Stable tie behavior preserves the original adjective insertion order.
    return {name: [adj for adj, _ in sorted(adjs.items(), key=lambda item: item[1], reverse=True)[:3]]
            for name, adjs in sorted(scores.items()) if len(adjs) >= 3}


def pretty_print(char_adj_dict, output_path):
    top = top_adjectives(char_adj_dict)
    Path(output_path).write_text("".join(f"{name}: {' '.join(adjs)}\n" for name, adjs in top.items()), encoding="utf-8")
    return top


def analyze(input_path, output_dir, nlp=None):
    import spacy

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if Path(input_path).resolve() in {(output_dir / name).resolve() for name in
                                     ["char_adj.txt", "char_adj_dict.json", "mutual_info_dict.json", "characters.json"]}:
        raise ValueError("Input path collides with an output artifact.")
    text = Path(input_path).read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("NER input is empty.")
    nlp = nlp if nlp is not None else spacy.load("en_core_web_sm")
    nlp.max_length = max(nlp.max_length, len(text) + 1)
    doc = nlp(text)
    counts, characters = extract_character_adjectives(doc)
    scores = calculate_mutual_information(counts)
    top = pretty_print(scores, output_dir / "char_adj.txt")
    write_json(output_dir / "char_adj_dict.json", counts)
    write_json(output_dir / "mutual_info_dict.json", scores)
    write_json(output_dir / "characters.json", characters)
    return {"tokens": len(doc), "person_name_strings": len(characters),
            "names_with_adjectives": len(counts), "names_with_top_three": len(top),
            "pair_events": sum(sum(a.values()) for a in counts.values())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    print(analyze(args.input, args.output_dir))
