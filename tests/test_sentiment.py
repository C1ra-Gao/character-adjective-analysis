import itertools
import tempfile
import unittest
from pathlib import Path

from char_roles import classify_sentiment, mean_similarity, read_char_adj_file, positive_adj


class FakeDoc:
    def __init__(self, word):
        self.word = word
        self.vector_norm = 0 if word == "missing" else 1

    def similarity(self, seed):
        pos, neg = {"pos": (1, 0), "neg": (0, 1), "flat": (0.5, 0.5)}[self.word]
        return pos if seed.word in positive_adj else neg


class SentimentTests(unittest.TestCase):
    def test_average_all_pairs(self):
        result = classify_sentiment({"A": ["pos", "pos", "neg"]}, FakeDoc)["A"]
        self.assertAlmostEqual(result["positive_score"], 2 / 3)
        self.assertAlmostEqual(result["negative_score"], 1 / 3)
        self.assertEqual(result["label"], "Positive")

    def test_all_permutations_have_same_scores_and_label(self):
        for words in itertools.permutations(["pos", "neg", "flat"]):
            result = classify_sentiment({"A": list(words)}, FakeDoc)["A"]
            self.assertEqual(result["label"], "Neutral")
            self.assertEqual(result["positive_score"], 0.5)
            self.assertEqual(result["negative_score"], 0.5)

    def test_negative_and_positive(self):
        result = classify_sentiment({"A": ["neg"] * 3, "B": ["pos"] * 3}, FakeDoc)
        self.assertEqual(result["A"]["label"], "Negative")
        self.assertEqual(result["B"]["label"], "Positive")

    def test_empty_and_missing_vectors_are_unscored(self):
        result = classify_sentiment({"A": [], "B": ["pos", "neg", "missing"]}, FakeDoc)
        self.assertEqual(result["A"]["reason"], "empty_adjectives")
        self.assertEqual(result["B"]["missing_vectors"], ["missing"])
        self.assertIsNone(result["B"]["positive_score"])
        self.assertEqual(result["B"]["label"], "Unscored")

    def test_empty_average_is_invalid(self):
        with self.assertRaises(ValueError):
            mean_similarity([], [FakeDoc("good")])

    def test_input_parser(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "input.txt"
            p.write_text("\nAlice: good happy friendly\n", encoding="utf-8")
            self.assertEqual(read_char_adj_file(p), {"Alice": ["good", "happy", "friendly"]})
            for text in ["Alice", ": a b c", "Alice: a b", "Alice: a b c\nAlice: d e f"]:
                p.write_text(text, encoding="utf-8")
                with self.subTest(text=text), self.assertRaises(ValueError):
                    read_char_adj_file(p)


if __name__ == "__main__":
    unittest.main()
