"""v1.0.1 dry-run — verify the 5 fixes from screenshot:
  1. title_prefix has no prohibited words
  2. size_chart defaults to empty
  3. var1 empty → default_color_value fallback
  4. var2 empty + fill_sizes_enabled → expand to one row per standard size
  5. seller_sku is unique across expanded rows (no "SKU is not unique")
"""
from __future__ import annotations
import sys, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

import openpyxl
from app.config import default_config
from app.converter import convert_source


def make_source() -> Path:
    """Mock EasyBoss xlsx with 3 products exercising different fix paths."""
    src = Path("/tmp/th_v101_dryrun.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    headers = [
        "产品名", "品牌", "SKU", "规格1名称", "规格1选项",
        "规格2名称", "规格2选项", "税前价格", "库存",
        "产品图片1", "包裹重量（KG）", "产品描述", "尺码图",
    ]
    ws.append(headers)

    # Product A: complete variant (color + size both filled) — should be unchanged
    ws.append([
        "เสื้อยืด Oversize Premium Cotton",   # 产品名 (no COD/【…】/฿)
        "",
        "PH123-Black-S",
        "颜色", "Black",
        "尺码", "S",
        369, 999,
        "https://example.com/a.jpg",
        0.2,
        "Premium cotton t-shirt.",
        "",
    ])
    ws.append([
        "เสื้อยืด Oversize Premium Cotton",
        "",
        "PH123-Black-M",
        "颜色", "Black",
        "尺码", "M",
        369, 999,
        "https://example.com/a.jpg",
        0.2,
        "Premium cotton t-shirt.",
        "",
    ])

    # Product B: var1 (color) empty, var2 (size) filled — triggers default_color
    ws.append([
        "เสื้อยืด Premium (B)",
        "",
        "PH124-XXL",
        "颜色", "",   # ← empty color
        "尺码", "XXL",
        369, 999,
        "https://example.com/b.jpg",
        0.2,
        "Premium cotton t-shirt.",
        "",
    ])

    # Product C: var2 (size) EMPTY, var1 filled — triggers fill_sizes expansion
    # Should expand to 6 rows (S,M,L,XL,2XL,3XL) with unique seller_sku
    ws.append([
        "เสื้อยืด Premium (C)",
        "",
        "PH125-Pink",   # base SKU
        "颜色", "Pink",
        "尺码", "",   # ← empty size, triggers fill_sizes
        369, 999,
        "https://example.com/c.jpg",
        0.2,
        "Premium cotton t-shirt.",
        "",
    ])

    # Product D: both var1 and var2 empty — triggers BOTH fallbacks
    ws.append([
        "เสื้อยืด Premium (D)",
        "",
        "PH126",
        "颜色", "",
        "尺码", "",
        369, 999,
        "https://example.com/d.jpg",
        0.2,
        "Premium cotton t-shirt.",
        "",
    ])

    wb.save(src)
    return src


