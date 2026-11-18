# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, nowdate, add_months, getdate, date_diff


@frappe.whitelist()
def get_dashboard_data(company=None):
    """جلب جميع بيانات لوحة إدارة الأصول."""

    if not company:
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
            "Global Defaults", "default_company"
        )

    filters = {"docstatus": 1, "company": company}

    # ── جميع الأصول المرحّلة ──────────────────────────────────────────
    assets = frappe.get_all(
        "Asset",
        filters=filters,
        fields=[
            "name",
            "asset_name",
            "asset_category",
            "status",
            "location",
            "cost_center",
            "net_purchase_amount",
            "purchase_date",
            "available_for_use_date",
            "calculate_depreciation",
        ],
    )

    if not assets:
        return {"error": "لا توجد أصول مرحّلة"}

    # ── خريطة الإهلاك المتراكم والقيم الحالية ────────────────────────
    dep_map = _get_depreciation_map(company)

    total_cost = 0.0
    total_dep = 0.0
    total_value = 0.0

    by_category = {}
    by_location = {}
    by_cost_center = {}
    alerts = []
    status_count = {}

    today = getdate(nowdate())

    for a in assets:
        dep = flt(dep_map.get(a.name, 0))
        cost = flt(a.net_purchase_amount)
        value = cost - dep

        total_cost += cost
        total_dep += dep
        total_value += value

        # ── تصنيف حسب الفئة
        cat = a.asset_category or "غير محدد"
        if cat not in by_category:
            by_category[cat] = {"count": 0, "cost": 0.0, "dep": 0.0, "value": 0.0}
        by_category[cat]["count"] += 1
        by_category[cat]["cost"] += cost
        by_category[cat]["dep"] += dep
        by_category[cat]["value"] += value

        # ── تصنيف حسب الموقع
        loc = a.location or "غير محدد"
        if loc not in by_location:
            by_location[loc] = {"count": 0, "cost": 0.0, "value": 0.0}
        by_location[loc]["count"] += 1
        by_location[loc]["cost"] += cost
        by_location[loc]["value"] += value

        # ── تصنيف حسب مركز التكلفة
        cc = a.cost_center or "غير محدد"
        if cc not in by_cost_center:
            by_cost_center[cc] = {"count": 0, "cost": 0.0, "value": 0.0}
        by_cost_center[cc]["count"] += 1
        by_cost_center[cc]["cost"] += cost
        by_cost_center[cc]["value"] += value

        # ── الحالة
        st = a.status or "Unknown"
        status_count[st] = status_count.get(st, 0) + 1

        # ── التنبيهات
        dep_pct = (dep / cost * 100) if cost else 0
        if dep_pct >= 100:
            alerts.append({
                "type": "danger",
                "icon": "🔴",
                "title": "أصل مُستهلك بالكامل",
                "asset": a.asset_name,
                "asset_id": a.name,
                "detail": f"تكلفة: {cost:,.0f} LYD | إهلاك: {dep:,.0f} LYD (100%)",
            })
        elif dep_pct >= 80:
            alerts.append({
                "type": "warning",
                "icon": "🟠",
                "title": "أصل قارب الاستهلاك الكامل",
                "asset": a.asset_name,
                "asset_id": a.name,
                "detail": f"نسبة الإهلاك: {dep_pct:.1f}%",
            })

    # ── جدول الإهلاك القادم (أقرب 3 أشهر) ──────────────────────────
    upcoming = _get_upcoming_depreciation(company)

    # ── بيانات المخطط الزمني (آخر 12 شهر) ──────────────────────────
    monthly_timeline = _get_monthly_timeline(company)

    return {
        "company": company,
        "kpi": {
            "total_assets": len(assets),
            "total_cost": total_cost,
            "total_dep": total_dep,
            "total_value": total_value,
            "dep_pct": round((total_dep / total_cost * 100) if total_cost else 0, 1),
        },
        "by_category": by_category,
        "by_location": by_location,
        "by_cost_center": by_cost_center,
        "status_count": status_count,
        "alerts": alerts[:20],  # أقصى 20 تنبيه
        "upcoming_depreciation": upcoming,
        "monthly_timeline": monthly_timeline,
    }


def _get_depreciation_map(company):
    """إجمالي الإهلاك المتراكم لكل أصل."""
    rows = frappe.db.sql(
        """
        SELECT gle.against_voucher, SUM(gle.debit) as total_dep
        FROM `tabGL Entry` gle
        JOIN `tabAsset` a ON a.name = gle.against_voucher
        JOIN `tabAsset Category Account` aca
            ON aca.parent = a.asset_category AND aca.company_name = a.company
        WHERE gle.account = aca.depreciation_expense_account
          AND gle.debit != 0
          AND gle.is_cancelled = 0
          AND gle.is_opening = 'No'
          AND a.company = %s
          AND a.docstatus = 1
        GROUP BY gle.against_voucher
        """,
        company,
        as_dict=True,
    )
    return {r.against_voucher: flt(r.total_dep) for r in rows}


def _get_upcoming_depreciation(company):
    """أقساط الإهلاك المستحقة في الـ 3 أشهر القادمة."""
    today = nowdate()
    future = add_months(today, 3)
    rows = frappe.db.sql(
        """
        SELECT
            a.name as asset_id,
            a.asset_name,
            a.asset_category,
            ds.schedule_date,
            ds.depreciation_amount
        FROM `tabAsset Depreciation Schedule` ads
        JOIN `tabDepreciation Schedule` ds ON ds.parent = ads.name
        JOIN `tabAsset` a ON a.name = ads.asset
        WHERE ads.status = 'Active'
          AND a.company = %s
          AND a.docstatus = 1
          AND ds.journal_entry IS NULL
          AND ds.schedule_date BETWEEN %s AND %s
        ORDER BY ds.schedule_date ASC
        LIMIT 30
        """,
        (company, today, future),
        as_dict=True,
    )
    return rows


def _get_monthly_timeline(company):
    """إجمالي الإهلاك الشهري خلال آخر 12 شهر."""
    start = add_months(nowdate(), -12)
    rows = frappe.db.sql(
        """
        SELECT
            DATE_FORMAT(gle.posting_date, '%%Y-%%m') as month_key,
            DATE_FORMAT(gle.posting_date, '%%b %%Y') as month_label,
            SUM(gle.debit) as dep_amount
        FROM `tabGL Entry` gle
        JOIN `tabAsset` a ON a.name = gle.against_voucher
        JOIN `tabAsset Category Account` aca
            ON aca.parent = a.asset_category AND aca.company_name = a.company
        WHERE gle.account = aca.depreciation_expense_account
          AND gle.debit != 0
          AND gle.is_cancelled = 0
          AND gle.is_opening = 'No'
          AND a.company = %s
          AND gle.posting_date >= %s
        GROUP BY month_key
        ORDER BY month_key ASC
        """,
        (company, start),
        as_dict=True,
    )
    return rows
