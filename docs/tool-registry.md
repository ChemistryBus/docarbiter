# Tool Registry

> Verification date: 2026-11-09. Star counts are a snapshot of GitHub that day; licenses follow the repository's `LICENSE` / package metadata.
> Machine-readable version: `registry.json`. This file is the human-readable description.
> Per-tool install commands and upstream links: `docs/install-routed-tools.md`.
> "Pending" in the Chinese/English status always means **not yet verified with Chinese and English CER corpora**, not "unsupported."

## 1. Primary tools (12)

### Core layer: installed by default, runs on CPU, permissive licenses

| # | Tool | ★ | License | Role | Install | Chinese/English status |
|---:|---|---:|---|---|---|---|
| 1 | **MinerU** | 83.3k | Apache-2.0 + additional terms | PDF → structured Markdown, heading hierarchy, page anchors | `pip install mineru==4.1.7`; `mineru-doc` | Chinese/English demo 0.0046 / 0.0013; scans 1.59% / 0.20% |
| 2 | **Docling** | 70.3k | MIT | Office / HTML / EPUB / audio-video / RAG chunks / LaTeX / complex merged tables | `pip install docling==2.149.0`; `docling convert` | Chinese/English demo 0.0061 / 0.0093; scans 1.01% / 7.12%; best structure and reading order on real merged tables |
| 3 | **liteparse** | 13.0k | Apache-2.0 | Fastest for PDFs with a text layer; word-level coordinates, font information | `pip install liteparse==2.18.0`; wrapper `liteparse-doc` | Chinese/English demo 0.0061 / 0.0079; text layer usable; not applicable to scans |
| 4 | **MarkItDown** | 194.5k | MIT | Single-column / Office fast conversion to Markdown | `pip install markitdown==0.1.9`; `markitdown` | Chinese/English demo 0.0061 / 0.0185; two-column failure not reproduced (synthetic); not applicable to scans |
| 5 | **RapidOCR** | 8.5k | Apache-2.0 | Image / screenshot OCR | `pip install rapidocr==3.10.0`; Python API | Chinese scan 1.16%; English scan 0.10% |
| 6 | **OCRmyPDF** | 35.3k | MPL-2.0 | Add a text layer to scanned PDFs | `pip install ocrmypdf==17.12.1`; `ocrmypdf` | Chinese scan 10.1%; English scan 0.20% |
| 7 | **pdfplumber** | 10.9k | MIT | Simple bordered tables / character coordinates / DataFrame | `pip install pdfplumber==0.11.10`; Python API | Synthetic bordered tables/merged cells 1.000; real multi-line cells out of order; borderless 0 tables; interleaved two-column 60%–68%; not applicable to scans |
| 8 | **pdftotext** (Poppler) | — | GPL-2.0/3.0 | Plain-text baseline, text-layer detection | System package (Homebrew `poppler`); `pdftotext` | Chinese/English text layer; CID/no ToUnicode produces garbled output |

### Extended layer: installed on demand, heavy dependencies / GPU / special cases

| # | Tool | ★ | License | Role | Install | Chinese/English status |
|---:|---|---:|---|---|---|---|
| 9 | **PaddleOCR** | 92.5k | Apache-2.0 | Chinese OCR / PP-Structure layout and tables | `pip install paddleocr paddlepaddle`; `paddleocr` | Native Chinese, English usable; CER pending; large dependency footprint |
| 10 | **Marker** | 40.8k | Apache-2.0 | PDF → Markdown, multilingual | `pip install marker-pdf==2.1.0`; CLI `marker_single` (to be verified) | Surya multilingual OCR; Chinese/English pending; GPU recommended |
| 11 | **Unstructured** | 15.7k | Apache-2.0 | Enterprise multi-format ingestion / partitioning | `pip install unstructured`; Python API (CLI to be verified) | Depends on OCR backend; Chinese/English pending; heavy dependencies |
| 12 | **olmOCR** | 19.8k | Apache-2.0 | VLM scanned-document OCR / long documents | `pip install olmocr==0.4.27`; CLI `olmocr` (to be verified) | Multilingual; Chinese/English pending; GPU required |

### Optional additions (kept in the registry, not installed by default)