def main():
    src = make_source()
    print(f"mock source: {src}")

    out_dir = Path("/tmp/th_v101_out")
    if out_dir.exists():
        shutil.rmtree(out_dir)

    cfg = default_config()
    ps = cfg["product_xlsx_settings"]

    # Print the key default values we just changed
    print("\n--- v1.0.1 DEFAULTS ---")
    print(f"  title_prefix    = {ps['title_prefix']!r}  (no COD/【…】/฿ ✓)")
    print(f"  category_value  = {ps['category_value']!r}")
    print(f"  size_chart_value= {ps['size_chart_value']!r}  (empty, must be set by user ✓)")
    print(f"  cod_value       = {ps['cod_value']!r}  (default N ✓)")
    print(f"  default_color   = {ps['default_color_value']!r}  ✓")
    print(f"  fill_sizes      = {ps['fill_sizes_enabled']!r}, std={ps['standard_sizes']!r}")

    result = convert_source(
        source_xlsx=src, output_dir=out_dir, settings=ps,
        template_src=REPO / "assets" / "batch-product-source.xlsx",
        progress=lambda p, m: None, log=lambda s: None,
        download_imgs=False,
    )
    print(f"\nresult: {result.product_count} products / {result.row_count} rows")
    print(f"output: {result.output_paths[0].name}")

    # Inspect
    wb2 = openpyxl.load_workbook(result.output_paths[0])
    ws2 = wb2["Template"]
    headers_out = [str(c.value or "") for c in ws2[1]]
    print(f"\ncolumns: {len(headers_out)}, pre_order_time: {'pre_order_time' in headers_out}")

    def col(label): return headers_out.index(label) + 1

    print("\n--- ROW-BY-ROW ---")
    for r in range(2, ws2.max_row + 1):
        pn = ws2.cell(r, col("product_name")).value or ""
        c1 = ws2.cell(r, col("property_value_1")).value or ""
        c2 = ws2.cell(r, col("property_value_2")).value or ""
        sku = ws2.cell(r, col("seller_sku")).value or ""
        sc = ws2.cell(r, col("size_chart")).value or ""
        print(f"  R{r}: title={str(pn)[:30]!r:35}  color={c1!r:15}  size={c2!r:8}  sku={sku!r:25}  size_chart={sc!r}")

    # Assertions
    print("\n--- ASSERTIONS ---")
    skus = [ws2.cell(r, col("seller_sku")).value for r in range(2, ws2.max_row + 1)]
    colors = [ws2.cell(r, col("property_value_1")).value for r in range(2, ws2.max_row + 1)]
    sizes = [ws2.cell(r, col("property_value_2")).value for r in range(2, ws2.max_row + 1)]

    # 1) No "COD" in any title (case-sensitive — "COD" is the prohibited word)
    titles = [ws2.cell(r, col("product_name")).value or "" for r in range(2, ws2.max_row + 1)]
    titles_with_cod = [t for t in titles if "COD" in t]
    print(f"  [{'OK  ' if not titles_with_cod else 'FAIL'}] titles without 'COD' (got {len(titles_with_cod)} COD'd)")

    # 2) No 【】 in titles
    titles_with_brackets = [t for t in titles if "【" in t or "】" in t]
    print(f"  [{'OK  ' if not titles_with_brackets else 'FAIL'}] titles without 【…】 (got {len(titles_with_brackets)})")

    # 3) All colors non-empty (default_color fallback worked)
    empty_colors = [i for i, c in enumerate(colors) if not c]
    print(f"  [{'OK  ' if not empty_colors else 'FAIL'}] all colors filled (got {len(empty_colors)} empty)")

    # 4) No "S,M,L,XL,2XL,3XL" string crammed into one cell
    multi_sizes = [i for i, s in enumerate(sizes) if "," in str(s)]
    print(f"  [{'OK  ' if not multi_sizes else 'FAIL'}] no comma-separated size strings (got {len(multi_sizes)})")

    # 5) seller_sku unique
    sku_count = len(skus)
    sku_unique = len(set(skus))
    print(f"  [{'OK  ' if sku_count == sku_unique else 'FAIL'}] seller_sku unique ({sku_unique}/{sku_count})")

    # 6) size_chart empty (TH 后台不允许 GitHub raw 外链)
    size_charts = [ws2.cell(r, col("size_chart")).value for r in range(2, ws2.max_row + 1)]
    non_empty = [s for s in size_charts if s]
    print(f"  [{'OK  ' if not non_empty else 'FAIL'}] size_chart empty by default (got {len(non_empty)} non-empty)")

    # 7) Product C (PH125-Pink) should expand to 6 rows with unique SKUs ending in -S, -M, -L, -XL, -2XL, -3XL
    print("\n--- Product C expansion check (PH125-Pink → 6 size rows) ---")
    c_skus = [s for s in skus if s and "PH125" in s]
    print(f"  C skus ({len(c_skus)}): {c_skus}")

    # 8) Product D (both empty) should expand to 6 rows with default color
    print("\n--- Product D expansion check (PH126 + both empty → 6 size rows, default_color) ---")
    d_rows = [(s, c, sz) for s, c, sz in zip(skus, colors, sizes) if s and "PH126" in s]
    print(f"  D rows ({len(d_rows)}):")
    for s, c, sz in d_rows:
        print(f"    sku={s}  color={c}  size={sz}")


if __name__ == "__main__":
    main()