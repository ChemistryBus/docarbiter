# PDF - 维基百科，自由的百科全书

<https://zh.wikipedia.org/wiki/%E4%BE%BF%E6%90%BA%E5%BC%8F%E6%96%87%E6%A1%A3%E6%A0%BC%E5%BC%8F>

# PDF[编辑]

扩展名 | .pdf 
---|---
互联网媒体类型 | 
- application/pdf,[1]
- application/x-pdf
- application/x-bzpdf
- application/x-gzpdf

类型代码 | PDF [1]（包含一个空格） 
统一类型标识 | com.adobe.pdf 
开发者 | Adobe Inc. (1991—2008年)
ISO (2008年—)

首次发布 | 1993年6月15日 
最新版本 | 
2.0

扩展为 | PDF/A, PDF/E, PDF/UA, PDF/VT, PDF/X 
标准 | ISO 32000-2 
自由格式？ | 是 
网站 | iso 

便携式文档格式（英语：Portable Document Format，缩写：PDF）是一种用独立于应用程序、硬件、操作系统的方式呈现文档的文件格式。[2]每个PDF文件包含固定布局的平面文档的完整描述，包括文本、字形、图形及其他需要显示的信息。PDF文件除平面的文本和图形外，还可能包括逻辑结构元素，注释、表单、图层、富媒体（包括视频内容）之类的交互元素，使用U3D或PRC的三维对象，以及多种其他数据内容。PDF规范还提供了启用这些功能时所需的加密功能、数字签名、文档附件和元数据等。

PDF源自1991年Adobe Systems共同创始人约翰·沃诺克发起的“Camelot项目”。[3]2008年成为ISO标准的一部分，编号ISO 32000，最新的版本ISO 32000-2:2020在2020年十二月发布。

## 历史
[编辑]
Adobe Systems在1993年免费提供了PDF规范[4]，当时与PDF一起竞逐跨平台文档格式的，还包括DjVu（当时仍在开发中）、Envoy、Common Ground Digital Paper、Farallon Replica及Adobe自己本身的 PostScript（.ps）格式。在万维网及HTML文本尚未兴起时，PDF在桌面出版工作流技术当中很受欢迎。PDF起初为Adobe所控制的专有格式，直到2008年7月1日才被官方以开放标准发行，并由国际标准化组织以 ISO 32000-1:2008 发布。[5][6]此后，标准的控制权便移转到了产业专家志愿者所组的ISO委员会底下。2008年，Adobe在 ISO 32000-1 发布了公共专利许可，对于制作、使用、销售及发布PDF兼容的应用所需的专利，皆赋予买断式授权。[7]

PDF 1.7含有一些Adobe所定义的专有技术，如Adobe XML表单结构（XFA）和JavaScript中对Acrobat的扩展。这些技术被ISO 32000-1引用为对于该规范之完整实现不可或缺且规范性的，但是它们并没有被标准化，其规格也只有发布在Adobe的网站上。[8][9][10][11][12]这些技术大部分也没有被热门的PDF第三方实现所支持。

2017年7月28日，发布了ISO 32000-2:2017（PDF 2.0）。ISO 32000-2不将任何专有技术当作是规范性引用文件。[13]

2020年12月14日，发布了ISO 32000-2:2020（PDF 2.0）。在2017版本的基础上包括了对规范性引用的澄清、更正以及其他的一些重要更新。 [14]

## 技术基础
[编辑]
PDF文件通常由矢量图形、文本和位图图形构成。

PDF主要由三项技术组成：

- 派生自PostScript页面描述语言的子集，用以生成和输出图形。
- 字型嵌入/替换系统，可使字型随文件一起传输。
- 结构化的存储系统，用以绑定这些元素和任何相关内容到单个文件，带有适当的资料压缩系统。

### PostScript
[编辑]
PostScript是一种运行于解释器以生成图像的页面描述语言，一个需要大量资源的进程。不仅能处理图形，也具有if及loop之类命令的标准编程语言特性。PDF很大程度上基于PostScript，但做了简化，以移除像这样的流控制特性，还保持着lineto之类的图形命令。

通常，类PostScript的PDF代码产生于PostScript源文件。以PostScript代码输出的图形命令被收集并标记；其中文档所引用的任何文件图像或字体也被收集，然后每一件都被压缩成单个文件。由此，整个的PostScript领域（字体、输出、计量）得以保持完整。

作为一个文档格式，PDF相比较于PostScript有一些优势：

- PDF包含已标记和解析的PostScript源代码，以在修改PDF页面描述中的项与修改所产生的页面造型之间直接保持一致。
- PDF（自1.4版）支持真图形透明度；PostScript不支持。
- PostScript是一种带有隐形全局状态的解释型语言，因此伴随着一页的指令能任何后续页面的表现。因此，PostScript文档中所有先前的页面必须经过处理以决定所给出的页面的正确的表现，而PDF文档中的每一页不受其他因素的影响。结果PDF查看器允许用户迅速跳转到长文档的最后一页，而一个PostScript查看器需要在能够显示目标页面之前继续地处理所有的页面（除可选PostScript文档结构规范已被周密地遵守外）。

PDF 1.6及更高版本支持嵌入PDF文件的交互式3D文档，可以使用U3D、PRC或其他各种3D格式嵌入3D图像。[15][16]

## 技术概括
[编辑]

### 文件结构
[编辑]
PDF文件是COS（"Carousel" Object Structure，Carousel对象结构）格式的子集。COS也伴随着FDF文件。[17]COS树文件主要由对象组成，其中有八种类型：[18]

- 布尔值，表示true或false
- 数字
- 字符串
- 名称
- 数组，对象的指令性集合
- 字典，按名称索引对象的集合
- 字符串流，通常包含大量数据
- 空对象

对象可以是直接（嵌入其他对象）或非直接的。直接对象以对象号及代号编号。称为xref表的索引表赋予每个对象从文件开头起的字节偏移量。[19]这一设计允许有效的随机存取到文件中的对象，还允许无需重写整个文件（增量更新）即可做出小的改动。从PDF 1.5版开始，非直接对象也可位于称为“对象流”的字符串流中。这一增加文件大小的技术有大量小的非直接对象，并且对置标PDF特别有用。

PDF文件有两种输出方式：非线性（非“优化”）和线性（“优化”）。非线性PDF文件比线性PDF文件占用的硬盘空间更小，但由于部分页面数据分散在文件各处，访问速度可能较慢。线性PDF文件（也称“优化”或“web优化”PDF文件）按页面顺序组织数据，使网页浏览器插件无需等待整个文件下载完成即可开始阅读。[20]PDF文件可用Adobe Acrobat软件或QPDF优化。

### 图像模式
[编辑]
图形在PDF中呈现的基本设计是以非常类似于PostScript中的方式，除了PDF 1.4增添的透明度的使用。

