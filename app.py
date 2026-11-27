import io
import re
import unicodedata
from datetime import date
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


# ============================================================
# PO CALCULATOR - BRAND & MARKETPLACE
# Jubelio + Desty (BigSeller can be added later)
# ============================================================

st.set_page_config(
    page_title="PO Calculator - Multi Brand",
    page_icon="📦",
    layout="wide",
)

st.title("📦 PO Calculator — Multi Brand & Marketplace")
st.caption(
    "Upload data Jubelio/Desty, pilih brand, periksa pemetaan warehouse, "
    "lalu ekspor hasil PO sesuai format Daily Order."
)

# ------------------------------------------------------------
# MASTER BRAND CONFIGURATION
# Warehouse headers follow the Daily Order screenshots supplied
# by the user. Adjust this section if a Daily Order template changes.
# ------------------------------------------------------------

BRAND_CONFIG: Dict[str, dict] = {
    "CAVE": {
        "aliases": ["cave", "cao-70106"],
        "sources": ["Jubelio"],
        "warehouses": [
            "CAVE", "Makassar", "Medan", "Oxar Central Warehouse",
            "Jakarta Timur", "Surabaya", "Yogyakarta", "PADANG",
            "BANJARMASIN", "BALI",
        ],
        "oxar_columns": [
            "Makassar", "Medan", "Oxar Central Warehouse", "Jakarta Timur",
            "Surabaya", "Yogyakarta", "PADANG", "BANJARMASIN", "BALI",
        ],
    },
    "Yummys": {
        "aliases": ["yummys", "yummy"],
        "sources": ["Jubelio"],
        "warehouses": [
            "AARON-DEPOK", "AARON-GRESIK", "AARON-RIAU",
            "AARON-SURABAYA", "AARON-YOGYAKARTA",
            "Oxar-Jakarta Timur", "Oxar Central Warehouse",
            "OXAR-Makassar", "OXAR-Medan", "OXAR-Padang",
            "OXAR-Banjarmasin", "OXAR-Palembang", "OXAR-Bali",
        ],
        "oxar_columns": [
            "Oxar-Jakarta Timur", "Oxar Central Warehouse",
            "OXAR-Makassar", "OXAR-Medan", "OXAR-Padang",
            "OXAR-Banjarmasin", "OXAR-Palembang", "OXAR-Bali",
        ],
    },
    "BHSTx": {
        "aliases": ["bhstx", "bhst"],
        "sources": ["Jubelio"],
        "warehouses": ["OXAR BANJARMASIN", "OXAR BEKASI", "OXAR MAKASSAR"],
        "oxar_columns": ["OXAR BANJARMASIN", "OXAR BEKASI", "OXAR MAKASSAR"],
    },
    "Essens": {
        "aliases": ["essens"],
        "sources": ["Jubelio"],
        "warehouses": [
            "Makassar", "Medan", "Oxar Central Warehouse", "Surabaya",
            "Yogyakarta", "Padang", "Palembang", "Pekanbaru", "Banjarmasin",
        ],
        "oxar_columns": [
            "Makassar", "Medan", "Oxar Central Warehouse", "Surabaya",
            "Yogyakarta", "Padang", "Palembang", "Pekanbaru", "Banjarmasin",
        ],
    },
    "BMYT": {
        "aliases": ["bmyt"],
        "sources": ["Jubelio"],
        "warehouses": ["Gudang BMYT Bali", "Gudang OXAR"],
        "oxar_columns": ["Gudang OXAR"],
    },
    "Hexxa": {
        "aliases": ["hexxa"],
        "sources": ["Jubelio"],
        # Daily Order Hexxa: only Jakarta Timur and Surabaya are warehouse columns.
        "warehouses": ["Jakarta Timur", "Surabaya"],
        "oxar_columns": [],
    },
    "NDR": {
        "aliases": ["ndr"],
        "sources": ["Jubelio"],
        "warehouses": ["Pusat", "Oxar Bekasi"],
        "oxar_columns": ["Oxar Bekasi"],
    },
    "Jamu Jago": {
        "aliases": ["jamu jago", "jamujago"],
        "sources": ["Desty"],
        "warehouses": [
            "SEMARANG (WH Jamu Jago)",
            "Gudang Oxar Banjarmasin",
            "Gudang Oxar BEKASI",
            "Gudang Oxar JKT Timur",
            "Gudang Oxar Makassar",
            "Gudang Oxar Medan",
            "Gudang Oxar Padang",
            "Gudang Oxar Surabaya",
            "Gudang Oxar Yogyakarta",
        ],
        "oxar_columns": [
            "Gudang Oxar Banjarmasin", "Gudang Oxar BEKASI",
            "Gudang Oxar JKT Timur", "Gudang Oxar Makassar",
            "Gudang Oxar Medan", "Gudang Oxar Padang",
            "Gudang Oxar Surabaya", "Gudang Oxar Yogyakarta",
        ],
    },
    "Teratu": {
        "aliases": ["teratu"],
        "sources": ["Jubelio"],
        "warehouses": ["Oxar Banjarmasin"],
        "oxar_columns": ["Oxar Banjarmasin"],
    },
    "Aquila": {
        "aliases": ["aquila", "aquilla"],
        "sources": ["Jubelio"],
        "warehouses": ["Oxar Banjarmasin"],
        "oxar_columns": ["Oxar Banjarmasin"],
    },
    "Bumi Tauhid": {
        "aliases": ["bumi tauhid", "bumitauhid"],
        "sources": ["BigSeller"],
        "source_note": "Objective dan marketplace (BigSeller)",
        "warehouses": [
            "Bumi Tauhid", "Gudang Bekasi", "Gudang Makassar",
            "Gudang Medan", "Gudang Surabaya",
        ],
        "oxar_columns": [
            "Gudang Bekasi", "Gudang Makassar", "Gudang Medan", "Gudang Surabaya"
        ],
    },
    "Safwan": {
        "aliases": ["safwan"],
        "sources": ["BigSeller"],
        "source_note": "Shopee melalui BigSeller",
        "warehouses": ["Gudang Safwan", "Oxar Surabaya", "Oxar Makassar"],
        "oxar_columns": ["Oxar Surabaya", "Oxar Makassar"],
    },
    "Attaqwa": {
        "aliases": ["attaqwa"],
        "sources": ["Jubelio"],
        "warehouses": ["Attaqwa", "Gudang Medan", "Gudang Padang"],
        "oxar_columns": ["Gudang Medan", "Gudang Padang"],
    },
    "Aqshor": {
        "aliases": ["aqshor"],
        "sources": ["Jubelio"],
        # Master union is used for source-warehouse mapping and the combined view.
        "warehouses": [
            "Aqshor", "Gudang Bekasi", "Gudang Makassar",
            "Gudang Medan", "Gudang Surabaya",
        ],
        "oxar_columns": [
            "Gudang Bekasi", "Gudang Makassar", "Gudang Medan", "Gudang Surabaya"
        ],
        # Daily Order Aqshor has two distinct marketplace blocks with different headers.
        "marketplace_layouts": {
            "Shopee": {
                "label": "Shopee",
                "warehouses": [
                    "Aqshor", "Gudang Bekasi", "Gudang Makassar",
                    "Gudang Medan", "Gudang Surabaya",
                ],
                "oxar_columns": [
                    "Gudang Bekasi", "Gudang Makassar", "Gudang Medan", "Gudang Surabaya"
                ],
                "include_oxar_totals": True,
            },
            "TikTok": {
                "label": "TikTok",
                "warehouses": [
                    "Gudang Bekasi", "Gudang Makassar", "Gudang Medan", "Gudang Surabaya"
                ],
                "oxar_columns": [],
                "include_oxar_totals": False,
            },
        },
    },
}

