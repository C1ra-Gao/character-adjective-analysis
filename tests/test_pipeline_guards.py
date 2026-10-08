import tempfile
import unittest
from pathlib import Path

from pipeline import run
from preprocessing import preprocess


class PipelineGuardTests(unittest.TestCase):
    def test_existing_output_directory_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            source, out = Path(folder) / "input.txt", Path(folder) / "output"
            source.write_text("Alice was happy.", encoding="utf-8")
            out.mkdir()
            sentinel = out / "existing.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run(source, out, "Example")
            self.assertEqual(sentinel.read_text(), "keep")

    def test_full_text_output_inside_public_tree_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input.txt"
            source.write_text("Alice was happy.", encoding="utf-8")
            out = Path(__file__).resolve().parents[1] / "forbidden_test_output"
            with self.assertRaises(ValueError):
                run(source, out, "Example")
            self.assertFalse(out.exists())

    def test_preprocessing_does_not_overwrite_input(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input.txt"
            source.write_text("Alice was happy.", encoding="utf-8")
            with self.assertRaises(ValueError):
                preprocess(source, source)
            self.assertEqual(source.read_text(), "Alice was happy.")


if __name__ == "__main__":
    unittest.main()