PDF图形使用设备独立性笛卡儿坐标系来描述页面的外观。一个PDF页面描述可使用矩阵来缩放、旋转或错切图形元素。PDF中的一个主要概念是图形状态，即是可能会通过页面描述修改、保存或还原的图形参数的集合。PDF有（如在1.6版）24种图形状态属性，其中最重要的有：

#### 矢量图
[编辑]
PDF中的矢量图如同在PostScript当中一样，是由路径组成的。路径通常由直线和多项的贝兹曲线组成，但也可以从文本的外廓构建。不同于PostScript，PDF不允许带直线和曲线的单一路径去组合文本外廓。路径可被描绘、填充或用于剪取。描绘和填充可用任意图形状态中的色彩集，包括式样。

PDF支持多种调色板类型。最简单的是瓷砖式样，其中艺术作品的一部分被指定以被重复地绘制。这可能是彩色瓷砖式样，带有在式样对象中的指定的颜色，或是延迟色别编码到式样已绘制时候的没有颜色的瓷砖式样。从PDF 1.3开始还有了底纹式样, 连续绘制不同的颜色。七种底纹式样中最简单的是轴向底纹（Type 2）和径向底纹（Type 3）。

#### 位图
[编辑]
PDF中的位图（称作Image XObjects）由带相关字符串流的字典呈现。字典描述了图像的属性和包含图像数据的流。（少见的是，位图或许会作为一个内嵌图像被直接嵌入于页面描述。）图像通常出于压缩的目的过滤。PDF中支持的图像过滤器包含了常用的过滤器

- ASCII85Decode 用于把字符串流放入7位ASCII的过滤器
- ASCIIHexDecode 类似于ASCII85Decode，但兼容性低
- FlateDecode 基于RFC 1950及RFC 1951所定义的zlib/deflate算法（亦即gzip，但不是zip）的常用过滤器；引入于PDF 1.2；可用两组预测功能中的一组以进一步兼容zlib/deflate算法：出自TIFF 6.0规格中的Predictor 2和来自PNG规格（RFC 2083）的预测器（过滤器）
- LZWDecode 基于LZW算法的过滤器可用两组预测功能中的一组进一步兼容LZW压缩：出自TIFF 6.0规格中的Predictor 2和来自PNG规格的预测器（过滤器）
- RunLengthDecode 使用游程编码算法和图像指定的过滤器的用于带重复数据的字符串流的简单的压缩算法
- DCTDecode 基于JPEG标准的有损过滤器
- CCITTFaxDecode 基于ITU-T T.4和T.6中定义的Group 3或Group 4 CCITT（ITU-T）传真压缩标准的无损二值（黑白）过滤器
- JBIG2Decode 基于JBIG2标准的有损或无损二值（黑白）过滤器，引入PDF 1.4
- JPXDecode 基于JPEG 2000标准的有损或无损过滤器，引入PDF 1.5

通常PDF中包含的所有图像嵌入于图像，但PDF允许图像数据通过使用外部字符串流或替代图像存储于外部文件。PDF的标准子集，包括PDF/A和PDF/X，禁止这些特性。

#### 文本
[编辑]
文本在PDF中以页面内容字符串流中的“文本元素”呈现出来。一个文本元素指定字符应在指定位置描绘。字符用所选字体源的编码指定。

##### 字体
[编辑]
PDF中的字体对象是对数码字体的描述。可能是字体中的字符的描述，或者是包含嵌入的字体文件。后者叫嵌入字体，前者叫非嵌入字体。所嵌入的字体文件基于广泛使用的标准数码字体文件：Type 1（及其压缩版变种CFF）、TrueType和（自PDF 1.6版起）OpenType。另外PDF支持由PDF图形处理器描述的字体组件中的Type 3变种。

##### Standard Type 1字体（Standard 14字体）
[编辑]
以Standard 14字体著称的四种字体在文档中PDF有特别的意义：

- Times（v3，常规、斜体、粗体和粗斜体）
- Courier（常规、斜体、粗体和粗斜体）
- Helvetica（v3，常规、伪斜体、粗体和粗伪斜体）
- Symbol/Zapf Dingbats

这些字体有时称作Base 14字体。[21]这些字体或有相同度量的合适的替代字体，必须能用在所有PDF阅读器上，而且不必嵌入PDF。[22]PDF查看器必须掌握这些字体度量。否则字体如果没有嵌入PDF就可能会被替换。

##### 编码
[编辑]
文本字符串中，字符用以编码映射字形于当前字体的字符代码（整数）显示。预定义的编码有多种，包括WinAnsi、MacRoman，以及大量东亚语言编码，而且字体可以有自己的编码。（即使WinAnsi和MacRoman编码取自Windows和Macintosh操作系统中历史上的专有编码，用这类编码的内容在任何平台上都运行的好。）PDF可以指定可以使用的预定义的编码、字体内置编码，或者提供预定义或内置编码的查询表（不对TrueType字体推荐）。[23]PDF中的编码机制是为Type 1字体设计的，而且应用到TrueType字体的规则是复合的。

对于大型字体或者带非标准字形的字体，特殊编码Identity-H（用于横写）或Identity-V（用于竖写）被使用。如果关于字符的语义信息被预定义，这类字体有必要提供ToUnicode表。

#### 透明度
[编辑]
PDF的原始图像模型像PostScript的opaque：页面上描绘的每个对象完全替换先前在同一位置标记的任何东西。在PDF 1.4中图像模型被扩展以允许透明度。使用透明度的时候，新对象与先前标记的对象相互作用产生混合的特效。透明度添加到PDF由写到PDF 1.3及早期的规格的产品中被忽略设计的新的扩展方法完成。结果，使用少量透明度的文件在旧的查看器中可能会以被接受地视图查看，但大量用透明度的文件在旧的查看器中会显示不正确而没警告。

透明度扩展基于透明度组、混合模式、形状和alpha的关键概念。这一模式紧密对应Adobe Illustrator 9的特性。混合模式基于当时Adobe Photoshop所用的。PDF 1.4规格出版的时候，用于计算混合模式的公式被Adobe保密。此后它们被公布。[24]

PDF规格中透明度组的概念独立于Adobe Illustrator之类的应用中已有的“组”或“层”的概念。那些反映对象之上的逻辑关系的分组在编辑那些对象的时候有意义，但不是图像模型的一部分。

### 交互式元素
[编辑]
PDF文件或许包含注释、表单、视频和Flash动画之类的交互式元素。

富媒体PDF是一个用来描述可以嵌入或链入PDF的交互式内容的术语。这一内容必须用Flash文件格式提供。Adobe收购Macromedia的时候，公司的主业是Flash，而且Flash播放器被嵌入Adobe Acrobat，Adobe Reader，移除了用于Flash、QuickTime或Windows Media之类第三方插件的需。不幸的是，这造成QuickTime视频从PDF被禁这样与苹果公司的裂痕。富媒体专家Robert Connolly相信这一事件引发了苹果与Adobe之间Flash iPhone/iPad争论之上的冲突。富媒体PDF将不在苹果的iPad之类的iOS设备上操作，而且交互性受到限制。

