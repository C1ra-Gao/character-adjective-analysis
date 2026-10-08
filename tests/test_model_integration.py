"""Real-model checks, in addition to the whole-book pipeline runs."""
import itertools
import tempfile
import unittest
from pathlib import Path

import spacy

from char_roles import classify_sentiment
from ner import extract_character_adjectives
from preprocessing import preprocess


class ModelIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.small = spacy.load("en_core_web_sm")
        cls.medium = spacy.load("en_core_web_md", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])

    def test_real_vector_order_invariance(self):
        outputs = [classify_sentiment({"Alice": list(words)}, self.medium)["Alice"]
                   for words in itertools.permutations(["good", "angry", "happy"])]
        for out in outputs:
            self.assertEqual(out["label"], outputs[0]["label"])
            self.assertAlmostEqual(out["positive_score"], outputs[0]["positive_score"], places=12)
            self.assertAlmostEqual(out["negative_score"], outputs[0]["negative_score"], places=12)

    def test_vector_tokenization_matches_original_full_pipeline(self):
        full = spacy.load("en_core_web_md")
        for word in ["good", "bad", "angry", "happy"]:
            self.assertAlmostEqual(full(word).similarity(full("friendly")),
                                   self.medium.make_doc(word).similarity(self.medium.make_doc("friendly")), places=12)

    def test_multi_token_entity_and_document_edges(self):
        from spacy.tokens import Doc, Span
        doc = Doc(self.small.vocab, words=["kind", "Harry", "Potter", "was", "happy"],
                  pos=["ADJ", "PROPN", "PROPN", "AUX", "ADJ"])
        doc.ents = [Span(doc, 1, 3, label="PERSON")]
        counts, names = extract_character_adjectives(doc)
        self.assertEqual(names, ["Harry Potter"])
        self.assertEqual(counts["Harry Potter"], {"kind": 1, "happy": 1})

    def test_real_preprocessor_strips_wrapper_and_preserves_input(self):
        text = ("Gutenberg license\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\n"
                "Alice was a kind and friendly person.\n\nShe was happy to meet her friends.\n"
                "*** END OF THE PROJECT GUTENBERG EBOOK X ***\nProject Gutenberg footer")
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "book.txt", Path(folder) / "clean.txt"
            source.write_text(text, encoding="utf-8")
            summary = preprocess(source, output)
            self.assertTrue(summary["gutenberg_wrapper_removed"])
            self.assertEqual(source.read_text(encoding="utf-8"), text)
            self.assertNotIn("Gutenberg", output.read_text(encoding="utf-8"))
            self.assertTrue(all(line.strip() for line in output.read_text().splitlines()))


if __name__ == "__main__":
    unittest.main()
