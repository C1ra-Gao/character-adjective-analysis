# Phase 2 verification procedure

This is a technical reproduction record, not the public portfolio README.
Commands below run from the portfolio directory. Keep validation directories
outside it. Tested on macOS arm64 with Python **3.12.6**. Other platforms and
Python versions have not been verified.

## Environment

```sh
python3.12 -m venv ../.local-validation/.venv
../.local-validation/.venv/bin/python -m pip install -r requirements-lock.txt
../.local-validation/.venv/bin/python -m pip check
```

Confirm the interpreter version before claiming an exact reproduction. The lock
file records every installed package version, and the two official spaCy model
wheel URLs include their SHA-256 digests. Actual tested package/model metadata
is in `environment.json`.

NLTK also needs a data resource, which is not included in pip's lock file.
Download the official `punkt_tab.zip` URL recorded in `nltk-resource.json` into
`../.local-validation/punkt_tab.zip`. The normal NLTK downloader was incompatible
with this session's network proxy, so the same official archive was downloaded
directly. Validate the hash and extract it locally:

```sh
curl -fL https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip -o ../.local-validation/punkt_tab.zip
../.local-validation/.venv/bin/python - <<'PY'
import hashlib, json, pathlib, zipfile
local = pathlib.Path('../.local-validation')
record = json.loads(pathlib.Path('docs/nltk-resource.json').read_text())
archive = local / 'punkt_tab.zip'
if hashlib.sha256(archive.read_bytes()).hexdigest() != record['zip_sha256']:
    raise SystemExit('NLTK archive differs from tested resource; do not claim an exact reproduction.')
with zipfile.ZipFile(archive) as z:
    z.extractall(local / 'nltk_data/tokenizers')
for name, digest in record['english_files'].items():
    p = local / 'nltk_data/tokenizers/punkt_tab/english' / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        raise SystemExit('Extracted English tokenizer resource differs.')
PY
export NLTK_DATA="$(cd ../.local-validation/nltk_data && pwd)"
../.local-validation/.venv/bin/python -m unittest discover -s tests -v
```

The URL is a maintained upstream branch; the digest check deliberately fails
if its contents change. The tested archive is retained locally, outside the
public portfolio. No unverified resource is silently substituted.

## Input and complete runs

Acquire input books legally and keep the files outside the portfolio directory.
The local validation used the two course-submission inputs, with hashes recorded
in each `run_summary.json`. The Dorian Gray input is the older Gutenberg #174
edition; the current downloadable edition may differ. Use a matching hash to
reproduce these exact aggregates. A different edition is a new run.

The original Dune course copy is not bundled with this project. Do not download
an unauthorized copy, or publish a raw/preprocessed copy or rejected sentences.
The same rule applies to any restricted input. Commands accept locally supplied
files; an absent source is an explicit error.

```sh
../.local-validation/.venv/bin/python pipeline.py /path/to/dorian_gray.txt ../.local-validation/runs/dorian_gray --book 'The Picture of Dorian Gray'
../.local-validation/.venv/bin/python pipeline.py /path/to/legally-held/dune.txt ../.local-validation/runs/dune --book Dune
../.local-validation/.venv/bin/python validate_run.py ../.local-validation/runs/dorian_gray --report ../.local-validation/dorian_check.json
../.local-validation/.venv/bin/python validate_run.py ../.local-validation/runs/dune --report ../.local-validation/dune_check.json
```

Each output directory must be new. The pipeline refuses existing directories
and locations inside the public portfolio tree. Outputs include local full
preprocessed text and language-rejection logs, plus aggregate counts, PMI,
top-three words, vector scores, labels and versions. The stage scripts also
support explicit input/output arguments for separate execution:

```sh
../.local-validation/.venv/bin/python preprocessing.py /path/to/book.txt ../.local-validation/clean.txt --rejections ../.local-validation/rejected.json
../.local-validation/.venv/bin/python ner.py ../.local-validation/clean.txt ../.local-validation/stages
../.local-validation/.venv/bin/python char_roles.py ../.local-validation/stages/char_adj.txt ../.local-validation/stages
```

Only reviewed aggregate artifacts were copied into `results/`. No raw book,
preprocessed book, rejection-log content, original submission or course PDF is
included there. `verification.json` includes their hashes as evidence, not their
contents. Always check data rights before deciding what to distribute.

## Difference interpretation

`compare_repairs.py RUN_DIR HISTORICAL_CHAR_ADJ --report REPORT` compares the
historical top-three artifact separately from two controlled arithmetic checks.
Controlled checks use repaired counts/word lists and the current model for both
arithmetic variants. Their labels are **not reconstructed 2023 experimental
results**, and a changed label is not evidence of improved accuracy.

Repeat runs in fresh local directories can be compared byte-for-byte. Phase 2
verified matching files in the same machine/environment; a clean install on a
second machine has not been tested.