交互式表单是一个添加表单到PDF文件格式的机制。

PDF当前支持用于集成数据和PDF表单的两种不同的办法。两种格式今天并存于PDF规格：[25][26][27][28]

- AcroForms（又叫Acrobat forms）引入PDF 1.2格式规格并包含于所有后来的PDF规格。
- Adobe XML表单架构（XFA）的表单，引入PDF 1.5格式规格。XFA规格没有包含于PDF规格，仅仅作为可选特性参考。Adobe XFA表单不与AcroForms兼容。[29]

#### AcroForms
[编辑]
AcroForms于PDF 1.2格式被引入。AcroForms准许使用对象（如文本框、选择钮等）及一些代码（如JavaScript）。

在标准PDF动作类型之外，交互式形式（AcroForms）支持提交、重置和导入数据。“提交”动作传送所选表单字段和值的名称给指定的统一资源定为符（URL）。交互式表单字段名称和值或许会被以任意格式提交（取决于输出格式、提交的PDF和XFDF旗标的设置）：[25]

- HTML表单格式（自PDF 1.5起用HTML 4.01规格；1.2起用HTML 2.0）
- 表单数据格式（Forms Data Format，FDF）
- XML表单数据格式（XML Forms Data Format，XFDF）（扩展XFDF规格，2.0版；自PDF 1.5起被支持；在PDF 1.4中替换XML表单提交格式定义）
- PDF（整个文档可以被提交，而不是单独的字段和值）。（PDF 1.4中定义）

AcroForms可以保持表单字段于包含key:value组合的外部的单独的文件。内部的文件可能使用FDF和XFDF文件。[30][31][32]使用权（UR）签名定义导入表单数据文件以FDF、XFDF及文本（CSV/TSV）格式，及以FDF及XFDF格式从数据文件导出文件的权利。[25]

##### 表单数据格式（FDF）
[编辑] 
扩展名 | 
.fdf

---|---
互联网媒体类型 | 
application/vnd.fdf[33]

类型代码 | 'FDF' 
开发者 | Adobe Systems 
首次发布 | 1996年（PDF 1.2） 
扩展自 
扩展为 | XFDF 
标准 | ISO 32000-1:2008 
免费格式？ | 是 

表单数据格式（Forms Data Format，FDF）基于PDF，使用同样的句法和基本上一样的文件结构，但比PDF简单，自从FDF文档的主体由只有一个要求的对象组成开始。表单数据格式定义于PDF规格（自PDF 1.2起）。表单数据格式可在表单数据到服务器、接收响应和组合到交互式表单的时候被使用。还可以被用来导出表单数据到能被导回到相应的PDF交互式表单的单独的文件。从PDF 1.3开始，FDF可被用来定义用于从所应用的PDF文档分开的注释的容器。FDF通常封装X.509证书之类的信息、要求证书、设置目录、设置时间戳服务器和为网络传输嵌入PDF文件。[32]FDF使用MIME内容类型application/vnd.fdf、文件扩展名.fdf，并在Mac OS使用文件类型'FDF'。[25]导入和导出独立FDF文件的支持没有被自由或免费PDF软件广泛的实现。例如，Evince、Okular、Poppler、KPDF或Sumatra PDF没有导入/导出的支持，然而，Evince、Okular和Popller填入PDF Acroforms并在PDF中保存已填写数据。导入独立FDF文件的支持在Adobe Reader中得到实现；导入和导出支持（包括在PDF中保存FDF数据）作为示例在Foxit Reader和PDF-XChange Viewer Free中得到实现；PDF文件中FDF数据的保存也被pdftk支持。

##### XML表单数据格式（XFDF）
[编辑] 
扩展名 | 
.xfdf

---|---
互联网媒体类型 | 
application/vnd.adobe.xfdf[34]

类型代码 | 'XFDF' 
开发者 | Adobe Systems 
首次发布 | 2003年7月（引用于PDF 1.5） 
最新版本 | 
3.0

2009年8月

扩展自 | PDF、FDF、XML 
标准 | ISO 19444-1:2016 

XML表单数据格式（XFDF，XML Forms Data Format）是表单数据格式的XML版，但XFDF只执行FDF内含表单及注释的子集。FDF字典中的一些词条没有等价于XFDF的，像是状态、编码、JavaScript、页面关键字、嵌入式FDF、差异和目标。此外，XFDF不允许在基于已给定的数据的新页面大量生成或者添加；就像使用FDF文件的时候能被完成的一样。XFDF规格被引用于（但不包含于）PDF 1.5规格（及其以后的版本）。它被单独描述为“XML表单数据结构规格”（XML Forms Data Format Specification）。[31]PDF 1.4规格允许以XML格式提交表单，但在PDF 1.5规格中以XFDF格式提交取代。XFDF符合XML标准。

到2016年12月，XFDF 3.0在ISO 19444-1:2016 – Document management – XML Forms Data Format – Part 1: Use of ISO 32000-2 (XFDF 3.0)的名义下成为ISO/IEC标准。[35]这个标准是ISO 32000-2的规范性参考资料。

XFDF可用以和FDF相等的方式，如提交表单数据给服务器，做出修订，然后返回，并且新表单数据被导入到交互式表单。它还可以用来导出表单数据到能被导回到相应的PDF交互式表单的单独的文件。

#### Adobe XML表单架构（XFA）
[编辑]
PDF 1.5格式中，Adobe Systems引入了新的、专有的表单格式，名为Adobe XML表单架构（XFA）。XFA 2.02引用在PDF 1.5规格（及以后的版本），但单独描述为《Adobe XML Forms Architecture (XFA) Specification》，有多个版本。[36]XFA规格没有包括在ISO 32000-1 PDF 1.7并仅仅作为由Adobe创建的外部专有规格引用。在ISO 32000-2（PDF 2.0）当中被弃用。

Adobe XFA表单不与AcroForms兼容。Adobe Reader包含使用XFA表单的“禁用特性”，仅在打开只来自Adobe的可行的技术创建的PDF文档时激活。[37][38]XFA Forms不兼容于Adobe Reader 6以前的版本。

XFA表单可创建或用作PDF文件或作为XDP（XML数据包）文件。PDF中XFA源的格式由XML数据包规格描述。[25]XDP可能作为单独的文档，也可能在PDF文档的内部携带。XDP提供打包周边XML容器内部的表单组件的机制。XDP也可以打包一个PDF文件，伴随XML表单和模板数据。[36]PDF可能包含XFA（在XDP格式中），XFA也可能包含PDF。[36]在用于XFA表单XFA（XML表单架构）语法从一个应用移到另一个应用的时候，它们必须以XML数据包封装。[39]