| Tool | ★ | License | Role | Notes |
|---|---:|---|---|---|
| **Surya** | 21.6k | Apache-2.0 | OCR / layout / reading order | Underlying engine of Marker; GPU recommended |
| **Camelot** | 3.8k | MIT | Table extraction (lattice / stream) | Complements pdfplumber; text-layer tables |
| **Tesseract** | 77.4k | Apache-2.0 | OCR fallback | `chi_sim` Chinese weaker than PaddleOCR; many system dependencies |
| **qpdf** | 5.6k | Apache-2.0 | Split / merge / decrypt / repair | PDF operations, no content extraction |
| **pypdf** | 10.3k | BSD-3-Clause | Pure-Python PDF operations | No external binary dependency; suitable for scripting |
| **pdfminer.six** | 7.0k | MIT | Low-level text/coordinate extraction | Fallback; lower level than pdfplumber |

## 2. Considered but not included in the default path

| Tool | ★ | License | Reason not included |
|---|---:|---|---|
| **PDF-Extract-Kit** | 10.1k | AGPL-3.0 | Copyleft license; strong layout/table/formula support. Link only; users decide whether to install |
| **PyMuPDF** | — | AGPL-3.0 / commercial dual license | Same as above; strong low-level control, but would drag the project into AGPL |
| **Ghostscript** | — | AGPL-3.0 | Same as above; used for PDF rendering/conversion |
| **Anthropic `pdf` skill** | — | Proprietary | Not redistributable; handles merge/split/encryption/forms, no structured extraction. README gives a link only |
| **LlamaParse** | — | Commercial API | Cloud parsing; data leaves the machine, billed per page |
| **Azure Document Intelligence** | — | Commercial API | Same as above; strong Chinese layout, but not local |
| **Google Document AI** | — | Commercial API | Same as above |
| **Adobe PDF Extract** | — | Commercial API | Same as above |
| **Mathpix** | — | Commercial API | Strong formulas/tables, but cloud |
| **EasyOCR** | — | Apache-2.0 | Runs, but for Chinese, RapidOCR/PaddleOCR are lighter and more specialized |
| **MMOCR** | — | Apache-2.0 | Research framework; heavy dependencies, higher deployment cost than PaddleOCR |
| **docTR** | — | Apache-2.0 | Mainly OCR; lacks full PDF layout/reading order |

## 3. License grouping (used by `install.sh`)

**Default `--profile core` (permissive, CPU, lightweight):**
MinerU, Docling, liteparse, MarkItDown, RapidOCR, OCRmyPDF, pdfplumber, Poppler/pdftotext.

**`--profile extra` (heavy dependencies / GPU / special):**
PaddleOCR, Marker, Unstructured, olmOCR, Surya, Camelot, Tesseract, qpdf, pypdf, pdfminer.six.

**Never included in the install script:**
PDF-Extract-Kit (AGPL), PyMuPDF (AGPL), Ghostscript (AGPL), Anthropic `pdf` (Proprietary), commercial cloud APIs.

> **Handling of GPL/MPL tools**: `pdftotext` (Poppler, GPL) and OCRmyPDF (MPL) are invoked via system packages/separate processes, without modification or redistribution; the repository's MIT license is unaffected. `install.sh` only runs package-manager commands and does not copy upstream code into the repository.

## 4. Version pinning strategy

Commands and pitfalls in the thin shells were tested against local versions. `install.sh` reads the exact versions in `requirements.lock` by default; only `--latest` installs the newest version and marks it "unverified." Currently tested versions:

```
mineru==4.1.7
docling==2.149.0
liteparse==2.18.0
markitdown==0.1.9
rapidocr==3.10.0
ocrmypdf==17.12.1
pdfplumber==0.11.10
pymupdf==1.28.2      # recorded only, not installed
```

> Extended-layer versions will be added after installation; `marker-pdf` / `surya-ocr` / `unstructured` / `olmocr` / `paddleocr` will be pinned to the first tested version.

## 5. Items pending verification

- [ ] Actual CLI entry points and parameters for Marker / Surya / Unstructured / olmOCR
- [x] CER of each tool on Chinese scans, synthetic interleaved two-column, traditional Chinese, CID/no ToUnicode
- [ ] Cell-level CER on real two-column, true vertical writing, merged-cell tables
- [ ] CER of each tool on real English two-column, English tables, hyphenated line breaks, quotes/dashes (synthetic interleaved two-column already tested)
- [ ] PaddleOCR PP-Structure cell accuracy on Chinese tables
- [ ] Independent license for MinerU model weights (whether downloaded models carry separate terms)
- [ ] Independent license for Marker / Surya model weights
- [ ] `liteparse` behavior on Chinese PDFs without ToUnicode
- [ ] `docling` default OCR backend and Chinese model selection
- [x] `registry.json` and `skills/_tools/` ids match (`validate.py` already checks)
- [ ] Full Chinese and English CER for the 12 primary tools
