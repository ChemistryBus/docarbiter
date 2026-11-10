# 许可证 FAQ

> 本文是通俗说明，不是法律意见。以各上游 `LICENSE` 原文为准。

## Q1：MinerU 是 Apache-2.0 吗？我们能用吗？

**能用。** MinerU 的许可证是 **Apache-2.0 + 附加条款**（包元数据里写作 `LicenseRef-MinerU-Open-Source-License`）。附加条款只在这两种情况下触发：

1. 你及关联方合并口径 **MAU > 1 亿**，或 **月收入 > 2000 万美元** → 需要单独商业许可；
2. 你基于 MinerU 向第三方提供**在线服务** → 必须在产品界面或公开文档显著位置标明「使用了 MinerU」。

本项目：

- 不盈利、不提供在线服务；
- 不重新分发 MinerU 代码或模型；
- 只在用户本机通过 `mineru-doc` 调用 CLI。

因此当前用法不触发附加条款。**如果未来你把本合集做成在线服务**，需要在界面/文档标注 MinerU；如果用户量/收入达到门槛，需要联系 MinerU 团队取得商业许可。

原文（英文 + 中文）见 `THIRD_PARTY_NOTICES.md`。

## Q2：为什么不收录 PyMuPDF？

PyMuPDF 是 **AGPL-3.0 / 商业双许可**。AGPL 的传染性会把整个项目拖入 AGPL，和本仓库的 MIT 不兼容。需要底层 PDF 控制时：

- 用 `pdfplumber` / `pdfminer.six` / `pypdf` 覆盖大部分场景；
- 确实需要 PyMuPDF 的用户，自行安装并自行评估许可；
- 本仓库只给链接，不安装、不推荐。

## Q3：PDF-Extract-Kit 不是很好用吗？为什么不装？

它很强（版面/表格/公式），但许可证是 **AGPL-3.0**。同上：只给链接，不自动安装。需要的人自行决定。

## Q4：Poppler / pdftotext 是 GPL，会不会污染我的项目？

本仓库**只调用系统 `pdftotext` 二进制**，不修改、不链接、不再分发 Poppler。你的项目如果也只是调用命令行，通常不构成衍生作品。**如果你把 `pdftotext` 二进制打包进发行物**，需要单独评估 GPL 义务。

## Q5：OCRmyPDF 是 MPL-2.0，我能改吗？

可以。MPL-2.0 是**文件级 copyleft**：你修改的 OCRmyPDF 源文件要继续以 MPL-2.0 发布；你项目里的其他文件不受影响。本仓库只调用 CLI，不修改。

## Q6：RapidOCR 的模型可以直接商用吗？

RapidOCR 代码是 Apache-2.0；模型权重来自 PaddleOCR / 百度，包内 `MODEL_LICENSES.md` 说明了来源与再分发要求。**本仓库不重新分发模型**；用户安装包后由工具自行下载。要再分发模型或做在线服务，先读上游模型许可。

## Q7：商业云 API（LlamaParse / Azure / Google / Adobe / Mathpix）为什么不在默认路径？

三个原因：

1. **数据离机**：文档会发送到第三方；
2. **按页计费**：成本不可控；
3. **不可复现**：服务端模型会变，今天的分数明天不一定成立。

需要时可以在 `docarbiter` 里显式询问用户是否同意上传；默认不调用。

## Q8：本仓库自己的代码是什么许可？

**MIT**。你可以商用、修改、再分发，只需保留版权声明。上游工具仍按各自许可证约束。

## Q9：我只调用这些工具，需要开源我的产品吗？

一般情况下不需要：

- MIT / Apache-2.0 / BSD / MPL 工具：调用通常不触发开源义务（MPL 只约束被修改的文件）；
- GPL 工具（如 Poppler）：只调用命令行通常不构成衍生作品；打包二进制要单独评估；
- AGPL 工具（PyMuPDF / PDF-Extract-Kit / Ghostscript）：本仓库不安装、不推荐；如果你自行使用并提供网络服务，AGPL 义务可能触发。

拿不准时，问律师，不要问 README。

## Q10：MinerU 附加条款的官方原文在哪？

- 上游仓库：https://github.com/opendatalab/MinerU
- 本机安装包内的 `LICENSE.md`：`mineru-4.1.7.dist-info/licenses/LICENSE.md`
- 本仓库：`THIRD_PARTY_NOTICES.md`（已附英文 + 中文原文）

> 如果上游更新了条款，以你安装版本内的 `LICENSE.md` 为准。