当PDF和XFA结合在一起，结果是任意页面中的XFA表单覆盖了PDF背景。这一架构有时被提作XFAF（XFA Foreground，XFA前景）。替代方法是直接在XFA（不用PDF，或者只用带有PDF标记的最小构造XFA的容器的“外挂PDF”，或用静态XFA表单的预渲染描述作为PDF）展开所有表单，包括样板文件。这有时被称为全XFA。[39]

PDF 1.5开始，可变文本字段的文本内容，以及标记注解可能包含格式信息（样式信息）。这些富文本字符串是符合XML表单架构规格2.02（本身是XHTML 1.0规格的子集）定义的富文本惯例的XML文档，扩展了CSS2样式属性中受限的设置。[25]PDF 1.6中，PDF支持XML表单架构（XFA）规格2.2定义的富文本元素和属性。PDF 1.7中，PDF支持XML表单架构（XFA）规格2.4定义的富文本元素和属性。[25]

多数PDF处理器不处理XFA内容。生成外挂PDF的时候会被建议包含于PDF标记的一个简单的单页PDF图像显示警告（如：“为了查看本文档的全部内容，你需要新版PDF查看器”等。）能渲染XFA内容的PDF处理器应该不现实警示页面图像或者以动态表单内容迅速替换。[40]带有一些XFA渲染功能支持的PDF软件的例子包括Adobe Reader for Windows、Linux、Mac OS X（但不是Adobe Reader Mobile for Android / iOS）或Nuance PDF Reader。

### 逻辑架构与可读性
[编辑]
“标签”PDF（ISO 32000-1:2008 14.8）含有文档架构和语义信息，以允许可靠的文字抽取及使用。技术上来说，标签PDF是建立在PDF 1.3 所引入的逻辑结构框架上，对于其格式的程式化使用 。标签PDF定义了一组标准结构类型及属性，允许页面内容（文本、图形和图片）之后被提取并再利用于其他用途。[41]

当PDF文件仅供打印时，并不要求支持标签PDF。因为此一特色是非必须的，且ISO 32000-1对于标签PDF的规则相对模糊，所以在消费性设备当中，包括辅助技术（AT），标签PDF的支持参差不齐。[42]

一个专门针对可读性、为ISO标准之子集的PDF规格：PDF/UA于2012年首次发布。

W3C的PDF无障碍技术指出，PDF的阅读顺序主要由文件元素的标签顺序决定；若阅读顺序不正确，键盘与辅助技术用户可能无法理解内容。[43]PDFtoMDConverter发布的一项第一方基准覆盖40份PDF与四种转换系统，并将阅读顺序与文字、OCR、标题、表格、Markdown解析成功率及执行时间分开报告；结果仅适用于该基准所列资料集、系统与版本。[44]

### 安全和签名
[编辑]
一份PDF文件可能以用于验证的担保或者数字签名加密。

由Acrobat PDF提供的标准担保以两种不同的方法及两种不同的密码组成，用户密码，加密文件并阻止开启；所有者密码，指定即使文档被解密的时候应该被限制的操作，可以包括：打印、从文档复制文本和图像、修饰文档，或者添加或删除文本注释和AcroForm字段。用户密码（控制开启）加密文件并要求密码破解以去除，难度取决于密码长度及加密算法——它可能非常安全（假设好的密码及加密算法没有已知的攻击手法）。所有者密码（控制操作）不加密文件，相反取决于客户端软件以遵循这些限制，并且不安全。所有者密码可以被许多通常可用的PDF破解软件移除，包括一些自由的在线服务。[45]由此，文档作者放在PDF文档中的使用限制不安全，而且不能在一旦文件被散布时保证；这一危险在使用Adobe Acrobat软件以创建或编辑PDF文件应用这类限制的时候显现出来。

即使没有移除密码，许多免费或开源PDF阅读器忽略权限“保护”并允许用户打印或者做文本摘要的复制，就像文档没被密码保护限制一样。

一些解决方案像Adobe的LiveCycle Rights Management更强化信息权利管理的方式，不仅能限制谁能打开文档，而且以标准的安全处理程序做不到的方式可靠的执行权限。

#### 使用权
[编辑]
从PDF 1.5起，使用权（UR）签名用来启用在一些PDF查看器应用中不是默认的附加的交互式特性。这一签名用来验证由真实的授权机构赋予的许可。例如，它可以允许用户：[25]

- 保存伴有修订表单和/或注释数据的PDF文档
- 从FDF、XFDF和文本（CSV/TSV）格式中的数据文件导入
- 从FDF和XFDF格式中的数据文件导出
- 从数据提交
- 从命名的页面模板具体呈现新页面
- 应用一个数码签名到已有的数字签名表单字段
- 创建、删除、修正、复制、导入、导出注释

例如，Adobe Systems在Adobe Reader中授权启用附加特性，使用公钥密码学。Adobe Reader使用从一个Adobe授权的权威认证的验证那个签名。PDF 1.5规格宣称其他PDF阅读器应用可以为他们自己的目的自由使用这一相同机制。[25]

### 文件附件
[编辑]
PDF文件可以有文档级和页面级的文件附件，读者可访问并打开或存储于本地的文件系统。PDF附件可作为示例用pdftk加到已有的PDF文件。Adobe Reader提供对附件的支持，而且基于Poppler的阅读器如Evince或Okular也有对文档级附件的支持。

### 元数据
[编辑]
PDF文件可包含两种类型的元数据。[46]第一种是文档信息字典，一套像作者、标题、主题、创建及更新日期的关键字/值字段。这存储于可选的文件尾部。有一小组字段是有定义的，而且如果有需要，可以用附加的文本字段扩充。

后来在PDF 1.4中，对元数据流的支持被加入，用可扩展元数据平台（XMP）来添加像在其他文件格式那样的基于XML标准的可扩展的元数据。这允许元数据附加到文档中的任何字符串流，诸如关于嵌入式插图的说明，以及整个文档（附加到文档目录），使用可扩展的纲要。

## 相关技术
[编辑]

### Mars
[编辑]
Adobe曾探索基于XML的下一代PDF，代号Mars。[47]

Mars的图形元素的格式有时简单地描述为SVG，[48]但根据2007年11月的0.8版草案规格（§3 Mars SVG Support）这一格式实际上仅仅是接近于SVG：它同时包含SVG新增和移除的部分，因此一般不可被标准SVG工具查看或创建：一些东西在SVG查看器和Mars查看器之间看起来明显不同。

Adobe Systems于2008年停止开发Mars。[49]

## 技术问题
[编辑]

### 扫描的文档
[编辑]
由扫描仪硬拷贝文档创建的PDF文件包含原始文本没有由相同的文档直接创建的PDF文件那样相同的架构。扫描的文档原本地包含了文档的图片，没有关于文本的信息。只要用户可以看到它只是另一个PDF文件，带有从其他任意地方来的不能区分的名称和扩展名；好的扫描仪或许会精确地视作与原生的PDF文件相同，即使是视觉上质量很差的文件，常常带有扭曲的页面，给出了其本性。然而，文件大小会明显不同，而且不能搜索文本。对于精确质量的扫描可以用带光学字符识别（OCR）的合适的软件识别文档中的文本，并嵌入文档中而使其可以检索，取决于OCR的准确性。