# Sumber data per brand mengikuti daftar Source DR yang diberikan.
# BigSeller ditampilkan sebagai sumber yang akan datang, tetapi parser-nya
# belum diaktifkan pada versi ini.
BRAND_SOURCE_NOTES = {
    "CAVE": "Jubelio",
    "Yummys": "Jubelio",
    "Bumi Tauhid": "BigSeller — Objective dan marketplace (belum aktif)",
    "Safwan": "BigSeller — Shopee (belum aktif)",
    "NDR": "Jubelio",
    "Essens": "Jubelio",
    "BMYT": "Jubelio",
    "Jamu Jago": "Desty",
    "Aquila": "Jubelio",
    "Attaqwa": "Belum dikonfirmasi",
    "Aqshor": "Belum dikonfirmasi",
}

# Default status exclusions. The app excludes these statuses and keeps
# other non-empty statuses, so new valid status labels can still be counted.
DEFAULT_EXCLUDED = {
    # Paid, Completed, Processing, dan Shipped tetap dihitung.
    # Hanya pembatalan, retur, dan pembayaran yang belum dilakukan dikeluarkan.
    "Jubelio": [
        "CANCEL", "CANCELLATION", "RETURN", "RETUR", "UNPAID",
        "BELUM BAYAR", "BELUM DIBAYAR", "BELUM BAYAR",
    ],
    "Desty": [
        "CANCEL", "CANCELLATION", "RETURN", "RETUR", "UNPAID",
        "BELUM BAYAR", "BELUM DIBAYAR",
    ],
}

