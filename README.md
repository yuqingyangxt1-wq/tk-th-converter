# TK 泰国表格转化工具 v1.0

把 EasyBoss「导出#SKU」一键转成 **TikTok Shop 泰国站** 的批量上传模板 V5.0.2。

> TH 站首发版（男装为主，฿ 泰铢默认），跨平台 Python 源码 + Windows 一键打包。
> 和 PH 菲律宾版是同款骨架，但是 TH 的类目体系、品牌、币种、字段都已按泰国卖家中心调好。

---

## 这版适合谁

- 主做 **TikTok Shop Thailand** 男装的卖家
- 用 EasyBoss 做产品管理（其他 ERP 只要列名匹配也能跑）
- 不想每次手动在 Excel 里改标题、品牌、类目、尺码、价格、COD、尺码图

PH 菲律宾版是另一个工具：[**yuqingyangxt1-wq/tk-ph-converter**](https://github.com/yuqingyangxt1-wq/tk-ph-converter)。两个工具互不冲突，可以同时跑。

---

## 能干啥

| 模块 | 说明 |
| --- | --- |
| 转化 | EasyBoss 源表 → TH V5.0.2 模板，自动套标题前缀/品牌/价格/类目/尺码/包裹 |
| 入池 | 多批产品合并到一个「产品池」，方便反复改设置复用 |
| 提取 | 从产品池里读出来，再次转化（适合测试不同设置） |
| 多副本 | 每个产品可生成 N 个 listing（带随机后缀防查重），支持单文件 or 拆 N 文件 |
| 源表识别 | 自动认 EasyBoss 表头，也支持 TH 模板本身的二次加工 |
| 进度 | 阶段进度条 + 日志区，后台线程跑，UI 不卡 |

---

## 目录结构

```
tk-th-converter/
├── app/
│   ├── __init__.py
│   ├── main.py             # tkinter GUI（入口：main()）
│   ├── config.py           # config.json 读写 / 默认配置（TH 泰铢默认）
│   ├── source_reader.py    # EasyBoss / TikTok 输入解析
│   ├── tiktok_writer.py    # 写 TH V5.0.2 模板
│   ├── converter.py        # 转化主流程
│   └── product_pool.py     # 入池 / 提取
├── assets/
│   ├── batch-product-source.xlsx   # TikTok TH V5.0.2 模板
│   └── default_size_chart.png      # 默认 Unisex 尺码图
├── TK-TH-Converter.spec             # PyInstaller 配置
├── build_windows.bat                # Windows 一键打包
├── requirements.txt
├── config.json                      # 首次运行生成
└── README.md
```

---

## 跑起来（开发模式 · Mac / Windows / Linux）

```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m app.main
```

依赖只有 `openpyxl`（tkinter 随 Python 自带）。可选 `tkinterdnd2` 启用拖放。

---

## 打包成 Windows .exe

两种路径，**推荐走 GitHub Actions**（云端免费，5 分钟出包，不需要 Windows 机器）：

1. 把这个仓库 fork / push 到你自己的 GitHub
2. 改 `.github/workflows/build-windows.yml` 里的 `on: push:` 触发条件
3. push 代码后到 Actions 页面下载 `TK-TH-Converter-windows.zip`
4. 解压后是 `TK-TH-Converter.exe` + `assets/`，直接发给客户用

本地 Windows 打包：
1. 装 **Python 3.11+**（勾选 `tcl/tk and IDLE` + `Add python.exe to PATH`）
2. 把整个 `tk-th-converter/` 拷到 Windows 上
3. 双击 `build_windows.bat`

产物在 `dist/TK-TH-Converter.exe`（约 12 MB）。

---

## TH 版默认设置

打开 exe 后会在同目录生成 `config.json`，按需修改：

| 字段 | TH 默认 | 说明 |
| --- | --- | --- |
| `title_prefix` | `COD ฿199 Unisex T-shirt【S-3XL】 ` | 标题前缀，含泰铢符号 |
| `brand_value` | `No brand` | TH 卖家中心默认 |
| `category_value` | `Men's Tops/T-shirts` | TH 模板 25 个男装类目其一 |
| `price_value` | `199` | 泰铢，不带货币符号（模板只接数字） |
| `quantity_value` | `999` | 通用安全库存 |
| `cod_value` | `Y` | TH 默认支持货到付款 |
| `standard_sizes` | `S,M,L,XL,2XL,3XL` | property_value_2 标准尺码 |
| `size_chart_value` | GitHub raw PNG URL | 默认 Unisex T-shirt 尺码图，公网可访问 |
| `parcel_weight_value` | `200` g | 通用 T 恤单件重量 |
| `pre_order_time_value` | `""` | TH 不使用预售，输出 xlsx 自动删列 |

> TH 模板里 `pre_order_time` 列默认存在，但工具写入时会**物理删除整列**——卖家后台不会显示预售 3 天的字段。

---

## EasyBoss → TH 字段映射

| TH 模板列 | EasyBoss 源列 | 处理 |
| --- | --- | --- |
| `category` | `产品类目` | 默认强制覆盖为 `Men's Tops/T-shirts`，可在设置改 |
| `brand` | `品牌` | 默认 `No brand` |
| `product_name` | `产品名` | 加 `title_prefix` + 可选随机后缀 |
| `product_description` | `产品描述` | 默认英文文案覆盖 |
| `main_image` ~ `image_9` | `产品图片1..9` | 直接透传（Shopee 图需手动传 TikTok Media Center 替换 URL） |
| `property_name_1/2` | `规格1/2名称` | 中文 `颜色/尺码` → 英文 `Color/Size` 自动转 |
| `property_value_1/2` | `规格1/2选项` | 多 SKU 去重 |
| `parcel_weight` | `包裹重量（KG）` | KG × 1000 自动转 g |
| `parcel_length/width/height` | `包裹长/宽/高（CM）` | 直接透传 |
| `price` | `税前价格` | 默认 199 ฿ 覆盖 |
| `quantity` | `库存` | 默认 999 覆盖 |
| `seller_sku` | `平台SKU` | 自动剥 `-颜色-尺码` 后缀做 master，多变体拼后缀 |
| `size_chart` | `尺码图` | 默认用 PNG 公网链接 |
| `cod` | — | 默认 `Y` |
| `delivery` | — | 留空，让卖家手动选 |

TH 模板比 PH 多 9 列 `product_property/100157 ~ 100403`（Material、Pattern、Neckline、Sleeve length、Season、Style、Fit、Stretch、Washing instructions、Waist height）。**这版默认不填**——这些列每类目允许的值不一样，填错整行报红。如果你的类目固定，可以在 GUI 里改成默认填，等下个版本加自动映射。

---

## 常见问题

**Q: 卖家中心上传报红？**
A: 大概率是 `size_chart` 列空——用默认 PNG URL 或者传你自己的图。第二个常见原因是 `category` 写错——TH 模板的 HiddenStyle 会按 category 校验列是否 Mandatory/Forbid。

**Q: 价格是泰铢还是美元？**
A: 泰铢。模板只接数字，币种由卖家账号决定。在标题前缀里加了 `฿199` 是为了搜索结果页买家一看就知道价格。

**Q: 商品图显示不出来？**
A: Shopee cf.shopee.ph 图链在 TikTok 后台过期了。工具会自动下载到 `images/`，把 `image_manifest.txt` 里的图手动传 TikTok Media Center，再用新 URL 替换回 xlsx 即可。

**Q: 改了设置但没生效？**
A: GUI 是自动保存的（trace_add 实时落盘）。如果怀疑有问题，删掉 exe 同目录的 `config.json` 重启，会用出厂默认值。

---

## 跟 PH 版对比

| 项 | PH 菲律宾版 | TH 泰国版（这版） |
| --- | --- | --- |
| 类目 | 中文路径 | 英文路径（`Men's Tops/T-shirts` 等） |
| 货币 | ₱ 356 | ฿ 199 |
| 品牌 | `No brand` | `No brand`（同） |
| pre_order | 已删列 | 默认不写、模板列也删 |
| product_property 9 列 | 同 | 同（TH 模板自带，PH 也有但 ID 不同） |
| HiddenStyle / HiddenAttr | PH 模板自带 | TH 模板自带，按类目决定 Mandatory |
| 仓库 | tk-ph-converter | tk-th-converter（本仓库） |

两个工具底层代码 90% 共享，差异都在 `config.py` 默认值 + 模板资源。

---

## License

MIT。同仓库随便用。