### 可读性
[编辑]
PDF文件可专门为让残疾人阅读而创建。[50][51][52][53][54]截至2014年[update]PDF文件格式在使用中可以包含标签（XML）、替换文本、标题、音频描述等。置标PDF在PDF/A-1a规格中被要求。[55][56]一些软件可以自动生成置标PDF，但这个特性不被默认启用。[57][58]常见的屏幕阅读器，包括JAWS、Window-Eyes、Hal和Kurzweil 1000及3000可以朗读置标PDF，就像Acrobat和Acrobat Reader后来的版本一样。[59][60][61]此外，置标PDF可为有视觉障碍的读者重排和放大。问题仍存在于给旧版PDF和从扫描的文档生成的PDF加标记。这些情况下，可读性标记和重排就不可用，而且必须手动或用OCR技术处理。这些过程对于一些残疾人是达不到的。

对PDF可读性的一个重大挑战是PDF文档有三种不同的视图，取决于文档的创建，会和其他视图相矛盾。这些视图有：物理视图、标记视图和内容视图。物理视图可以显示和打印（多数人认为的PDF文档）。标记视图是屏幕阅读器和其他访问技术用来给有障碍的用户带来高质量导航和阅读体验的。内容视图基于PDF内容字符串流中的对象的物理排列，并可能由不完全支持标记视图的软件显示，如Adobe Reader的Reflow特性。

基于ISO 32000-1的可阅读PDF国际标准PDF/UA在2012年以ISO 14289-1发布，并为可阅读PDF技术建立规范的语言。

### 病毒和漏洞
[编辑]
PDF附件带病毒最先发现于2001年。这种名为OUTLOOK.PDFWorm或Peachy的病毒，会通过Microsoft Outlook以附件的形式将自己发送至Adobe PDF文件。然后会用Adobe Acrobat将自身激活，但不会被Acrobat Reader激活。[62]

随着时间推移，新的漏洞在Adobe Reader的多个版本被发现，[63]促使企业发出安全性修复。其他PDF阅读器也容易受到影响。一个恶化的因素是PDF阅读器会被配置在网页嵌入PDF时候自动启动，为攻击带来了载体。如果恶意的网页包含一份利用PDF的漏洞感染的PDF文件，系统会无法抵抗，即使浏览器是安全的。其中一些漏洞是由于PDF标准允许PDF文档用JavaScript脚本指令的结果。在PDF阅读器中禁止执行JavaScript有助于缓解那些未来的漏洞，即使这不阻止PDF查看器其他部分的漏洞。安全专家称JavaScript对于PDF阅读器来说不是基本的，而且出于禁止JavaScript的安全保障胜过任何造成的兼容性问题。[64]阻止PDF文件漏洞的一种方式是有本地或网络服务能在阅读前把文件转换成其他格式。[65]

2010年3月30日安全专家Didier Stevens报告Adobe Reader和福昕阅读器有如果用户经询问允许启动时运行恶意可执行文件的漏洞。[66]

### 使用限制和显示
[编辑]
PDF可能会被加密，以致查看或编辑内容时会要求输入密码。PDF参考书同时定义40位和128位加密，都运用RC4和MD5的复杂系统。PDF参考书还定义第三方可以制定他们自己的PDF加密系统的方式。

PDF文件或许还包含嵌入的DRM限制，提供限制复制、编辑或打印的进一步控制。复制、编辑或打印的限制取决于阅读软件遵循他们，因此他们提供的安全机制是有限的。

PDF参考书有面向最终用户概览的技术细节。[67]就像HTML文件一样，PDF文件可以向网络服务器提交信息。这可以被用来追踪客户端PC的IP地址，这一过程被称作背景连线通信。Acrobat Reader升级到7.0.5以后，用户会被提示“...via a dialogue box that the author of the file is auditing usage of the file, and be offered the option of continuing”。[68]

Adobe通过LiveCycle安全服务器提供针对特定文档设置安全策略的方法。这可以包括要求用户认证并限制文档可被离线打开的时候可以被访问或者加载的时期。PDF文档一旦被绑定到策略服务器和指定策略，这一策略可以被所有者更改或撤销。这一策略控制文档，否则就是“在自然状态下”。每个文档打开或关闭事件也可以被策略服务器追踪。策略服务器可以由个人设置，或Adobe通过Adobe在线服务提供公共服务。和其他DRM形式一样，依附这些策略和限制有可能会，也有可能不会被阅读器软件执行。

### 默认的显示设置
[编辑]
PDF文档可以包含显示设置，包括页面显示输出和缩放级别。打开文档的时候Adobe Reader用这些设置去替换用户的默认设置。[69]免费的Adobe Reader不能移除这类限制。

## 内容
[编辑]
PDF文件通常混合了矢量图形、文本和位图。PDF的基本内容包括：

- 文本存储为内容字符串（就是不是文本本身）
- 由图形和线条组成的用于说明和设计的矢量图形
- 由照片和其他类型的图片组成的位图

在近期PDF标准修订中，PDF文档还支持链接（文档内部或网页）、表单、JavaScript（可通过Acrobat 3.0的插件启用），或者其他任意类型的能用插件控制的可嵌入内容。

PDF 1.6支持互动式3D文档嵌入PDF——3D绘图可用U3D或PRC及其他多种格式嵌入。[70][71]

在电脑屏幕上看起来相似的两个PDF文件有可能大小不同。例如，一个高分辨率位图比低分辨率的占更多的存储空间。通常更高的分辨率更适宜打印文档而不是显示于屏幕。其他可能影响文件大小的可能有嵌入全部字体，尤其是东亚字体，以及将文字存为图片。

## 软件
[编辑]
有许多软件选项用来创建PDF，包括内置于Mac OS X及多数Linux发行版、LibreOffice、Microsoft Office 2016、[72]WordPerfect 9、Scribus许多适用于Microsoft Windows的PDF打印驱动、pdfTeX排版系统、DocBook PDF工具、围绕Ghostscript及Adobe Acrobat本身开发的应用以及Adobe FrameMaker的PDF排印功能。Google的在线办公包Google Docs也允许上传、保存为PDF。

光栅图像处理器（RIPs）用于转换PDF文件为位图格式以适应于成像在纸上及其他媒体的打印机、数字生产用印刷机以及一种被称为栅格化的进程中的印前。有直接处理PDF能力的RIP包括在出自Adobe Systems和Jaws[73]的Adobe PDF排印引擎[74]与出自Global Graphics的Harlequin RIP当中。

有一些软件可以直接创建空白的PDF文档，例如Adobe官方的Adobe Acrobat DC，但是通常意义不大；因为Adobe Acrobat并不擅长于对文档进行排版。

