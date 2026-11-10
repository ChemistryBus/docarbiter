# License FAQ

> This is a plain-language explanation, not legal advice. The upstream `LICENSE` text of each project prevails.

## Q1: Is MinerU Apache-2.0? Can we use it?

**Yes.** MinerU's license is **Apache-2.0 + additional terms** (written in the package metadata as `LicenseRef-MinerU-Open-Source-License`). The additional terms are triggered only in these two cases:

1. You and your affiliates, on a combined basis, have **MAU > 100 million**, or **monthly revenue > $20 million** → a separate commercial license is required;
2. You provide an **online service** to third parties based on MinerU → you must prominently state "Uses MinerU" in the product UI or public documentation.

This project:

- is non-profit and does not provide an online service;
- does not redistribute MinerU code or models;
- only invokes the CLI on the user's local machine through `mineru-doc`.

Therefore the current usage does not trigger the additional terms. **If you turn this collection into an online service in the future**, you will need to mark MinerU in the UI/documentation; if user volume/revenue reaches the thresholds, you will need to contact the MinerU team for a commercial license.

See `THIRD_PARTY_NOTICES.md` for the original text (English + Chinese).

## Q2: Why is PyMuPDF not included?

PyMuPDF is **AGPL-3.0 / commercial dual-licensed**. AGPL's copyleft would drag the whole project into AGPL, which is incompatible with this repository's MIT. When you need low-level PDF control:

- use `pdfplumber` / `pdfminer.six` / `pypdf`, which cover most scenarios;
- users who really need PyMuPDF should install it themselves and assess the license themselves;
- this repository only provides links; it does not install or recommend it.

## Q3: Isn't PDF-Extract-Kit quite good? Why not install it?

It is powerful (layout/tables/formulas), but its license is **AGPL-3.0**. Same as above: links only, no automatic installation. Those who need it decide for themselves.

## Q4: Poppler / pdftotext are GPL. Will that contaminate my project?

This repository **only invokes the system `pdftotext` binary**; it does not modify, link against, or redistribute Poppler. If your project also only calls the command line, it usually does not constitute a derivative work. **If you bundle the `pdftotext` binary into your distribution**, you need to assess GPL obligations separately.

## Q5: OCRmyPDF is MPL-2.0. Can I modify it?

Yes. MPL-2.0 is **file-level copyleft**: OCRmyPDF source files you modify must continue to be released under MPL-2.0; other files in your project are unaffected. This repository only invokes the CLI and does not modify it.

## Q6: Can RapidOCR's models be used commercially directly?

The RapidOCR code is Apache-2.0; the model weights come from PaddleOCR / Baidu, and the package's `MODEL_LICENSES.md` states the source and redistribution requirements. **This repository does not redistribute models**; after the user installs the package, the tool downloads them itself. To redistribute models or provide an online service, read the upstream model license first.

## Q7: Why aren't commercial cloud APIs (LlamaParse / Azure / Google / Adobe / Mathpix) on the default path?

Three reasons:

1. **Data leaves the machine**: documents are sent to a third party;
2. **Per-page billing**: costs are uncontrollable;
3. **Not reproducible**: server-side models change; a score that holds today may not hold tomorrow.

When needed, `docarbiter` can explicitly ask the user whether they agree to upload; by default it does not call them.

## Q8: What license does this repository's own code use?

**MIT**. You can use it commercially, modify it, and redistribute it, as long as you retain the copyright notice. Upstream tools are still bound by their own licenses.

## Q9: If I only call these tools, do I need to open-source my product?

Generally no:

- MIT / Apache-2.0 / BSD / MPL tools: calling them usually does not trigger open-source obligations (MPL only constrains modified files);
- GPL tools (such as Poppler): merely calling the command line usually does not constitute a derivative work; bundling the binary must be assessed separately;
- AGPL tools (PyMuPDF / PDF-Extract-Kit / Ghostscript): this repository does not install or recommend them; if you use them yourself and provide a network service, AGPL obligations may be triggered.

If you are unsure, ask a lawyer, not a README.

## Q10: Where is the official text of MinerU's additional terms?

- Upstream repository: https://github.com/opendatalab/MinerU
- `LICENSE.md` inside the local installation package: `mineru-4.1.7.dist-info/licenses/LICENSE.md`
- This repository: `THIRD_PARTY_NOTICES.md` (English + Chinese original text attached)

> If upstream updates the terms, the `LICENSE.md` in the version you installed prevails.
