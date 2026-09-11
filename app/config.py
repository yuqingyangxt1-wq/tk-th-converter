"""Configuration management - load/save config.json, provide defaults."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


APP_NAME = "TK泰国表格转化工具"
__version__ = "1.0.1"  # v1.0.1: TH 后台禁用词 / fill_sizes 展开 / 默认 Color / size_chart 必传


def get_app_dir() -> Path:
    """Return the writable directory next to the executable.

    This is where config.json (and any future user files) live. For both
    a PyInstaller --onefile exe and a `python -m app.main` source run,
    this is the directory containing the exe / project root.
    """
    if getattr(sys, "frozen", False):  # PyInstaller bundle
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_assets_dir() -> Path:
    """Return the directory containing bundled read-only assets (the template).

    Source run: <project>/assets/
    PyInstaller: also <exe-dir>/assets/ (we ship assets/ next to the exe
                 rather than relying on _MEIPASS, matching the original
                 tool's "template/ folder" layout and keeping the template
                 user-replaceable).
    """
    return get_app_dir() / "assets"


def default_config() -> dict[str, Any]:
    """The shipped defaults — mirror the original v1.2 tool."""
    return {
        "version": 2,
        "product_xlsx_last": "",
        "product_xlsx_output_dir": "",
        "product_xlsx_last_output_dir": "",
        "product_pool_dir": "",
        "product_xlsx_settings": {
            # v1.0.1: 让用户能跳过图片下载（默认勾上 = 下载；GUI 转化页有开关）
            "download_images_enabled": True,
            # Title (TH 版：v1.0.1 后台禁用词规避：去 "COD" / 去方括号【…】 /
            # 去特殊符号 ฿，用更中性的泰式写法。卖家如要 COD 字样需手动加。)
            "title_prefix_enabled": True,
            "title_prefix": "เสื้อยืด Oversize ",
            # Brand
            "brand_enabled": True,
            "brand_value": "No brand",
            # Price (THB)
            "price_enabled": True,
            "price_value": 199,
            # Quantity
            "quantity_enabled": True,
            "quantity_value": 999,
            # COD (v1.0.1: 默认改为 N — TH 后台对 "COD" 字样敏感，
            # 如果 seller 真用 COD 收发货可手动改 Y)
            "cod_enabled": True,
            "cod_value": "N",
            # Fill standard sizes S-3XL into property_value_2
            # v1.0.1: 行为由"塞整串"改为"按尺码拆成多行"，详见 tiktok_writer.build_rows_for_product
            "fill_sizes_enabled": True,
            "standard_sizes": "S,M,L,XL,2XL,3XL",
            # v1.0.1: 源表 var1 (颜色) 为空时的兜底值，避免 Primary variation value 空
            # 被 TikTok 后台拒。卖家如想留空可关闭。
            "default_color_enabled": True,
            "default_color_value": "As Picture",
            # Random suffix to differentiate copies
            "title_random_suffix_enabled": True,
            "random_suffix_length": 3,
            # Category (v1.0.1: 用户团队主要做女装，默认切到女装类目；
            # 25 个男装类目仍可手动切换)
            "category_enabled": True,
            "category_value": "Womenswear & Underwear>Women's Tops>Women's T-shirts",
            # Output copies per product (防查重 / 同款多 listing)
            "output_copies": 2,
            # When False (default), output_copies is realized as N in-file
            # duplicate rows per variant. When True, the tool emits N separate
            # xlsx files; each file contains every product and uses a unique
            # random suffix on title + seller_sku.
            "split_output_files": False,
            # Description (TH 市场：英文通用)
            "description_enabled": True,
            "description_value": (
                "High-quality product with careful packaging. "
                "Material: premium fabric, soft and comfortable, breathable for daily wear. "
                "Care: machine washable, retains shape after washing. "
                "Size: please refer to the size chart image before ordering. "
                "Shipping: orders ship within 1-2 business days; delivery typically takes 3-8 days."
            ),
            # Size chart URL (v1.0.1: TH 后台不接受 GitHub raw 外链，
            # 默认留空让卖家在 GUI 里填 TikTok Media Center 拿到的 URL/ID。
            # 如果卖家要用占位图，可以在 GUI 里粘贴任意 URL。)
            "size_chart_enabled": True,
            "size_chart_value": "",
            # Parcel
            "parcel_enabled": True,
            "parcel_weight_value": 200,   # grams
            "parcel_length_value": 10,   # cm
            "parcel_width_value": 10,
            "parcel_height_value": 5,
            # TikTok-specific (TH 不使用预售，留空；delivery 也留空让卖家填)
            "pre_order_time_value": "",
            "delivery_value": "",
        },
        # Source column mapping (override which EasyBoss/源列 maps to what)
        # If a key is empty/None, the reader falls back to auto-detection.
        "source_column_mapping": {
            "product_name": "产品名",
            "brand": "品牌",
            "category": "产品类目",
            "platform_sku": "平台SKU",
            "var1_name": "规格1名称",
            "var1_value": "规格1选项",
            "var2_name": "规格2名称",
            "var2_value": "规格2选项",
            "var3_name": "规格3名称",
            "var3_value": "规格3选项",
            "price": "税前价格",
            "stock": "库存",
            "sku_image": "SKU图片",
            "image_1": "产品图片1",
            "image_2": "产品图片2",
            "image_3": "产品图片3",
            "image_4": "产品图片4",
            "image_5": "产品图片5",
            "image_6": "产品图片6",
            "image_7": "产品图片7",
            "image_8": "产品图片8",
            "image_9": "产品图片9",
            "parcel_weight_kg": "包裹重量（KG）",
            "parcel_length": "包裹长度（CM）",
            "parcel_width": "包裹宽度（CM）",
            "parcel_height": "包裹高度（CM）",
            "description": "产品描述",
            "size_chart": "尺码图",
        },
    }


def config_path() -> Path:
    return get_app_dir() / "config.json"


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load config from disk, merging with defaults so new keys appear."""
    p = path or config_path()
    cfg = default_config()
    if p.exists():
        try:
            with p.open("r", encoding="utf-8") as f:
                on_disk = json.load(f)
            # Shallow merge at top level, deep merge for *_settings / mapping
            for k, v in on_disk.items():
                if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
        except (OSError, json.JSONDecodeError):
            # Corrupt config → fall back to defaults but don't overwrite
            pass
    return cfg


def save_config(cfg: dict[str, Any], path: Path | None = None) -> None:
    p = path or config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_settings(cfg: dict[str, Any]) -> dict[str, Any]:
    """Return the product_xlsx_settings sub-dict, applying defaults for missing keys."""
    defaults = default_config()["product_xlsx_settings"]
    s = dict(defaults)
    s.update(cfg.get("product_xlsx_settings", {}))
    return s


def update_settings(cfg: dict[str, Any], **kwargs: Any) -> None:
    cfg.setdefault("product_xlsx_settings", {})
    cfg["product_xlsx_settings"].update(kwargs)