UNMAPPED_LABEL = "⛔ Tidak dihitung — tidak ada di Daily Sales All Client"

# Header candidates based on the actual sample files.
JUBELIO_HEADERS = {
    "date": ["Tanggal", "Tanggal Pesanan"],
    "order": ["No Pesanan", "Nomor Pesanan", "Order ID"],
    "brand": ["Nama Toko", "Store", "Nama Brand"],
    "channel": ["Channel", "Marketplace", "Platform"],
    "warehouse": ["Lokasi", "Warehouse", "Gudang"],
    "status": ["Status", "Status Pesanan"],
}
DESTY_HEADERS = {
    "date": ["Tanggal Pesanan Dibuat", "Tanggal Pesanan", "Tanggal"],
    "order": ["Nomor Pesanan\n(di Marketplace)", "Nomor Pesanan (di Marketplace)",
              "Nomor Pesanan\n(di Desty)", "Nomor Pesanan (di Desty)"],
    "brand": ["Channel - Nama Toko", "Nama Toko", "Brand"],
    "channel": ["Channel - Nama Toko", "Channel", "Marketplace"],
    "warehouse": ["Nama Gudang\nMaster", "Nama Gudang Master", "Warehouse"],
    "status": ["Status Pesanan", "Status"],
}


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def norm(value) -> str:
    """Normalize text for matching without changing the displayed label."""
    s = clean_text(value).lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def norm_wh(value) -> str:
    """Warehouse matching key: ignore common prefixes such as Gudang/Oxar."""
    s = clean_text(value).lower()
    s = re.sub(r"\b(gudang|warehouse|oxar)\b", " ", s)
    s = re.sub(r"\bwh\b", " ", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", s)


def find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    exact = {clean_text(c).lower(): c for c in df.columns}
    for cand in candidates:
        if clean_text(cand).lower() in exact:
            return exact[clean_text(cand).lower()]
    normalized = {norm(c): c for c in df.columns}
    for cand in candidates:
        if norm(cand) in normalized:
            return normalized[norm(cand)]
    return None


def read_excel_upload(uploaded_file, preferred_sheet: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
    data = uploaded_file.getvalue()
    book = pd.ExcelFile(io.BytesIO(data))
    if preferred_sheet and preferred_sheet in book.sheet_names:
        sheet = preferred_sheet
    elif "Data1" in book.sheet_names:
        sheet = "Data1"
    elif "Daftar Pesanan" in book.sheet_names:
        sheet = "Daftar Pesanan"
    else:
        sheet = book.sheet_names[0]
    df = pd.read_excel(io.BytesIO(data), sheet_name=sheet)
    df.columns = [clean_text(c) for c in df.columns]
    return df, sheet


def brand_match(series: pd.Series, aliases: List[str]) -> pd.Series:
    vals = series.fillna("").astype(str).str.lower()
    mask = pd.Series(False, index=series.index)
    for alias in aliases:
        mask = mask | vals.str.contains(re.escape(alias.lower()), na=False)
    return mask


def normalize_marketplace(value: str, source: str) -> str:
    label = clean_text(value)
    if source == "Jubelio":
        if "|" in label:
            label = label.split("|")[-1].strip()
        upper = label.upper()
        if "SHOPEE" in upper:
            return "Shopee"
        if "TIKTOK" in upper:
            return "TikTok"
        if "TOKOPEDIA" in upper:
            return "Tokopedia"
        if "LAZADA" in upper:
            return "Lazada"
        if "BLIBLI" in upper:
            return "Blibli"
        return label or "Jubelio"
    if source == "Desty":
        label = label.split("-", 1)[0].strip()
        return label.title() if label else "Desty"
    return label or source


def prepare_source(
    df: pd.DataFrame,
    source: str,
    brand: str,
    aliases: List[str],
) -> Tuple[pd.DataFrame, dict]:
    headers = JUBELIO_HEADERS if source == "Jubelio" else DESTY_HEADERS
    cols = {key: find_col(df, candidates) for key, candidates in headers.items()}
    missing = [k for k in ["date", "order", "brand", "warehouse", "status"] if not cols[k]]
    if missing:
        raise ValueError(
            f"Kolom wajib tidak ditemukan pada {source}: {', '.join(missing)}. "
            f"Kolom yang terbaca: {', '.join(map(str, df.columns))}"
        )

    work = df.copy()
    # Keep the source file's original order number. Desty prefers marketplace
    # order number; if blank, use Desty order number.
    work["_date"] = pd.to_datetime(work[cols["date"]], errors="coerce", dayfirst=True)
    work["_order"] = work[cols["order"]].map(clean_text)
    if source == "Desty":
        desty_id_col = find_col(df, ["Nomor Pesanan\n(di Desty)", "Nomor Pesanan (di Desty)"])
        if desty_id_col:
            fallback = work[desty_id_col].map(clean_text)
            work["_order"] = work["_order"].where(work["_order"] != "", fallback)
    work["_brand_raw"] = work[cols["brand"]].map(clean_text)
    work["_warehouse_raw"] = work[cols["warehouse"]].map(clean_text)
    work["_status_raw"] = work[cols["status"]].map(clean_text)
    if cols["channel"]:
        work["_channel_raw"] = work[cols["channel"]].map(clean_text)
    else:
        work["_channel_raw"] = work["_brand_raw"]

    # Filter selected brand using both store name and warehouse/location.
    # Some Jubelio rows (e.g. INTERNAL/Toko Default and Blibli CAO-70106)
    # do not carry the brand name in Nama Toko, but the brand is identifiable
    # from its brand-specific warehouse or an explicit store alias.
    brand_identity = (
        work["_brand_raw"].fillna("").astype(str)
        + " | "
        + work["_warehouse_raw"].fillna("").astype(str)
    )
    work = work[brand_match(brand_identity, aliases)].copy()
    # Warehouse kosong tetap dipertahankan agar masuk laporan pengecualian,
    # bukan hilang diam-diam. Tanggal, nomor pesanan, dan status wajib tersedia.
    work = work[
        work["_date"].notna()
        & (work["_order"] != "")
        & (work["_status_raw"] != "")
    ].copy()

    excluded = DEFAULT_EXCLUDED[source]
    status_upper = work["_status_raw"].str.upper().str.strip()
    exclude_mask = pd.Series(False, index=work.index)
    for token in excluded:
        exclude_mask = exclude_mask | status_upper.str.contains(re.escape(token), na=False)
    excluded_rows = int(exclude_mask.sum())
    work = work.loc[~exclude_mask].copy()

    # Normalize marketplace label from channel field.
    work["_marketplace"] = work["_channel_raw"].map(
        lambda value: normalize_marketplace(value, source)
    )

    info = {
        "columns": cols,
        "excluded_rows": excluded_rows,
        "rows_after_brand": len(work),
        "unique_orders_before_mapping": work["_order"].nunique(),
    }
    return work, info


def auto_map_warehouse(raw_value: str, master: List[str]) -> Optional[str]:
    raw_key = norm_wh(raw_value)
    if not raw_key:
        return None
    # Exact normalized match after ignoring generic prefixes.
    hits = [m for m in master if norm_wh(m) == raw_key]
    if len(hits) == 1:
        return hits[0]
    # Safe alias rules for common location naming differences.
    aliases = {
        "jakartatimur": ["jakartatimur", "jktim"],
        "bekasi": ["bekasi"],
        "banjarmasin": ["banjarmasin"],
        "yogyakarta": ["yogyakarta", "jogja"],
        "bali": ["bali"],
        "makassar": ["makassar"],
        "medan": ["medan"],
        "surabaya": ["surabaya"],
        "padang": ["padang"],
        "palembang": ["palembang"],
        "pekanbaru": ["pekanbaru"],
        "semarang": ["semarang"],
    }
    for canonical_fragment, variants in aliases.items():
        if any(v in raw_key for v in variants):
            candidates = [m for m in master if canonical_fragment in norm_wh(m)]
            if len(candidates) == 1:
                return candidates[0]
    # Do not guess when ambiguous or unknown.
    return None


def build_mapping_table(work: pd.DataFrame, master: List[str]) -> pd.DataFrame:
    # Isi kosong juga dimasukkan agar bisa dilaporkan sebagai warehouse tidak dikenal.
    raw_values = sorted(work["_warehouse_raw"].fillna("").astype(str).unique())
    rows = []
    for raw in raw_values:
        target = auto_map_warehouse(raw, master)
        rows.append({
            "Warehouse pada file": raw if raw else "(Kosong / tidak ada nama warehouse)",
            "Masuk ke kolom Daily Order": target or UNMAPPED_LABEL,
        })
    return pd.DataFrame(rows)


def apply_mapping(work: pd.DataFrame, mapping_df: pd.DataFrame) -> pd.DataFrame:
    mapping = dict(zip(mapping_df["Warehouse pada file"], mapping_df["Masuk ke kolom Daily Order"]))
    result = work.copy()
    raw_key = result["_warehouse_raw"].replace("", "(Kosong / tidak ada nama warehouse)")
    result["_warehouse_target"] = raw_key.map(mapping)
    # Hanya warehouse yang benar-benar ada pada master Daily Sales All Client
    # yang boleh masuk ke rekap. Sisanya masuk sheet pengecualian.
    result = result[result["_warehouse_target"].isin(
        [v for v in mapping_df["Masuk ke kolom Daily Order"].unique()
         if v != UNMAPPED_LABEL]
    )].copy()
    return result


def get_unmapped_rows(work: pd.DataFrame, mapping_df: pd.DataFrame) -> pd.DataFrame:
    mapping = dict(zip(mapping_df["Warehouse pada file"], mapping_df["Masuk ke kolom Daily Order"]))
    result = work.copy()
    raw_key = result["_warehouse_raw"].replace("", "(Kosong / tidak ada nama warehouse)")
    result["_warehouse_target"] = raw_key.map(mapping)
    result = result[result["_warehouse_target"].eq(UNMAPPED_LABEL)].copy()
    return result


def deduplicate_orders(work: pd.DataFrame, across_marketplaces: bool = False) -> pd.DataFrame:
    work = work.copy()
    if across_marketplaces:
        work["_po_key"] = work["_order"].astype(str)
    else:
        work["_po_key"] = (
            work["_marketplace"].astype(str) + "::" + work["_order"].astype(str)
        )
    # Same order repeated for multiple product rows counts once.
    # Default key is unique per marketplace; optional global dedup is available.
    work = work.sort_values("_date")
    return work.drop_duplicates(subset=["_po_key"], keep="first").copy()


def make_daily_table(
    work: pd.DataFrame,
    warehouses: List[str],
    categories: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    if work.empty:
        return pd.DataFrame(columns=["Tanggal", "Category"] + warehouses + ["_total_po_calc"])
    key_col = "_po_key" if "_po_key" in work.columns else "_order"
    grouped = (
        work.groupby([work["_date"].dt.normalize(), "_warehouse_target"])[key_col]
        .nunique()
        .unstack(fill_value=0)
    )
    grouped = grouped.reindex(columns=warehouses, fill_value=0)
    grouped.index.name = "Tanggal"
    result = grouped.reset_index()
    result["Tanggal"] = pd.to_datetime(result["Tanggal"])
    result = result.sort_values("Tanggal")
    result.insert(1, "Category", result["Tanggal"].map(
        lambda d: (categories or {}).get(d.strftime("%Y-%m-%d"), "Daily")
    ))
    # Denominator internal untuk menghitung kontribusi Oxar; tidak ditampilkan
    # sebagai kolom Total PO pada tabel maupun file hasil.
    result["_total_po_calc"] = result[warehouses].sum(axis=1)
    return result


def add_template_totals(frame: pd.DataFrame, brand_cfg: dict) -> pd.DataFrame:
    result = frame.copy()
    oxar_cols = [c for c in brand_cfg.get("oxar_columns", []) if c in result.columns]
    if oxar_cols:
        result["Total Oxar Warehouse"] = result[oxar_cols].sum(axis=1)
        result["Contribute"] = result.apply(
            lambda row: row["Total Oxar Warehouse"] / row["_total_po_calc"]
            if row.get("_total_po_calc", 0) else 0,
            axis=1,
        )
    # Hilangkan kolom bantu agar Total PO tidak muncul di output.
    return result.drop(columns=["_total_po_calc"], errors="ignore")


def make_marketplace_tables(
    work: pd.DataFrame,
    brand_cfg: dict,
    categories: Optional[Dict[str, str]] = None,
) -> Dict[str, pd.DataFrame]:
    """Build marketplace sheets; some brands have different column layouts per channel."""
    outputs = {}
    layouts = brand_cfg.get("marketplace_layouts", {})

    if layouts:
        for marketplace, layout in layouts.items():
            part = work[work["_marketplace"].map(norm) == norm(marketplace)].copy()
            frame = make_daily_table(part, layout["warehouses"], categories)
            if layout.get("include_oxar_totals", False):
                frame = add_template_totals(
                    frame,
                    {"oxar_columns": layout.get("oxar_columns", [])},
                )
            else:
                frame = frame.drop(columns=["_total_po_calc"], errors="ignore")
            safe_label = re.sub(r"[^A-Za-z0-9_-]+", "_", layout.get("label", marketplace))[:25]
            outputs[safe_label] = frame
        return outputs

    for marketplace, part in work.groupby("_marketplace", dropna=False):
        label = clean_text(marketplace) or "Marketplace"
        safe_label = re.sub(r"[^A-Za-z0-9_-]+", "_", label)[:25]
        outputs[safe_label] = make_daily_table(part, brand_cfg["warehouses"], categories)
    return outputs


def excel_bytes(sheets: Dict[str, pd.DataFrame]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl", datetime_format="dd-mmm-yyyy") as writer:
        for sheet_name, frame in sheets.items():
            name = re.sub(r"[\[\]:*?/\\]", "_", sheet_name)[:31] or "Sheet"
            frame.to_excel(writer, sheet_name=name, index=False)
            ws = writer.sheets[name]
            ws.freeze_panes = "C2"
            ws.auto_filter.ref = ws.dimensions
            for col_cells in ws.columns:
                max_len = max((len(str(c.value)) if c.value is not None else 0) for c in col_cells)
                ws.column_dimensions[col_cells[0].column_letter].width = min(max(max_len + 2, 12), 34)
            # Format date column
            if frame.shape[1] and "Tanggal" in frame.columns:
                col_idx = list(frame.columns).index("Tanggal") + 1
                for row in range(2, ws.max_row + 1):
                    ws.cell(row, col_idx).number_format = "dd-mmm-yyyy"
    return output.getvalue()


# ------------------------------------------------------------
# USER INTERFACE
# ------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Pengaturan")
    selected_brand = st.selectbox("Pilih brand", list(BRAND_CONFIG.keys()))
    brand_cfg = BRAND_CONFIG[selected_brand]
    st.caption("Warehouse master mengikuti konfigurasi Daily Order brand ini.")
    st.write("**Kolom warehouse:**")
    for wh in brand_cfg["warehouses"]:
        st.write(f"• {wh}")
    across_marketplaces = st.checkbox(
        "Gabungkan deduplikasi nomor pesanan antar-marketplace",
        value=False,
        help="Jika tidak dicentang, nomor yang sama di marketplace berbeda dihitung masing-masing."
    )

st.subheader("1. Upload data transaksi")

# Tampilkan hanya tempat upload yang sesuai dengan Source DR brand terpilih.
# Jubelio dan Desty aktif; BigSeller ditampilkan sebagai placeholder nonaktif.
source_files = {}
active_sources = [src for src in brand_cfg.get("sources", []) if src in ["Jubelio", "Desty"]]

if active_sources:
    cols = st.columns(len(active_sources))
    for col, source in zip(cols, active_sources):
        with col:
            source_files[source] = st.file_uploader(
                f"Upload Excel {source} (.xlsx)",
                type=["xlsx"],
                key=f"upload_{selected_brand}_{source}",
                help=f"Brand {selected_brand} menggunakan sumber {source} sesuai konfigurasi Source DR.",
            )
elif "BigSeller" in brand_cfg.get("sources", []):
    st.info(
        f"Sumber data {selected_brand}: {BRAND_SOURCE_NOTES.get(selected_brand, 'BigSeller')}. "
        "Tempat upload BigSeller akan diaktifkan setelah format ekspor dan aturan kolom BigSeller selesai dibuat. "
        "Untuk saat ini file BigSeller belum dapat dihitung agar hasil PO tidak keliru."
    )
    st.file_uploader(
        "Upload Excel BigSeller (segera hadir)",
        type=["xlsx", "csv"],
        disabled=True,
        key=f"upload_{selected_brand}_BigSeller_disabled",
    )
else:
    st.warning(
        f"Sumber data untuk {selected_brand} belum tercantum/terkonfirmasi pada daftar Source DR. "
        "Silakan konfirmasi sumbernya sebelum brand ini diaktifkan."
    )

st.caption(
    f"Brand: {selected_brand}  |  Sumber data: "
    f"{BRAND_SOURCE_NOTES.get(selected_brand, ', '.join(brand_cfg.get('sources', [])) or 'Belum dikonfirmasi')}"
)

source_data = []
source_errors = []
source_infos = []

if source_files.get("Jubelio"):
    try:
        raw, sheet = read_excel_upload(source_files["Jubelio"], "Data1")
        prepared, info = prepare_source(raw, "Jubelio", selected_brand, brand_cfg["aliases"])
        prepared["_source"] = "Jubelio"
        source_data.append(prepared)
        info["source"] = "Jubelio"
        info["sheet"] = sheet
        source_infos.append(info)
    except Exception as exc:
        source_errors.append(f"Jubelio: {exc}")

if source_files.get("Desty"):
    try:
        raw, sheet = read_excel_upload(source_files["Desty"], "Daftar Pesanan")
        prepared, info = prepare_source(raw, "Desty", selected_brand, brand_cfg["aliases"])
        prepared["_source"] = "Desty"
        source_data.append(prepared)
        info["source"] = "Desty"
        info["sheet"] = sheet
        source_infos.append(info)
    except Exception as exc:
        source_errors.append(f"Desty: {exc}")

for err in source_errors:
    st.error(err)

if source_data:
    all_raw = pd.concat(source_data, ignore_index=True)
    st.subheader("2. Pemeriksaan data yang terbaca")
    summary = pd.DataFrame(source_infos)
    display_cols = ["source", "sheet", "rows_after_brand", "excluded_rows", "unique_orders_before_mapping"]
    st.dataframe(summary[display_cols], use_container_width=True, hide_index=True)

    st.write("**Contoh data setelah filter brand dan status:**")
    show_cols = ["_date", "_order", "_brand_raw", "_marketplace", "_warehouse_raw", "_status_raw", "_source"]
    st.dataframe(
        all_raw[show_cols].rename(columns={
            "_date": "Tanggal", "_order": "Nomor Pesanan",
            "_brand_raw": "Nama Toko", "_marketplace": "Marketplace",
            "_warehouse_raw": "Warehouse Asli", "_status_raw": "Status",
            "_source": "Sumber File",
        }).head(30),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("3. Pemetaan warehouse ke Daily Order")
    mapping_df = build_mapping_table(all_raw, brand_cfg["warehouses"])
    edited_mapping = st.data_editor(
        mapping_df,
        use_container_width=True,
        hide_index=True,
        disabled=["Warehouse pada file"],
        column_config={
            "Masuk ke kolom Daily Order": st.column_config.SelectboxColumn(
                "Masuk ke kolom Daily Order",
                options=[UNMAPPED_LABEL] + brand_cfg["warehouses"],
                required=True,
            )
        },
        key=f"mapping_{selected_brand}",
    )

    unmapped = edited_mapping[
        edited_mapping["Masuk ke kolom Daily Order"].eq(UNMAPPED_LABEL)
    ]

    mapped = apply_mapping(all_raw, edited_mapping)
    unmapped_rows = get_unmapped_rows(all_raw, edited_mapping)
    if not mapped.empty:
        mapped = deduplicate_orders(mapped, across_marketplaces=across_marketplaces)
    if not unmapped_rows.empty:
        unmapped_rows = deduplicate_orders(
            unmapped_rows, across_marketplaces=across_marketplaces
        )

    st.subheader("Ringkasan warehouse tidak terpetakan")
    if not unmapped_rows.empty:
        st.warning(
            f"Ada {unmapped_rows['_po_key'].nunique()} PO unik yang tidak dihitung "
            "karena nama warehouse tidak tersedia pada sheet Daily Sales All Client. "
            "Data ini hanya dicatat sebagai pengecualian."
        )
        unmapped_summary = (
            unmapped_rows.groupby("_warehouse_raw", dropna=False)
            .agg( jumlah_PO=("_po_key", "nunique"))
            .reset_index()
            .rename(columns={"_warehouse_raw": "Warehouse pada file", "jumlah_PO": "Jumlah PO unik"})
        )
        st.dataframe(unmapped_summary, use_container_width=True, hide_index=True)
    else:
        st.success("Tidak ada PO dengan warehouse di luar master Daily Sales All Client.")

    st.subheader("4. Hasil perhitungan PO")
    if mapped.empty:
        st.warning(
            "Belum ada data yang bisa dihitung. Periksa apakah nama brand cocok "
            "dengan kolom Nama Toko/Channel - Nama Toko dan warehouse sudah dipetakan."
        )
    else:
        # Category can be adjusted for each transaction date before export.
        date_list = sorted(mapped["_date"].dt.normalize().dropna().unique())
        cat_df = pd.DataFrame({
            "Tanggal": [pd.Timestamp(d) for d in date_list],
            "Category": ["Daily"] * len(date_list),
        })
        edited_cat = st.data_editor(
            cat_df,
            use_container_width=True,
            hide_index=True,
            disabled=["Tanggal"],
            column_config={
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    options=["Daily", "Double Date", "Payday"],
                    required=True,
                )
            },
            key=f"category_{selected_brand}",
        )
        category_map = {
            pd.Timestamp(row["Tanggal"]).strftime("%Y-%m-%d"): row["Category"]
            for _, row in edited_cat.iterrows()
        }

        warehouses = brand_cfg["warehouses"]
        daily = make_daily_table(mapped, warehouses, category_map)

        # Add template totals to consolidated and per-marketplace outputs.
        daily = add_template_totals(daily, brand_cfg)

        st.dataframe(daily, use_container_width=True, hide_index=True)

        st.subheader("5. Rincian sumber marketplace")
        marketplace_tables = make_marketplace_tables(mapped, brand_cfg, category_map)
        if not brand_cfg.get("marketplace_layouts"):
            marketplace_tables = {
                name: add_template_totals(frame, brand_cfg)
                for name, frame in marketplace_tables.items()
            }
        if marketplace_tables:
            tabs = st.tabs(list(marketplace_tables.keys()))
            for tab, (market_name, frame) in zip(tabs, marketplace_tables.items()):
                with tab:
                    st.dataframe(frame, use_container_width=True, hide_index=True)

        # Build one Excel file: consolidated + source marketplace sheets + audit.
        sheets = {f"{selected_brand} - Daily Order": daily}
        for market_name, frame in marketplace_tables.items():
            sheets[f"{selected_brand} - {market_name}"] = frame

        audit = mapped[[
            "_date", "_order", "_po_key", "_marketplace", "_source",
            "_warehouse_raw", "_warehouse_target", "_status_raw"
        ]].copy()
        audit.columns = [
            "Tanggal", "Nomor Pesanan", "Kunci PO", "Marketplace", "Sumber File",
            "Warehouse Asli", "Warehouse Daily Order", "Status"
        ]
        sheets["Audit Pesanan Unik"] = audit.sort_values(["Tanggal", "Marketplace"])

        if not unmapped_rows.empty:
            unmapped_audit = unmapped_rows[[
                "_date", "_order", "_po_key", "_marketplace", "_source",
                "_warehouse_raw", "_status_raw"
            ]].copy()
            unmapped_audit.columns = [
                "Tanggal", "Nomor Pesanan", "Kunci PO", "Marketplace", "Sumber File",
                "Warehouse pada file", "Status"
            ]
            unmapped_audit["Keterangan"] = (
                "Tidak ada nama warehouse pada sheet Daily Sales All Client; tidak dihitung"
            )
            sheets["Tidak Terpetakan"] = unmapped_audit.sort_values(
                ["Tanggal", "Marketplace"]
            )

        output = excel_bytes(sheets)
        st.download_button(
            label="⬇️ Download Excel Hasil PO",
            data=output,
            file_name=f"PO_{re.sub(r'[^A-Za-z0-9]+', '_', selected_brand)}_{date.today():%Y%m%d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )
        st.caption(
            "File Excel berisi rekap Daily Order, sheet per marketplace, Audit Pesanan Unik, "
            "serta sheet Tidak Terpetakan untuk PO yang warehouse-nya tidak ada di Daily Sales All Client. "
            "Total PO tidak ditampilkan sebagai kolom pada rekap."
        )
else:
    if "BigSeller" in brand_cfg.get("sources", []):
        st.warning(
            f"{selected_brand} menggunakan {BRAND_SOURCE_NOTES.get(selected_brand, 'BigSeller')}. "
            "Parser BigSeller belum tersedia, sehingga belum ada angka PO yang dihitung."
        )
    elif not brand_cfg["sources"]:
        st.warning(
            f"Sumber data {selected_brand} belum dikonfirmasi. Brand ini belum dapat diproses."
        )
    else:
        st.info(
            "Pilih brand di sidebar, lalu upload file sesuai sumber brand tersebut. "
            "Contoh: CAVE/Yummys menggunakan Jubelio; Jamu Jago menggunakan Desty."
        )

with st.expander("ℹ️ Catatan aturan perhitungan"):
    st.markdown(
        """
        - Satu nomor pesanan dihitung satu PO meskipun terdiri dari beberapa baris produk.
        - Kolom Total PO tidak ditampilkan pada hasil; rekap hanya menampilkan kolom warehouse dan kolom tambahan template yang relevan.
        - Jubelio menggunakan `No Pesanan`; Desty memprioritaskan `Nomor Pesanan (di Marketplace)` dan memakai nomor Desty sebagai cadangan jika kosong.
        - Status yang mengandung Cancel, Return/Retur, Unpaid, atau Belum Bayar dikeluarkan.
        - Status Paid, Completed, Processing, dan Shipped tetap dihitung.
        - Status Cancel, Return/Retur, Unpaid, dan Belum Bayar/Belum Dibayar dikeluarkan.
        - Tanggal mengikuti tanggal transaksi di file; aplikasi tidak membuat tanggal tambahan.
        - Warehouse yang tidak tersedia pada master Daily Sales All Client tidak dihitung dan dicatat di bagian/worksheet Tidak Terpetakan.
        - Tempat upload hanya menampilkan sumber yang ditetapkan untuk brand pada daftar Source DR.
        - CAVE, Yummys, NDR, Essens, BMYT, dan Aquila menggunakan Jubelio; Jamu Jago menggunakan Desty.
        - Bumi Tauhid dan Safwan menggunakan BigSeller, tetapi parser BigSeller belum diaktifkan.
        - Attaqwa menunggu konfirmasi sumber data.
        - Aqshor menggunakan Jubelio dan hasil marketplace dipisah menjadi sheet Shopee dan TikTok dengan susunan warehouse yang berbeda.
        """
    )
