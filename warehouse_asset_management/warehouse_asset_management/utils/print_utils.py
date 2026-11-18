# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt
"""
مكتبة مشتركة للطباعة الاحترافية لجميع تقارير أصول المخازن
Shared Professional Print Utility — Warehouse Asset Management
"""

import frappe
from frappe.utils import nowdate, flt
import base64, os


BANK_NAME_AR = "المصرف الإسلامي الليبي"
BANK_NAME_EN = "Libyan Islamic Bank"
DEPT_NAME    = "قسم الأصول الثابتة"


def _get_logo_b64() -> str:
    """إرجاع اللوغو بصيغة base64 مضمّنة في HTML"""
    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "public", "bank_logo.png"
    )
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return ""


def fmt_currency(val, decimals=2) -> str:
    """تنسيق الأرقام بفواصل"""
    try:
        return f"{flt(val):,.{decimals}f}"
    except Exception:
        return str(val) if val else "—"


def status_badge_ar(status: str) -> str:
    """شارة ملوّنة للحالة"""
    if not status:
        return "—"
    MAP = {
        "In Location":          ("#1d7a4a", "#e8f7ef", "في الموقع"),
        "Disposed":             ("#c0392b", "#fdecea", "مُستبعَد"),
        "Scrapped":             ("#b7590a", "#fef5ec", "مُهلَك"),
        "Sold":                 ("#6c3483", "#f5eef8", "مُباع"),
        "Capitalized":          ("#1560b0", "#eaf2fb", "مُرسمَل"),
        "Partially Depreciated":("#856404", "#fff8e1", "مهلك جزئياً"),
        "Fully Depreciated":    ("#555e68", "#f0f2f5", "مهلك كلياً"),
        "Draft":                ("#555e68", "#f0f2f5", "مسودة"),
        # Arabic statuses (Asset Inventory)
        "في المخزن":            ("#1560b0", "#eaf2fb", "في المخزن"),
        "مسلم للموظف":          ("#6c3483", "#f5eef8", "مسلم للموظف"),
        "تم إنشاء أصل ثابت":   ("#1d7a4a", "#e8f7ef", "تم إنشاء أصل ثابت"),
    }
    color, bg, label = MAP.get(status, ("#555", "#f5f5f5", status))
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color}33;'
        f'padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700;'
        f'white-space:nowrap">{label}</span>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# القالب الأساسي الاحترافي
# ─────────────────────────────────────────────────────────────────────────────
_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

* { margin:0; padding:0; box-sizing:border-box; }

body {
  font-family: 'Cairo', 'Tahoma', sans-serif;
  direction: rtl; text-align: right;
  background: #f0f4f8;
  color: #1e2a3a;
  font-size: 13px;
  line-height: 1.6;
}