因为PDF具有完美展现文件原貌的功能，因此市面上也有一部分软件并非为PDF而生，但是通过一些开发库或者图形绘制框架也具有PDF的导出功能。

此章节需要扩充。 (2010年7月)

一些用于编辑PDF文件的特殊软件，通过受很多限制并且比创建和编辑标准可编辑文档格式更昂贵的选择。Inkscape 0.46及以后版本允许通过Poppler加入中间的转译步骤编辑PDF。

Adobe Acrobat DC允许用户对一个未加密的PDF文件或者具有相关权限用户对PDF文件进行编辑，同时还自带了OCR识别、注释、表单预备、合并，数字签名等十分完善的功能[75]

Serif PagePlus可打开、编辑和保存已有的PDF文档，以及软件包中创建的文档的发布。

Microsoft Office Word也支持打开、编辑和保存已有的PDF文档的编辑功能。

Enfocus PitStop Pro，Acrobat的插件，允许PDF文件的手动和自动编辑，[76]同时免费的Enfocus Browser可以使编辑PDF的低级别架构成为可能。[77]

大多数的TeX文件经过编译系统后默认输出格式为PDF文件

### 注释
[编辑]
Adobe Acrobat是允许用户给已创建的PDF文件注释、高亮和添加笔记的专有软件的一个案例。作为自由软件可用的（GNU通用公共许可协议许可下）一个UNIX应用是PDFedit。另一个GPL授权的原生UNIX应用是Xournal。Xournal允许以不同的字体和颜色注释，以及用于为文本或段落的快速下划及高亮线条的规则。Xournal还有一个用于方形、矩形和圆形的形状识别工具。Xournal中的注释可以被移动、复制或粘贴。免费软件福昕阅读器，适用于Microsoft Windows，允许注释文档。Tracker Software的PDF-XChange Viewer的免费版允许不受限制的注释和标记。苹果Mac OS X内置PDF阅读器Preview也可以像免费软件Skim那样注释，后者支持与LaTeX、SyncTeX和PDFSync集成，以及与BibDesk参考文献管理软件集成。免费软件Qiqqa可以创建总结所有注释的报告，而且笔记通过他们的PDF库做出来。

对于移动版的注释，iAnnotate PDF（来自Branchfire）和GoodReader（来自Aji）允许对PDF注释以及导出注释的摘要。

在PDF被期望拥有纸质文档的全部功能的地方，墨水注释会被要求。一些接受来自鼠标的墨水输入的程序可能不足以对应平板上的手写输入。PC上已有的解决方案包括PDF Annotator和Qiqqa。

### 其他
[编辑]
PDF软件作为在线服务的例子包括用于查看和存储的Scribd、用于在线编辑的Pdfvue和用于PDF转换的Zamzar。

1993年出自Global Graphics的Jaws位图处理器成为第一个不用转换到其他格式原生产生PDF的销售用的印前RIP。公司在1997年给他们的Harlequin RIP发布了一个有同样兼容性的更新。[78]

爱克发-吉华1997年推介并出售Apogee，第一个基于PDF的印前工作流系统。

许多商业的胶印机接受递交发布就绪的PDF文件作为印刷来源，特别是PDF/X-1a子集和相同的变种。[79]发布就绪的PDF文件的提交是对接收已收集本地文件工作的不确定性需求的替代。

PDF被选为Mac OS X的“本地”元文件格式，取代早期Mac OS的PICT格式。Quartz图形层的图像模式基于Display PostScript和PDF共有的模式，产生了昵称Display PDF。Preview应用与Safari网页浏览器2.0及以后版本都可以显示PDF文件。对PDF的系统级支持使得Mac OS X应用可以自动创建PDF文档，给它们提供OS标准的打印架构支持。文件可以按文件标头输出为PDF 1.3格式。在Mac OS X 10.0到10.3版截图时，图像也可以截取为PDF；后来的版本保存截图为PNG文件，虽然这一行为若有需要可以重新设置为PDF。

一些桌面打印机也支持直接打印PDF，可以不用额外的辅助生成PDF数据。目前，所有PDF兼容打印机也支持PostScript，但多数PostScript打印机不直接支持PDF打印[来源请求]。

自由软件基金会曾认为他们的一个高优先级计划“提供自由、高质量和全功能的一组软件库及程序实现PDF文件格式及ISO 32000标准的相关技术”。[80][81]而在2011年，GNU PDF计划从“高优先级”列表中被移除，因为Poppler库的完善，[82]激励了像Evince之类的应用与GNOME桌面环境的广泛应用。Poppler基于Xpdf[83][84]代码。PDF软件列表亦列出可用的商业开发用软件库。

Apache软件基金会的Apache PDFBox计划是一款用于处理PDF文档的开放源代码Java库。PDFBox以Apache许可证授权发布。[85]

Apple开发者早期使用Quartz的CGPDFDocument（页面存档备份，存于互联网档案馆）来绘制一个PDF文档，但是因为使用较为底层的图形库绘制PDF文档和查看十分麻烦，因此在2017年的WWDC大会上Apple引进了PDFKit （页面存档备份，存于互联网档案馆）来让开发者在Apple产品的操作系统上让自己的App支持绘制，查看，标注PDF等等功能[86]

## 参考文献
[编辑]
- ^ 跳转到： 1.0 1.1 Hardy, M.; Masinter, L.; Markovic, D.; Johnson, D.; Bailey, M.. The application/pdf Media Type. IETF. 2017年3月. . RFC 8118.
- ^ Adobe Systems Incorporated, PDF Reference, Sixth edition, version 1.23 (30 MB) （页面存档备份，存于互联网档案馆）, Nov 2006, p. 33.
- ^ Warnock, J. The Camelot Project (PDF). PlanetPDF. 1991 [2014-05-27]. （原始内容存档 (PDF)于2009-03-04）.This document describes the base technology and ideas behind the project named “Camelot.” This project’s goal is to solve a fundamental problem [...] there is no universal way to communicate and view ... printed information electronically.

- ^ The Camelot Project (PDF). [2014-05-27]. （原始内容存档 (PDF)于2009-03-04）.
- ^ ISO 32000-1:2008 - Document management – Portable document format – Part 1: PDF 1.7. Iso.org. 2008-07-01 [2010-02-21]. （原始内容存档于2010-12-06）.
- ^ Orion, Egan. PDF 1.7 is approved as ISO 32000. The Inquirer. The Inquirer. 2007-12-05 [2007-12-05]. （原始内容存档于2007-12-13）.; Adobe wins backing for PDF 1.7. vnunet.com. [2015-01-18]. （原始内容存档于2007-12-20）.
- ^ Adobe Systems Incorporated, Public Patent License, ISO 32000-1: 2008 – PDF 1.7 (PDF), 2008 [2011-07-06], （原始内容存档 (PDF)于2020-10-28）
- ^ Guide for the procurement of standards-based ICT – Elements of Good Practice, Against lock-in: building open ICT systems by making better use of standards in public procurement. European Commission. 2013-06-25 [2013-10-20]. （原始内容存档于2020-09-19）.Example: ISO/IEC 29500, ISO/IEC 26300 and ISO 32000 for document formats reference information that is not accessible by all parties (references to proprietary technology and brand names, incomplete scope or dead web links).

