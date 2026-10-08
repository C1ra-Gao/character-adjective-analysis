import unittest

from preprocessing import clean_sentences, strip_gutenberg


class PreprocessingTests(unittest.TestCase):
    def test_old_and_new_gutenberg_markers(self):
        for determiner in ["THIS", "THE"]:
            text = ("\ufefflicense\r\n*** START OF " + determiner + " PROJECT GUTENBERG EBOOK X ***\r\n"
                    "Alice was happy.\r\n*** END OF " + determiner + " PROJECT GUTENBERG EBOOK X ***\r\nfooter")
            body, removed = strip_gutenberg(text)
            self.assertTrue(removed)
            self.assertEqual(body.strip(), "Alice was happy.")

    def test_plain_text_is_preserved(self):
        self.assertEqual(strip_gutenberg("Alice was happy."), ("Alice was happy.", False))

    def test_production_credits_inside_marker_are_removed(self):
        text = ("*** START OF THIS PROJECT GUTENBERG EBOOK X ***\n\n"
                "Produced by Test Producer.\nHTML version by Another Producer.\n\n"
                "Title\n\nTHE PREFACE\nAlice was happy.\n"
                "*** END OF THIS PROJECT GUTENBERG EBOOK X ***\nlicense")
        body, removed = strip_gutenberg(text)
        self.assertTrue(removed)
        self.assertNotIn("Producer", body)
        self.assertIn("THE PREFACE", body)

    def test_produced_phrase_in_plain_story_is_preserved(self):
        text = "Produced by a kind friend, the play was wonderful."
        self.assertEqual(strip_gutenberg(text), (text, False))

    def test_old_footer_note_inside_marker_is_removed(self):
        text = ("*** START OF THIS PROJECT GUTENBERG EBOOK X ***\nAlice was happy.\n\n"
                "End of Project Gutenberg's X, by Test Author\n\n"
                "*** END OF THIS PROJECT GUTENBERG EBOOK X ***\nlicense")
        body, removed = strip_gutenberg(text)
        self.assertTrue(removed)
        self.assertEqual(body.strip(), "Alice was happy.")

    def test_incomplete_markers_fail_visibly(self):
        for text in ["*** START OF THE PROJECT GUTENBERG EBOOK X ***\nbody",
                     "body\n*** END OF THIS PROJECT GUTENBERG EBOOK X ***",
                     "*** END OF THE PROJECT GUTENBERG EBOOK X ***\n*** START OF THE PROJECT GUTENBERG EBOOK X ***"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                strip_gutenberg(text)

    def test_internal_newlines_blank_and_quote_only(self):
        accepted, rejected = clean_sentences([" Alice\n\nwas happy. ", "  ", '"', ". . ."], lambda s: ("en", -4))
        self.assertEqual(accepted, ["Alice was happy."])
        self.assertEqual(len(rejected), 2)

    def test_non_english_short_sentence_is_not_bypassed(self):
        accepted, rejected = clean_sentences(["Bonjour!"], lambda s: ("fr", 0.99))
        self.assertEqual(accepted, [])
        self.assertEqual(rejected[0]["language"], "fr")


if __name__ == "__main__":
    unittest.main()