/* ── Toolbar ── */
.print-toolbar {
  position: sticky; top: 0; z-index: 9999;
  background: linear-gradient(135deg, #0d2137 0%, #1560b0 100%);
  padding: 10px 24px;
  display: flex; align-items: center; gap: 12px;
  box-shadow: 0 3px 12px rgba(0,0,0,.35);
}
.print-toolbar .tb-title { flex:1; text-align:center; color:#fff; font-size:15px; font-weight:700; }
.tb-btn {
  padding: 8px 20px; border: none; border-radius: 8px;
  cursor: pointer; font-family: 'Cairo', sans-serif;
  font-size: 13px; font-weight: 700; transition: all .2s;
}
.tb-btn-print { background: #27ae60; color: #fff; }
.tb-btn-print:hover { background: #1e8449; transform:scale(1.02); }
.tb-btn-close { background: rgba(255,255,255,.15); color: #fff; }
.tb-btn-close:hover { background: rgba(255,255,255,.28); }

/* ── Page ── */
.page { max-width: 1280px; margin: 20px auto; padding: 0 20px 50px; }

/* ── Header Card ── */
.report-header {
  background: linear-gradient(135deg, #0d2137 0%, #1560b0 80%, #c9a84c 100%);
  border-radius: 18px;
  padding: 0;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(13,33,55,.35);
  display: flex;
  min-height: 130px;
}
.header-logo-side {
  background: rgba(255,255,255,.07);
  border-left: 1px solid rgba(255,255,255,.12);
  padding: 24px 28px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  min-width: 160px;
}
.header-logo-side img {
  width: 72px; height: 72px; object-fit: contain;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,.3));
  border-radius: 8px;
  background: rgba(255,255,255,.08);
  padding: 6px;
}
.header-logo-side .bank-name-ar {
  color: #c9a84c; font-size: 12px; font-weight: 700;
  text-align: center; margin-top: 6px; line-height: 1.4;
}
.header-logo-side .bank-name-en {
  color: rgba(255,255,255,.6); font-size: 9px;
  text-align: center;
}
.header-center {
  flex: 1;
  padding: 24px 28px;
  display: flex; flex-direction: column; justify-content: center;
}
.header-center .report-title {
  color: #fff; font-size: 24px; font-weight: 900;
  margin-bottom: 4px; letter-spacing: -.3px;
}
.header-center .report-subtitle {
  color: rgba(255,255,255,.65); font-size: 12px;
}
.header-center .dept-badge {
  display: inline-block; margin-top: 10px;
  background: rgba(201,168,76,.2); border: 1px solid rgba(201,168,76,.5);
  color: #c9a84c; font-size: 11px; font-weight: 700;
  padding: 3px 14px; border-radius: 20px;
}
.header-meta-side {
  padding: 20px 24px;
  display: flex; flex-direction: column; justify-content: center;
  min-width: 200px;
  border-right: 1px solid rgba(255,255,255,.12);
}
.meta-row {
  display: flex; align-items: center; gap: 8px;
  color: rgba(255,255,255,.75); font-size: 11.5px;
  margin-bottom: 6px;
}
.meta-row .meta-label { color: rgba(255,255,255,.5); }
.meta-row .meta-val { color: #fff; font-weight: 700; }

/* ── KPI Cards ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.kpi-card {
  background: #fff;
  border-radius: 14px;
  padding: 18px 22px;
  box-shadow: 0 2px 14px rgba(0,0,0,.06);
  border-top: 4px solid;
  position: relative; overflow: hidden;
}
.kpi-card::after {
  content: ''; position: absolute; bottom:-20px; left:-20px;
  width:80px; height:80px; border-radius:50%;
  background: currentColor; opacity:.04;
}
.kpi-card.navy  { border-color: #1560b0; color: #1560b0; }
.kpi-card.green { border-color: #1d7a4a; color: #1d7a4a; }
.kpi-card.red   { border-color: #c0392b; color: #c0392b; }
.kpi-card.gold  { border-color: #c9a84c; color: #c9a84c; }
.kpi-card.purple{ border-color: #6c3483; color: #6c3483; }
.kpi-icon { font-size: 22px; margin-bottom: 6px; }
.kpi-label { font-size: 10.5px; color: #8899aa; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }
.kpi-value { font-size: 22px; font-weight: 900; color: #1e2a3a; line-height: 1.1; }
.kpi-unit  { font-size: 11px; color: #aab; margin-top: 3px; }

/* ── Section header ── */
.section-hdr {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 14px; padding: 10px 0 10px 0;
  border-bottom: 2px solid #e0e8f0;
}
.section-hdr h2 { font-size: 15px; font-weight: 800; color: #0d2137; }
.section-hdr .count-badge {
  background: #1560b0; color: #fff;
  border-radius: 20px; padding: 2px 12px;
  font-size: 11px; font-weight: 700;
}

/* ── Table ── */
.data-table {
  width: 100%; border-collapse: separate; border-spacing: 0;
  background: #fff;
  border-radius: 14px; overflow: hidden;
  box-shadow: 0 2px 18px rgba(0,0,0,.07);
}
.data-table thead tr th {
  background: linear-gradient(135deg, #0d2137, #1560b0);
  color: #fff;
  padding: 13px 12px;
  font-size: 11.5px; font-weight: 700;
  text-align: right; white-space: nowrap;
  border-left: 1px solid rgba(255,255,255,.08);
}
.data-table thead tr th:last-child { border-left: none; }
.data-table tbody td {
  padding: 11px 12px;
  border-bottom: 1px solid #eef2f7;
  font-size: 12px; vertical-align: middle;
}
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover { background: #f0f6ff !important; transition: background .15s; }
.data-table tbody tr.group-header td {
  background: linear-gradient(135deg, #0d2137, #1a3d72) !important;
  color: #fff !important; font-weight: 800 !important;
  font-size: 13px !important; padding: 12px 16px !important;
}
.data-table tfoot tr td {
  background: linear-gradient(135deg, #0d2137, #1560b0) !important;
  color: #fff !important; font-weight: 900 !important;
  font-size: 13px !important; padding: 13px 12px !important;
  border-top: 3px solid #c9a84c;
}

/* ── Number cells ── */
.num { text-align: left !important; font-variant-numeric: tabular-nums; }
.id-cell { color: #1560b0; font-weight: 700; font-size: 11px; }
.bold-name { font-weight: 700; color: #0d2137; }

/* ── Dep bar ── */
.dep-wrap { display:flex; flex-direction:column; gap:3px; }
.dep-bar-bg { height:5px; background:#eef2f7; border-radius:4px; overflow:hidden; }
.dep-bar-fill { height:100%; border-radius:4px; }

/* ── Footer ── */
.report-footer {
  margin-top: 28px; padding-top: 16px;
  border-top: 2px solid #e0e8f0;
  display: flex; justify-content: space-between; align-items: center;
}
.footer-left { color: #8899aa; font-size: 11px; line-height: 1.8; }
.footer-right { text-align: left; }
.sig-line {
  display: inline-block;
  min-width: 180px; border-top: 1.5px solid #1560b0;
  color: #1560b0; font-size: 11px; font-weight: 700;
  padding-top: 6px; margin-top: 30px; text-align: center;
}

/* ── Print ── */
@media print {
  body { background: #fff !important; font-size: 10.5px !important; }
  .print-toolbar { display: none !important; }
  .page { margin:0 !important; padding:0 !important; max-width:100% !important; }
  .kpi-card, .data-table { box-shadow: none !important; }
  .kpi-grid { gap: 10px !important; }
  .report-header { border-radius: 0 !important; margin-bottom: 14px !important; }
  @page { size: A4 landscape; margin: 12mm 10mm; }
}
"""


def build_print_html(
    report_title_ar: str,
    report_title_en: str,
    table_html: str,
    kpi_cards_html: str = "",
    filters_meta: dict = None,
    currency: str = "LYD",
    total_records: int = 0,
    extra_footer: str = ""
) -> str:
    """
    بناء صفحة HTML احترافية موحدة لأي تقرير.

    :param report_title_ar:  عنوان التقرير بالعربية
    :param report_title_en:  عنوان التقرير بالإنجليزية
    :param table_html:       HTML جدول البيانات (<table>…</table>)
    :param kpi_cards_html:   HTML بطاقات الإحصائيات (اختياري)
    :param filters_meta:     قاموس المرشحات للعرض في الرأسية
    :param currency:         رمز العملة
    :param total_records:    عدد السجلات
    """
    from frappe.utils import now_datetime, format_date

    logo_src = _get_logo_b64()
    logo_img = (
        f'<img src="{logo_src}" alt="شعار المصرف">'
        if logo_src else
        '<div style="width:72px;height:72px;background:rgba(255,255,255,.1);'
        'border-radius:8px;display:flex;align-items:center;justify-content:center;'
        'color:#c9a84c;font-size:28px">🏦</div>'
    )

    now = now_datetime()
    print_date_ar = format_date(nowdate(), "dd MMMM yyyy")
    print_time    = now.strftime("%H:%M")
    weekdays      = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
    weekday_ar    = weekdays[now.weekday()]

    # مرشحات التصفية
    meta_rows = ""
    if filters_meta:
        for label, val in filters_meta.items():
            if val:
                meta_rows += f"""
                <div class="meta-row">
                  <span class="meta-label">{label}:</span>
                  <span class="meta-val">{val}</span>
                </div>"""
    meta_rows += f"""
    <div class="meta-row">
      <span class="meta-label">📅</span>
      <span class="meta-val">{weekday_ar} — {print_date_ar}</span>
    </div>
    <div class="meta-row">
      <span class="meta-label">⏰</span>
      <span class="meta-val">{print_time}</span>
    </div>
    <div class="meta-row">
      <span class="meta-label">💰</span>
      <span class="meta-val">{currency}</span>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{report_title_ar} — {BANK_NAME_AR}</title>
<style>{_CSS}</style>
</head>
<body>

<!-- ── شريط الأدوات ── -->
<div class="print-toolbar" id="print-tb">
  <button class="tb-btn tb-btn-print" onclick="window.print()">🖨️ طباعة</button>
  <button class="tb-btn tb-btn-close" onclick="savePDF()">📄 حفظ PDF</button>
  <div class="tb-title">{report_title_ar} — {BANK_NAME_AR}</div>
  <button class="tb-btn tb-btn-close" onclick="window.close()">✕ إغلاق</button>
</div>

<div class="page">

  <!-- ── الرأسية ── -->
  <div class="report-header">

    <!-- اللوغو -->
    <div class="header-logo-side">
      {logo_img}
      <div class="bank-name-ar">{BANK_NAME_AR}</div>
      <div class="bank-name-en">{BANK_NAME_EN}</div>
    </div>

    <!-- العنوان -->
    <div class="header-center">
      <div class="report-title">{report_title_ar}</div>
      <div class="report-subtitle">{report_title_en}</div>
      <div class="dept-badge">🏛️ {DEPT_NAME}</div>
    </div>

    <!-- المعلومات الجانبية -->
    <div class="header-meta-side">
      {meta_rows}
    </div>

  </div>

  <!-- ── بطاقات الإحصائيات ── -->
  {f'<div class="kpi-grid">{kpi_cards_html}</div>' if kpi_cards_html else ""}

  <!-- ── عنوان القسم ── -->
  <div class="section-hdr">
    <h2>🗒️ تفاصيل البيانات</h2>
    <span class="count-badge">{total_records} سجل</span>
  </div>

  <!-- ── الجدول ── -->
  {table_html}

  <!-- ── الذيل ── -->
  <div class="report-footer">
    <div class="footer-left">
      <div><strong>{BANK_NAME_AR}</strong> · {DEPT_NAME}</div>
      <div>تاريخ الطباعة: {print_date_ar} · الساعة {print_time}</div>
      <div style="color:#c9a84c;font-size:10px;margin-top:2px">نظام إدارة أصول المخازن — ERPNext</div>
    </div>
    <div class="footer-right">
      <div class="sig-line">رئيس قسم الأصول الثابتة</div>
    </div>
  </div>
  {extra_footer}

</div>

<script>
function savePDF() {{
  document.getElementById('print-tb').style.display = 'none';
  window.print();
  setTimeout(() => document.getElementById('print-tb').style.display = 'flex', 1200);
}}
</script>
</body>
</html>"""


def kpi_card(icon: str, label: str, value: str, unit: str = "", color: str = "navy") -> str:
    return f"""
    <div class="kpi-card {color}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-unit">{unit}</div>
    </div>"""


def dep_bar(pct: float) -> str:
    """شريط تقدم الإهلاك"""
    clamped = min(max(pct, 0), 100)
    if pct >= 100:   bar_color = "#c0392b"
    elif pct >= 75:  bar_color = "#e67e22"
    elif pct >= 50:  bar_color = "#f39c12"
    else:            bar_color = "#1560b0"
    return (
        f'<div class="dep-wrap">'
        f'<span style="font-size:11px;font-weight:700;color:{bar_color}">'
        f'{pct:.1f}%</span>'
        f'<div class="dep-bar-bg">'
        f'<div class="dep-bar-fill" style="width:{clamped}%;background:{bar_color}"></div>'
        f'</div></div>'
    )