- ^ ISO/TC 171/SC 2/WG 8 N 603 – Meeting Report (PDF), 2011-06-27 [2014-05-27], （原始内容存档 (PDF)于2012-11-26）,XFA is not to be ISO standard just yet. ... The Committee urges Adobe Systems to submit the XFA Specification, XML Forms Architecture (XFA), to ISO for standardization ... The Committee is concerned about the stability of the XFA specification ... Part 2 will reference XFA 3.1

- ^ Embedding and publishing interactive, 3-dimensional, scientificfigures in Portable Document Format (PDF) files. [2013-10-20]. （原始内容存档于2016-03-04）.... the implementation of the U3D standard was not complete and proprietary extensions were used.

- ^ Leonard Rosenthol, Adobe Systems. PDF and Standards (PDF). 2012 [2013-10-20]. （原始内容 (PDF)存档于2013-09-02）.
- ^ Duff Johnson, Is PDF an open standard? - Adobe Reader is the de facto Standard, not PDF, 2010-06-10 [2014-01-19], （原始内容存档于2016-04-16）
- ^ ISO 32000-2 – Document management -- Portable document format -- Part 2: PDF 2.0. www.iso.org. [2017-07-28]. （原始内容存档于2020-12-10） （英语）.
- ^ Johnson, Duff. ISO 32000-2:2020 is now available (PDF). 2020-12-14 [2022-12-21]. （原始内容存档 (PDF)于2022-12-04） （美国英语）.
- ^ 3D supported formats. 2022-12-11 [2022-12-21]. （原始内容存档于2022-12-21）.
- ^ Acrobat SDK. opensource.adobe.com. [2022-12-21]. （原始内容存档于2023-03-04）.
- ^ 存档副本. [2015-01-20]. （原始内容存档于2020-05-08）.
- ^ Adobe Systems, PDF Reference, p. 51.
- ^ Adobe Systems, PDF Reference, pp. 39–40.
- ^ Adobe Developer Connection: PDF Reference and Adobe Extensions to the PDF Specification. Adobe Systems. [2010-12-13]. （原始内容存档于2010-12-03）.
- ^ Adobe Acrobat Base 14 Fonts. [2015-01-20]. （原始内容存档于2016-06-14）.
- ^ The PDF Font Aquarium (PDF). [2015-01-20]. （原始内容存档 (PDF)于2007-06-14）.
- ^ PDF Referencem Sixth Edition, version 1.7, table 5.11 (PDF). [2015-01-18]. （原始内容存档 (PDF)于2020-12-04）.
- ^ PDF Blend Modes Addendum (PDF). [2015-01-20]. （原始内容存档 (PDF)于2016-04-17）.
- ^ 跳转到： 25.0 25.1 25.2 25.3 25.4 25.5 25.6 25.7 25.8 Adobe Systems Incorporated, Document Management – Portable Document Format – Part 1: PDF 1.7, First Edition (PDF), 2008-07-01 [2010-02-19], （原始内容存档 (PDF)于2010-04-09）
- ^ Gnu PDF - PDF Knowledge - Forms Data Format. [2010-02-19]. （原始内容存档于2013-01-01）.
- ^ About PDF forms. [2010-02-19]. （原始内容存档于2011-04-29）.
- ^ Convert XFA Form to AcroForm?. 2008 [2010-02-19]. （原始内容存档于2018-11-18）.
- ^ Migrating from Adobe Acrobat forms to XML forms. [2010-02-22]. （原始内容存档于2010-10-06）.
- ^ Adobe Systems Incorporated. Using Acrobat forms and form data on the web. 2007-10-15 [2010-02-19]. （原始内容存档于2021-02-24）.
- ^ 跳转到： 31.0 31.1 XML Forms Data Format Specification, version 2 (PDF), September 2007 [2010-02-19], （原始内容 (PDF)存档于2009-12-23）
- ^ 跳转到： 32.0 32.1 FDF Data Exchange Specification (PDF), 2007-02-08 [2010-02-19], （原始内容存档 (PDF)于2010-05-24）
- ^ IANA Application Media Types - vnd.fdf, [2010-02-22], （原始内容存档于2011-08-22）
- ^ IANA Application Media Types - Vendor Tree - vnd.adobe.xfdf, [2010-02-22], （原始内容存档于2021-02-24）
- ^ ISO 19444-1:2016 – Document management -- XML Forms Data Format -- Part 1: Use of ISO 32000-2 (XFDF 3.0). www.iso.org. [2017-02-28]. （原始内容存档于2021-02-24） （英语）.
- ^ 跳转到： 36.0 36.1 36.2 Adobe Systems Incorporated. Adobe XML Forms Architecture (XFA). [2010-02-19]. （原始内容存档于2009-12-23）.
- ^ Adobe Reader - Software license agreement (PDF), [2010-02-19], （原始内容存档 (PDF)于2012-11-26）
- ^ LiveCycle Reader Extensions ES features and benefits. [2010-02-19]. （原始内容存档于2009-12-19）.
- ^ 跳转到： 39.0 39.1 XML Forms Architecture (XFA) Specification Version 2.5 (PDF), 2007-06-08 [2010-02-19], （原始内容 (PDF)存档于2009-12-23）
- ^ XML Forms Architecture (XFA) Specification Version 3.3 (PDF), 2012-01-09 [2014-04-09], （原始内容 (PDF)存档于2015-07-06）
- ^ What is Tagged PDF?. [2015-01-20]. （原始内容存档于2004-08-07）.
- ^ Is PDF Accessible?. [2015-01-20]. （原始内容存档于2014-12-22）.
- ^ PDF3: Ensuring correct tab and reading order in PDF documents. World Wide Web Consortium. [2026-10-02] （英语）.
- ^ Best PDF to Markdown Converter: Benchmarking OCR, Tables and Reading Order. PDFtoMDConverter. 2026-07-31 [2026-10-02] （英语）.
- ^ FreeMyPDF - A website that removes PDF user password restrictions. [2015-01-20]. （原始内容存档于2021-02-20）.
- ^ Adobe PDF reference version 1.7 （页面存档备份，存于互联网档案馆）, section 10.2
- ^ Jackson, Joab. Adobe plunges PDF into XML. Government Computer News. 2006-12-07 [2008-01-12]. （原始内容存档于2008-02-16）.
- ^ Adobe Systems. Mars. [2014-03-17]. （原始内容存档于2020-09-20）.
- ^ Adobe Labs - Mars Project. [2011-05-12]. （原始内容存档于2011-01-02）.
- ^ PDF Accessibility. WebAIM. [2010-04-24]. （原始内容存档于2021-02-24）.
- ^ Joe Clark. Facts and Opinions About PDF Accessibility. 2005-08-22 [2010-04-24]. （原始内容存档于2013-01-24）.
- ^ Accessibility and PDF documents. Web Accessibility Center. [2010-04-24]. （原始内容存档于2010-04-27）.
- ^ PDF Accessibility Standards v1.2. [2010-04-24]. （原始内容存档于2020-02-23）.
- ^ PDF Accessibility (PDF), California State University, [2010-04-24], （原始内容 (PDF)存档于2010-05-27）
- ^ Frequently Asked Questions (FAQs) – ISO 19005-1:2005 – PDF/A-1, Date: July 10, 2006 (PDF), 2006-07-10 [2011-07-06], （原始内容 (PDF)存档于2012-01-18）
- ^ PDF/A – A Look at the Technical Side (PDF). [2011-07-06]. （原始内容 (PDF)存档于2011-07-26）.
- ^ LibreOffice Help - Export as PDF, [2012-09-22], （原始内容存档于2021-02-25）
- ^ Exporting PDF/A for long-term archiving, 2008-01-11 [2015-01-23], （原始内容存档于2021-02-24）
- ^ Adobe Reader 8 - Read a PDF with Read Out Loud. [2010-04-24]. （原始内容存档于2016-01-18）.
- ^ Biersdorfer, J.D. Tip of the Week: Adobe Reader’s ‘Read Aloud’ Feature. The New York Times. 2009-04-10 [2010-04-24]. （原始内容存档于2020-11-22）.
- ^ Accessing PDF documents with assistive technology: A screen reader user's guide (PDF), Adobe, [2010-04-24], （原始内容存档 (PDF)于2013-02-02）
- ^ Adobe Forums, Announcement: PDF Attachment Virus "Peachy", 15 August 2001.
- ^ Security bulletins and advisories. Adobe. [2010-02-21]. （原始内容存档于2013-11-15）.
- ^ Steve Gibson - SecurityNow Podcast. [2015-01-23]. （原始内容存档于2020-05-08）.
- ^ PDFCleaner - PDF Exploit Sanitizer. [2015-01-23]. （原始内容存档于2013-04-30）.
- ^ PCmag.com blogs. [2015-01-23]. （原始内容存档于2010-04-04）.
- ^ Create Adobe PDF Online - Security Settings Help. Createpdf.adobe.com. [2010-02-21]. （原始内容存档于2009-12-23）.
- ^ New features and issues addressed in the Acrobat 7.0.5 Update (Acrobat and Adobe Reader for Windows and Mac OS). [2015-01-23]. （原始内容存档于2007-08-12）.
- ^ Getting Familiar with Adobe Reader > Understanding Preferences. [2009-04-22]. （原始内容存档于2021-02-24）.
- ^ 3D supported formats. Adobe. 2009-07-14 [2010-02-21]. （原始内容存档于2010-02-12）.
- ^ Acrobat 3D Developer Center. Adobe. [2010-02-21]. （原始内容存档于2010-06-29）.
- ^ Description of 2007 Microsoft Office Suite Service Pack 2 (SP2). Microsoft. [2009-05-09]. （原始内容存档于2009-04-29）.
- ^ www.globalgraphics.com/products/jaws_rip/. [2015-01-20]. （原始内容存档于2016-03-05）.
- ^ Adobe PDF Print Engine 2. [2015-01-20]. （原始内容存档于2013-08-22）.
- ^ Pro 與 Standard 的 PDF 功能 | Adobe Acrobat DC. acrobat.adobe.com. [2021-01-21]. （原始内容存档于2020-11-23）.
- ^ Enfocus - PitStop Pro - The industry standard for PDF preflighting and editing. [2015-01-20]. （原始内容存档于2012-06-14）.
- ^ 存档副本. [2015-01-20]. （原始内容存档于2013-01-30）.
- ^ Harlequin MultiRIP. [2014-03-02]. （原始内容存档于2014-02-09）.
- ^ Press-Ready PDF Files （页面存档备份，存于互联网档案馆） "For anyone interested in having their graphic project commercially printed directly from digital files or PDFs." (last checked on 2009-02-10).
- ^ High Priority Free Software Projects — Free Software Foundation — Working together for free software. www.fsf.org. [2022-09-23]. （原始内容存档于2009-07-01）.
- ^ GNUpdf contributors. Goals and Motivations. gnupdf.org. GNUpdf. 2007-11-28 [2014-04-02]. （原始内容存档于2014-07-04）.
- ^ Lee, Matt. GNU PDF project leaves FSF High Priority Projects list; mission complete!. fsf.org. Free Software Foundation. 2011-10-06 [2014-04-02]. （原始内容存档于2014-12-28）.
- ^ Poppler. poppler.freedesktop.org. [2022-09-23]. （原始内容存档于2020-08-14）.
- ^ poppler/poppler - The poppler pdf rendering library. [2022-09-23]. （原始内容存档于2013-04-14）.
- ^ Apache PDFBox | A Java PDF Library. pdfbox.apache.org. [2022-09-23]. （原始内容存档于2023-03-06）.
- ^ Introducing PDFKit on iOS - WWDC 2017 - Videos. Apple Developer. [2021-01-21]. （原始内容存档于2020-10-31） （英语）.

