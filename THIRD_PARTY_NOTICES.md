# Third-Party Notices

This repository (`docarbiter`) is licensed under the MIT License
(see `LICENSE`). It contains **only original documentation, wrappers, and install
scripts**. It does **not** contain, vendor, or sublicense any upstream source
code or model weights.

`scripts/install.sh` invokes package managers (`pip`, `brew`, `apt`) to install
the tools below on the user's machine. Each tool remains under its own license.
The user is responsible for complying with that license in their own use,
including commercial use, online-service attribution, and model-weight terms.

> This file is a good-faith attribution record, not legal advice. Verify the
> upstream license at the linked URL before redistributing or offering a service.

## Tools installed by this repository

| Tool | License | Copyright / holder | Upstream | Our use |
|---|---|---|---|---|
| MinerU | Apache-2.0 + additional terms (see below) | © 2026 MinerU Team | https://github.com/opendatalab/MinerU | Call CLI; no code or models redistributed |
| Docling | MIT | © IBM Corp. and Docling contributors | https://github.com/docling-project/docling | Call CLI; no code redistributed |
| liteparse | Apache-2.0 | © Run-Llama and liteparse contributors | https://github.com/run-llama/liteparse | Call Python package via our wrapper |
| MarkItDown | MIT | © Microsoft Corporation | https://github.com/microsoft/markitdown | Call CLI; no code redistributed |
| RapidOCR | Apache-2.0 | © RapidOCR authors; models derived from PaddleOCR / Baidu | https://github.com/RapidAI/RapidOCR | Call Python API; no models redistributed |
| OCRmyPDF | MPL-2.0 | © James R. Barlow and contributors | https://github.com/ocrmypdf/OCRmyPDF | Call CLI; no code modified or redistributed |
| pdfplumber | MIT | © 2015 Jeremy Singer-Vine | https://github.com/jsvine/pdfplumber | Call Python API |
| Poppler / pdftotext | GPL-2.0-only OR GPL-3.0-only | © The Poppler Developers; © Glyph & Cog, LLC | https://poppler.freedesktop.org/ | Call system binary only |
| qpdf | Apache-2.0 | © Jay Berkenbilt and contributors | https://github.com/qpdf/qpdf | Call system binary only |
| pypdf | BSD-3-Clause | © Mathieu Fenniak and contributors | https://github.com/py-pdf/pypdf | Call Python API |
| pdfminer.six | MIT | © pdfminer.six authors | https://github.com/pdfminer/pdfminer.six | Call Python API |
| Camelot | MIT | © 2019–2024 Camelot Developers; © 2018–2019 Peeply Private Ltd | https://github.com/camelot-dev/camelot | Call Python API |
| Tesseract | Apache-2.0 | © Google Inc. and Tesseract contributors | https://github.com/tesseract-ocr/tesseract | Call system binary only |
| PaddleOCR | Apache-2.0 | © PaddlePaddle Authors; model weights from Baidu / PaddleOCR | https://github.com/PaddlePaddle/PaddleOCR | Call Python API; no models redistributed |
| Marker | Apache-2.0 | © Datalab and Marker contributors | https://github.com/datalab-to/marker | Call CLI; no models redistributed |
| Surya | Apache-2.0 | © Datalab and Surya contributors | https://github.com/datalab-to/surya | Call Python API; no models redistributed |
| Unstructured | Apache-2.0 | © Unstructured Technologies and contributors | https://github.com/Unstructured-IO/unstructured | Call Python API |
| olmOCR | Apache-2.0 | © Allen Institute for AI (AI2) | https://github.com/allenai/olmocr | Call CLI; no models redistributed |

## Tools linked but NOT installed

| Tool | License | Reason | Link |
|---|---|---|---|
| Anthropic `pdf` skill | Proprietary (Anthropic PBC) | Cannot be redistributed; only linked | https://github.com/anthropics/skills |
| PyMuPDF | AGPL-3.0 / commercial dual license | Copyleft; not installed or recommended | https://github.com/pymupdf/PyMuPDF |
| PDF-Extract-Kit | AGPL-3.0 | Copyleft; not installed or recommended | https://github.com/opendatalab/PDF-Extract-Kit |
| Ghostscript | AGPL-3.0 | Copyleft; not installed | https://www.ghostscript.com/ |
| LlamaParse | Commercial API | Cloud service; data leaves the machine | https://www.llamaindex.ai/llamaparse |
| Azure Document Intelligence | Commercial API | Cloud service; data leaves the machine | https://azure.microsoft.com/products/ai-services/ai-document-intelligence |
| Google Document AI | Commercial API | Cloud service; data leaves the machine | https://cloud.google.com/document-ai |
| Adobe PDF Extract | Commercial API | Cloud service; data leaves the machine | https://developer.adobe.com/document-services/apis/pdf-extract/ |
| Mathpix | Commercial API | Cloud service; data leaves the machine | https://mathpix.com/ |

## MinerU additional terms (verbatim)

