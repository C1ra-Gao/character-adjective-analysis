# Third-party materials review

Reviewed on 2026-10-08 against installed package metadata/license files and
official upstream sources. This records attribution and distribution scope;
it does not license the course submission or book texts.

| Material | Verified information | Scope in this candidate |
|---|---|---|
| spaCy 3.8.16 | MIT, installed license and [upstream license](https://github.com/explosion/spaCy/blob/master/LICENSE) | Import and pinned dependency; no package source bundled |
| NLTK 3.10.3 | Apache-2.0, installed license and [upstream license](https://github.com/nltk/nltk/blob/develop/LICENSE.txt) | Import and pinned dependency; no package source/docs bundled |
| py3langid 0.4.0 | BSD-3-Clause, installed license expression/file and [upstream license](https://github.com/adbar/py3langid/blob/master/LICENSE) | Import and pinned dependency; no package source/model data bundled |
| spaCy English models 3.8.0 | MIT, installed license files and official [small](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0) / [medium](https://github.com/explosion/spacy-models/releases/tag/en_core_web_md-3.8.0) releases | Official wheel links and hashes only; models/training corpora not bundled |
| NLTK Punkt resources | Official [package metadata](https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.xml) identifies Jan Strunk; that XML does not state a license | Download reference and hashes only; archive/resources not bundled. Do not infer a data license from the NLTK code license |
| Project Gutenberg eBook 174 | [Source](https://www.gutenberg.org/ebooks/174) and [distribution terms](https://www.gutenberg.org/policy/license.html) | Book identifier, input hash, aggregate results and short word lists; no ebook/wrapper copied |
| Dune course copy | Supplied with the course; no redistribution authorization provided | Aggregate counts, name strings and short word lists only; no source/full-text derivatives |
| PfL course task and method requirements | Acknowledged course inputs; author confirms independent authorship of the 2023 code | Task text/PDF and original course materials not bundled; no template-code permission is awaited |

The model packages also contain `LICENSES_SOURCES` notices for their source
materials. The model MIT license is not a license to redistribute the training
corpora. This project does not vendor models, corpora, dependency wheels, or
tokenizer archives. If packaging them later, review their notices separately.

The full dependency lock includes transitive dependencies. It references
installable packages rather than copying their implementations. This review
does not claim a complete legal/security audit of every transitive dependency.

No upstream evaluation scores are presented as results of this project.
No repository-wide LICENSE has been added. The author's confirmation resolves
the earlier implementation-ownership concern. It does not grant rights to the
course documents, book texts, or other third-party materials. Only final author
approval is awaited for a GitHub push; no course-code authorization is awaited.