## 参见
[编辑]

## 外部链接
[编辑]
- Adobe PDF官方介绍：什么是PDF？Adobe便携式文档格式 （页面存档备份，存于互联网档案馆）
- How was the PDF format created? Quora
- PDF Association - PDF Association是软件开发者创作及处理PDF文档的产业协会
- Adobe PDF 101: Summary of PDF
- Adobe: PostScript vs. PDF – 官方介绍的PS、EPS与PDF的比较
- PDF Standards....transitioning the PDF specification from a de facto standard to a de jure standard，存于互联网档案馆 – 有关可访问文档格式的PDF/E及PDF/UA规格的信息
- ISO 19005-1:2005（页面存档备份，存于互联网档案馆） 国际标准化组织发布的PDF/A-1 ISO标准
- PDF Reference and Adobe Extensions to the PDF Specification（页面存档备份，存于互联网档案馆）
- Portable Document Format: An Introduction for Programmers （页面存档备份，存于互联网档案馆） – 对比PDF、PostScript及PDF构件的介绍（升级到v1.3）
- The Camelot Paper（页面存档备份，存于互联网档案馆） – John Warnock概述的创建PDF的项目
- Everything you wanted to know about PDF but were afraid to ask（页面存档备份，存于互联网档案馆） - Leonard Rosenthol（Adobe Systems）在TUG 2007上的谈话记录
- How to produce PDF with XSL-FO （页面存档备份，存于互联网档案馆）
- 善用佳软：全面接触PDF:最好用的PDF软件汇总 （页面存档备份，存于互联网档案馆）