Source: the `LICENSE.md` shipped with the `mineru` 4.1.7 Python package
(`mineru-4.1.7.dist-info/licenses/LICENSE.md`). The upstream project is
https://github.com/opendatalab/MinerU. The SPDX expression reported by the
package is `LicenseRef-MinerU-Open-Source-License`.

```text
## MinerU Open Source License

MinerU is licensed under Apache License 2.0 and is subject to the additional
terms below. Except to the extent expressly modified or supplemented by these
additional terms, your other rights and obligations are governed by Apache
License 2.0.

**1. Commercial License and Thresholds**

MinerU may be used for commercial purposes without a separate commercial
license. However, if you and your Affiliates, on a consolidated basis, meet
either of the following thresholds, you must obtain a separate commercial
license from [MinerU Team] before continuing such use:

a. monthly active users (MAU) exceed 100 million; or
b. total monthly revenue exceeds USD 20 million.

**2. Online Service Attribution Obligation**

If you provide online services to third parties based on MinerU, you must
clearly and prominently indicate, in the relevant product or service interface
or in publicly available documentation, that MinerU is used.

**3. Termination**

Where a separate commercial license is required under Section 1 but is not
obtained before continuing such use, or where the attribution obligation under
Section 2 is not complied with, this License and all rights granted under this
License will terminate automatically, and no further notice from the Licensor
is required.

**4. Definitions**

In these additional terms, "Affiliates" means any legal entity that directly or
indirectly controls, is controlled by, or is under common control with you.
"Control" means the power to direct the management and operating decisions of
an entity, whether through equity ownership, voting rights, contractual
arrangements, or otherwise.

The full text of Apache License 2.0 is available at
https://www.apache.org/licenses/LICENSE-2.0 .

© 2026 [MinerU Team]
```

```text
## MinerU 开源许可协议

MinerU 依据 Apache License 2.0 进行许可，并受以下附加条款约束。除本附加条款
明确修改或补充之处外，您的其他权利与义务均适用 Apache License 2.0 的规定。

**1. 商业许可与门槛**

MinerU 可在无需另行取得商业许可的情况下用于商业用途。但是，如果您及您的
关联方按合并口径计算，满足以下任一条件，则应当在继续该等使用前，从
[MinerU Team] 处取得单独的商业许可：

a. 月活跃用户数（MAU）超过 1 亿；或
b. 月总收入超过 2000 万美元。

**2. 在线服务标识义务**

如果您基于 MinerU 向第三方提供在线服务，您必须在相关产品或服务的操作界面，
或对外公开文档的显著位置，清晰明确地标明其使用了 MinerU。

**3. 协议终止**

凡属于依据第 1 条应当取得单独商业许可而未在继续使用前取得的情形，或者未履行
第 2 条所述标识义务的，本许可及本许可项下授予您的全部权利将自动终止，且许可
方无须另行通知。

**4. 定义**

在本附加条款中，"关联方"是指直接或间接控制您、受您控制，或与您处于共同控制
之下的任何法律实体。
"控制"是指通过股权、表决权、合同安排或其他方式，直接或间接决定某一实体管理
和经营事项的能力。

Apache License 2.0 全文见：https://www.apache.org/licenses/LICENSE-2.0 。

© 2026 [MinerU Team]
```

## RapidOCR model notice

RapidOCR's source code is Apache-2.0. Its OCR model artifacts are derived from
PaddleOCR and are attributed to Baidu and/or the applicable PaddleOCR rights
holders. The package ships a `MODEL_LICENSES.md` with provenance and
redistribution requirements. This repository does not redistribute any model
weights; `install.sh` installs the package, and models are downloaded by the
user at runtime.

## Poppler / pdftotext

Poppler is GPL-2.0-only OR GPL-3.0-only. This repository calls the system
`pdftotext` binary through `subprocess`; it does not modify, link against, or
redistribute Poppler. If you package `pdftotext` into a distribution, evaluate
GPL obligations separately.

## OCRmyPDF

OCRmyPDF is MPL-2.0 (file-level copyleft). This repository calls the CLI; it
does not modify OCRmyPDF source files. If you modify OCRmyPDF, the modified
files remain under MPL-2.0.

## pypdf

GitHub's license detector reports `NOASSERTION` for pypdf because the project
uses a BSD-3-Clause-style license with a custom copyright header. See the
upstream `LICENSE` for the exact text.

## Benchmark fixture texts (CC BY-SA 4.0)

The files under `benchmarks/fixtures/real/` are derivative works of Wikipedia
articles and are licensed under **CC BY-SA 4.0**, not the repository's MIT
license. See `benchmarks/fixtures/real/SOURCES.md` for the source URLs,
retrieval date, modifications, and attribution. If you redistribute those
fixtures, keep the attribution and the CC BY-SA 4.0 license.

## Trademarks

All product names, logos, and trademarks are the property of their respective
owners. Use of a name in this repository does not imply endorsement.
