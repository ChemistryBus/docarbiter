# Install the routed tools

`docarbiter` routes; it does **not** vendor upstream code. This page is the bridge between
"the router chose a tool" and "the tool is actually installed".

## One command

```bash
# From a clone: core tools used by the default routes
./scripts/install.sh --profile core

# Or bootstrap from GitHub (clone + install)
curl -fsSL https://raw.githubusercontent.com/ChemistryBus/docarbiter/main/bootstrap.sh | bash

# Check what is missing
./scripts/doctor.sh --check-conflicts
```

If you only want the skill and will install tools yourself:

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

## Core tools

| ID | Use it for | Upstream | License | Install |
|---|---|---|---|---|
| `mineru` | PDF → structured Markdown, page anchors, OCR | https://github.com/opendatalab/MinerU | Apache-2.0 + terms | `pip install mineru==4.1.7` |
| `docling` | Office/HTML/EPUB, RAG, LaTeX, complex merged tables | https://github.com/docling-project/docling | MIT | `pip install docling==2.149.0` |
| `liteparse` | Fast text-layer PDF, word coordinates | https://github.com/run-llama/liteparse | Apache-2.0 | `pip install liteparse==2.18.0` |
| `markitdown` | Simple single-column PDF/Office | https://github.com/microsoft/markitdown | MIT | `pip install markitdown==0.1.9` |
| `rapidocr` | Chinese-first image/screenshot OCR | https://github.com/RapidAI/RapidOCR | Apache-2.0 | `pip install rapidocr==3.10.0` |
| `ocrmypdf` | Add a searchable text layer to scans | https://github.com/ocrmypdf/OCRmyPDF | MPL-2.0 | `pip install ocrmypdf==17.12.1` + Tesseract |
| `pdfplumber` | Simple bordered tables, character coordinates | https://github.com/jsvine/pdfplumber | MIT | `pip install pdfplumber==0.11.10` |
| `pdftotext` | Plain-text baseline and text-layer probe | https://poppler.freedesktop.org/ | GPL-2.0/3.0 | macOS: `brew install poppler` · Debian/Ubuntu: `sudo apt-get install poppler-utils` |

## Extra and optional

These are **not installed by default**. `./scripts/install.sh --profile extra` installs the
first four plus optional supplements; individual commands are below.

| ID | Use it for | Upstream | License | Install |
|---|---|---|---|---|
| `paddleocr` | Chinese OCR / PP-Structure | https://github.com/PaddlePaddle/PaddleOCR | Apache-2.0 | `pip install paddleocr paddlepaddle` |
| `marker` | PDF → Markdown (GPU recommended) | https://github.com/datalab-to/marker | Apache-2.0 | `pip install marker-pdf==2.1.0` |
| `unstructured` | Enterprise multi-format ingestion | https://github.com/Unstructured-IO/unstructured | Apache-2.0 | `pip install unstructured==0.27.37` |
| `olmocr` | VLM OCR for scans (GPU required) | https://github.com/allenai/olmocr | Apache-2.0 | `pip install olmocr==0.4.27` |
| `surya` | OCR / layout / reading order | https://github.com/datalab-to/surya | Apache-2.0 | `pip install surya-ocr==0.23.0` |
| `camelot` | Text-layer table extraction | https://github.com/camelot-dev/camelot | MIT | `pip install camelot-py==2.0.0` |
| `tesseract` | OCR fallback | https://github.com/tesseract-ocr/tesseract | Apache-2.0 | macOS: `brew install tesseract tesseract-lang` · Debian/Ubuntu: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim` |
| `qpdf` | Split/merge/decrypt PDFs | https://github.com/qpdf/qpdf | Apache-2.0 | macOS: `brew install qpdf` · Debian/Ubuntu: `sudo apt-get install qpdf` |
| `pypdf` | Pure-Python PDF operations | https://github.com/py-pdf/pypdf | BSD-3-Clause | `pip install pypdf==7.0.0` |
| `pdfminer` | Low-level text/coordinate fallback | https://github.com/pdfminer/pdfminer.six | MIT | `pip install pdfminer.six==20260107` |

## Deliberately not installed

| Tool | License | Why |
|---|---|---|
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) | AGPL-3.0 / commercial | Copyleft; link only |
| [PDF-Extract-Kit](https://github.com/opendatalab/PDF-Extract-Kit) | AGPL-3.0 | Copyleft; link only |
| [Ghostscript](https://www.ghostscript.com/) | AGPL-3.0 | Copyleft; not installed |
| Anthropic `pdf` skill | Proprietary | Cannot be redistributed; link only |
| LlamaParse / Azure DI / Google Document AI / Adobe PDF Extract / Mathpix | Commercial API | Data leaves the machine; not a local default |

## Notes

- The install commands use package managers; this repository does not `git clone` third-party
  skill repositories.
- Upstream tools may download their own model weights on first use (for example MinerU and
  RapidOCR). That is upstream behavior, not a repository clone.
- In an offline or restricted environment, use `--skills-only`, preinstall the selected tools,
  and rerun `./scripts/doctor.sh --check-conflicts`.
- If a tool is missing, the router can still explain the fallback; install the selected tool
  from the upstream link above and rerun `doctor.sh`.

Machine-readable source: [`registry.json`](../registry.json) (`install` and `upstream` fields).
