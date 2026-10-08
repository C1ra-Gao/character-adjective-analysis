import math
import unittest

from ner import calculate_mutual_information, top_adjectives


class PMITests(unittest.TestCase):
    def test_known_joint_distribution(self):
        scores = calculate_mutual_information({"A": {"good": 3, "bad": 1}, "B": {"good": 1, "bad": 3}})
        self.assertEqual(scores["A"]["good"], round(math.log2(1.5), 5))
        self.assertEqual(scores["A"]["bad"], -1.0)
        self.assertEqual(scores["B"]["bad"], scores["A"]["good"])

    def test_independent_events_score_zero(self):
        self.assertEqual(calculate_mutual_information({"A": {"x": 2, "y": 2}, "B": {"x": 2, "y": 2}}),
                         {"A": {"x": 0.0, "y": 0.0}, "B": {"x": 0.0, "y": 0.0}})

    def test_replication_does_not_change_probabilities(self):
        counts = {"A": {"x": 3, "y": 1}, "B": {"x": 1, "y": 3}}
        larger = {c: {a: 10 * n for a, n in adjs.items()} for c, adjs in counts.items()}
        self.assertEqual(calculate_mutual_information(counts), calculate_mutual_information(larger))

    def test_empty_and_zero_events(self):
        for data in [{}, {"A": {}}, {"A": {"x": 0}}]:
            self.assertEqual(calculate_mutual_information(data), {})

    def test_zero_pairs_are_not_logged(self):
        self.assertEqual(calculate_mutual_information({"A": {"x": 0, "y": 1}}), {"A": {"y": 0.0}})

    def test_invalid_counts_rejected(self):
        for n in [-1, 0.5, True, "3"]:
            with self.subTest(count=n), self.assertRaises(ValueError):
                calculate_mutual_information({"A": {"x": n}})

    def test_top_three_threshold_and_order(self):
        self.assertEqual(top_adjectives({"A": {"a": 0, "b": 4, "c": 2, "d": 3}, "B": {"a": 1}}),
                         {"A": ["b", "d", "c"]})

    def test_ties_keep_original_insertion_order(self):
        self.assertEqual(top_adjectives({"A": {"z": 1, "a": 1, "b": 1}}), {"A": ["z", "a", "b"]})


if __name__ == "__main__":
    unittest.main()
