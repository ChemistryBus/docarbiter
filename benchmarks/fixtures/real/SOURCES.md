# Real fixture sources

The four PDFs in this directory are derivative works of Wikipedia articles.
They are **CC BY-SA 4.0**, not MIT. The repository's MIT license does not apply
to these fixture texts or PDFs.

Retrieved: **2026-11-09** via the local `seekport` bridge (DeepSeek Fetch).
Modifications: truncated to ~2,200 Chinese characters / ~3,200 English
characters, removed edit markers, reference brackets, infobox/table rows, and
editorial maintenance notes; rendered to A4 PDF with reportlab. The cleaned
text is stored next to each PDF as the answer key.

| Fixture | Source | License |
|---|---|---|
| `zh-ocr.pdf/.txt` | <https://zh.wikipedia.org/wiki/光学字符识别> | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| `zh-pdf.pdf/.txt` | <https://zh.wikipedia.org/wiki/便携式文档格式> | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| `en-ocr.pdf/.txt` | <https://en.wikipedia.org/wiki/Optical_character_recognition> | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| `en-pdf.pdf/.txt` | <https://en.wikipedia.org/wiki/PDF> | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| `bert-abstract-2p.pdf` / `bert-abstract-2p.txt` | Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", NAACL 2019, <https://aclanthology.org/N19-1423/> | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

Attribution: Wikipedia contributors. If you redistribute these fixtures, keep
this notice, the source URLs, and the CC BY-SA 4.0 license; derivative works
must be shared under the same license.

The raw fetched Markdown is in `source/` for reproducibility. It is also
CC BY-SA 4.0.

The BERT fixture is different:

- `bert-abstract-2p.pdf` is a 2-page excerpt (pages 1–2) of the ACL Anthology
  PDF, kept as a real two-column layout fixture. It is CC BY 4.0; attribution
  above.
- `bert-abstract-2p.txt` is the abstract text extracted from the ACL Anthology
  HTML page, used only for abstract-level CER. It is the same CC BY 4.0 work.
- The full 16-page PDF is kept locally in `benchmarks/private/` and is not
  distributed by the repository.

> The Wikipedia fixtures are text-layer PDFs generated from article text, not
> scans. The BERT fixture is a real two-column PDF but only the abstract is
> scored; the full body, figures, and references are not.
