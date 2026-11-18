// Asset Management Dashboard — لوحة إدارة الأصول الاحترافية (React / Executive Style)
// warehouse_asset_management/page/assets_dashboard/assets_dashboard.js

frappe.pages["assets-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "لوحة إدارة الأصول",
		single_column: true,
	});

	// ── حقل اختيار الشركة ─────────────────────────────────────────
	const companyField = page.add_field({
		fieldname: "company",
		label: __("Company"),
		fieldtype: "Link",
		options: "Company",
		default: frappe.defaults.get_user_default("Company"),
		change: () => loadDashboard(),
	});

	// ── زر تحديث ──────────────────────────────────────────────────
	page.add_inner_button(__("🔄 تحديث البيانات"), () => loadDashboard(), "btn-default");

	// ── حاوية المحتوى ─────────────────────────────────────────────
	$(wrapper).find(".page-content").html(`
		<div id="asset-dash-root" style="padding:12px 6px; font-family:'Tajawal','Inter',sans-serif; direction:rtl; background-color:#f8fafc; min-height:85vh">
			<div id="dash-loading" style="display:flex; flex-direction:column; align-items:center; justify-center; padding:100px 0; color:#64748b">
				<div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem; margin-bottom:16px"></div>
				<div style="font-weight:600; font-size:15px">جاري تحميل لوحة التحكم...</div>
			</div>
		</div>
	`);

	let chartInstances = {};

	// ── تحميل البيانات ─────────────────────────────────────────────
	function loadDashboard() {
		const company = companyField.get_value();
		if (!company) return;

		$("#dash-loading").show();
		$("#asset-dash-content").remove();

		// Destroy previous ApexCharts instances
		Object.values(chartInstances).forEach((chart) => {
			try { chart.destroy(); } catch (e) {}
		});
		chartInstances = {};

		frappe.call({
			method: "warehouse_asset_management.warehouse_asset_management.page.assets_dashboard.assets_dashboard.get_dashboard_data",
			args: { company },
			callback: (r) => {
				$("#dash-loading").hide();
				if (r.message && !r.message.error) {
					renderDashboard(r.message);
				} else {
					$("#asset-dash-root").html(
						`<div style="margin:60px auto; max-width:420px; text-align:center; background:#fff; padding:32px; border-radius:16px; box-shadow:0 4px 20px rgba(0,0,0,0.05); border:1px solid #e2e8f0">
							<div style="font-size:40px; margin-bottom:12px">📂</div>
							<div style="font-size:16px; font-weight:700; color:#1e293b; margin-bottom:6px">لا توجد بيانات أصول</div>
							<div style="font-size:13px; color:#64748b">${r.message?.error || "الرجاء التأكد من وجود أصول مرحلة للشركة المختارة"}</div>
						</div>`
					);
				}
			},
		});
	}

	// ── رسم اللوحة العصرية (React / Executive Dashboard Style) ─────
	function renderDashboard(data) {
		const { kpi, by_category, by_location, by_cost_center, status_count, alerts, upcoming_depreciation, monthly_timeline } = data;
		const cc = "LYD";

		const html = `
<div id="asset-dash-content" class="react-dash-wrapper">

	<!-- ═══ Top Summary KPI Bar (Shadcn Mini-Card Grid) ════════════ -->
	<div class="kpi-grid">
		<div class="kpi-box blue">
			<div class="kpi-top">
				<span class="kpi-title">إجمالي الأصول</span>
				<div class="kpi-icon-wrap blue">🏛️</div>
			</div>
			<div class="kpi-num">${kpi.total_assets} <span class="kpi-unit">أصل</span></div>
			<div class="kpi-sub-badge blue">مسجلة بالكامل</div>
		</div>

		<div class="kpi-box green">
			<div class="kpi-top">
				<span class="kpi-title">إجمالي تكلفة الشراء</span>
				<div class="kpi-icon-wrap green">💵</div>
			</div>
			<div class="kpi-num">${fmtNum(kpi.total_cost)} <span class="kpi-unit">${cc}</span></div>
			<div class="kpi-sub-badge green">القيمة الدفترية الأصلية</div>
		</div>

		<div class="kpi-box red">
			<div class="kpi-top">
				<span class="kpi-title">إجمالي الإهلاك المتراكم</span>
				<div class="kpi-icon-wrap red">📉</div>
			</div>
			<div class="kpi-num">${fmtNum(kpi.total_dep)} <span class="kpi-unit">${cc}</span></div>
			<div class="kpi-sub-badge red">معدل الإهلاك ${kpi.dep_pct}%</div>
		</div>

		<div class="kpi-box purple">
			<div class="kpi-top">
				<span class="kpi-title">صافي القيمة الحالية</span>
				<div class="kpi-icon-wrap purple">✨</div>
			</div>
			<div class="kpi-num">${fmtNum(kpi.total_value)} <span class="kpi-unit">${cc}</span></div>
			<div class="kpi-sub-badge purple">القيمة الصافية المتبقية</div>
		</div>
	</div>

	<!-- ═══ Alerts Container (If Any) ═══════════════════════════════ -->
	${alerts && alerts.length ? renderAlertsBanner(alerts) : ""}

	<!-- ═══ Row 1: Category Comparison & Asset Status ═══════════════ -->
	<div class="dash-row two-cols">
		<div class="dash-card">
			<div class="dash-card-header">
				<div>
					<div class="dash-card-title">فئات الأصول والثمن الأصلي مقابل الإهلاك</div>
					<div class="dash-card-subtitle">مقارنة القيمة الأصلية والإهلاك لكل فئة</div>
				</div>
			</div>
			<div class="chart-container">
				<div id="apex-category-chart"></div>
			</div>
		</div>

		<div class="dash-card">
			<div class="dash-card-header">
				<div>
					<div class="dash-card-title">توزيع حالة الأصول</div>
					<div class="dash-card-subtitle">نسب الحالات التشغيلية والمالية للأصول</div>
				</div>
			</div>
			<div class="chart-container">
				<div id="apex-status-chart"></div>
			</div>
		</div>
	</div>

	<!-- ═══ Row 2: Timeline & Location & Cost Center ═══════════════ -->
	<div class="dash-row three-cols">
		<div class="dash-card">
			<div class="dash-card-header">
				<div>
					<div class="dash-card-title">تتبع الإهلاك الشهري</div>
					<div class="dash-card-subtitle">النمو الزمني لقيود الإهلاك (آخر 12 شهر)</div>
				</div>
			</div>
			<div class="chart-container">
				<div id="apex-timeline-chart"></div>
			</div>
		</div>

		<div class="dash-card">
			<div class="dash-card-header">
				<div>
					<div class="dash-card-title">الأصول حسب مراكز التكلفة</div>
					<div class="dash-card-subtitle">صافي قيمة الأصول لكل مركز</div>
				</div>
			</div>
			<div class="chart-container">
				<div id="apex-costcenter-chart"></div>
			</div>
		</div>

		<div class="dash-card">
			<div class="dash-card-header">
				<div>
					<div class="dash-card-title">التوزيع حسب الموقع</div>
					<div class="dash-card-subtitle">توزيع التكلفة حسب المقرات والأماكن</div>
				</div>
			</div>
			<div class="chart-container">
				<div id="apex-location-chart"></div>
			</div>
		</div>
	</div>

	<!-- ═══ Row 3: Detail Tables ═══════════════════════════════════ -->
	<div class="dash-row two-cols">
		<div class="dash-card">
			<div class="dash-card-header">
				<div class="dash-card-title">📋 تفاصيل وقيم فئات الأصول</div>
			</div>
			${renderCategoryTable(by_category, kpi.total_cost, cc)}
		</div>

		<div class="dash-card">
			<div class="dash-card-header">
				<div class="dash-card-title">⏰ جدول الإهلاك القادم (3 أشهر)</div>
			</div>
			${renderUpcomingTable(upcoming_depreciation, cc)}
		</div>
	</div>

</div>

<!-- ═══ CSS Design System (Executive React / Shadcn UI Palette) ════ -->
<style>
.react-dash-wrapper {
	max-width: 1440px;
	margin: 0 auto;
	display: flex;
	flex-direction: column;
	gap: 16px;
}

/* KPI Grid */
.kpi-grid {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 14px;
}

@media (max-width: 1024px) {
	.kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
	.kpi-grid { grid-template-columns: 1fr; }
}

.kpi-box {
	background: #ffffff;
	border-radius: 12px;
	padding: 16px 20px;
	border: 1px solid #e2e8f0;
	box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	transition: all 0.2s ease;
}
.kpi-box:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 12px 0 rgba(15, 23, 42, 0.08);
}

.kpi-top {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 8px;
}
.kpi-title {
	font-size: 12px;
	font-weight: 600;
	color: #64748b;
}
.kpi-icon-wrap {
	width: 34px;
	height: 34px;
	border-radius: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 16px;
}
.kpi-icon-wrap.blue   { background: #eff6ff; }
.kpi-icon-wrap.green  { background: #f0fdf4; }
.kpi-icon-wrap.red    { background: #fef2f2; }
.kpi-icon-wrap.purple { background: #faf5ff; }

.kpi-num {
	font-size: 22px;
	font-weight: 800;
	color: #0f172a;
	letter-spacing: -0.5px;
	margin-bottom: 6px;
}
.kpi-unit {
	font-size: 12px;
	font-weight: 600;
	color: #94a3b8;
}

.kpi-sub-badge {
	display: inline-block;
	width: fit-content;
	font-size: 11px;
	font-weight: 600;
	padding: 2px 8px;
	border-radius: 6px;
}
.kpi-sub-badge.blue   { background: #eff6ff; color: #2563eb; }
.kpi-sub-badge.green  { background: #f0fdf4; color: #16a34a; }
.kpi-sub-badge.red    { background: #fef2f2; color: #dc2626; }
.kpi-sub-badge.purple { background: #faf5ff; color: #9333ea; }

/* Grid Rows */
.dash-row { display: grid; gap: 16px; }
.dash-row.two-cols { grid-template-columns: 1fr 1fr; }
.dash-row.three-cols { grid-template-columns: 1.2fr 1fr 1fr; }

@media (max-width: 1024px) {
	.dash-row.two-cols, .dash-row.three-cols { grid-template-columns: 1fr; }
}

/* Card Styling */
.dash-card {
	background: #ffffff;
	border-radius: 12px;
	padding: 18px 20px;
	border: 1px solid #e2e8f0;
	box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
	display: flex;
	flex-direction: column;
}
.dash-card-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 12px;
	padding-bottom: 10px;
	border-bottom: 1px solid #f1f5f9;
}
.dash-card-title {
	font-size: 14px;
	font-weight: 700;
	color: #0f172a;
}
.dash-card-subtitle {
	font-size: 11px;
	color: #94a3b8;
	margin-top: 2px;
}

.chart-container {
	position: relative;
	min-height: 240px;
	width: 100%;
}

/* Alerts */
.alerts-banner {
	background: #fff;
	border: 1px solid #fecaca;
	border-radius: 12px;
	padding: 12px 16px;
	display: flex;
	align-items: center;
	gap: 12px;
	box-shadow: 0 1px 3px rgba(239, 68, 68, 0.05);
}
.alert-chip {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	background: #fef2f2;
	color: #991b1b;
	border: 1px solid #fee2e2;
	padding: 4px 10px;
	border-radius: 8px;
	font-size: 12px;
	font-weight: 600;
}

/* Table Styling */
.clean-table {
	width: 100%;
	border-collapse: collapse;
	font-size: 12px;
}
.clean-table th {
	background: #f8fafc;
	color: #475569;
	font-weight: 700;
	font-size: 11px;
	padding: 10px 12px;
	border-bottom: 1px solid #e2e8f0;
	text-align: right;
}
.clean-table td {
	padding: 10px 12px;
	border-bottom: 1px solid #f1f5f9;
	color: #334155;
}
.clean-table tr:last-child td {
	border-bottom: none;
}
.clean-table tr:hover td {
	background: #f8fafc;
}
.progress-bar-bg {
	width: 100%;
	height: 6px;
	background: #e2e8f0;
	border-radius: 4px;
	overflow: hidden;
	margin-top: 4px;
}
.progress-bar-fill {
	height: 100%;
	border-radius: 4px;
}
</style>
`;

		$("#asset-dash-root").html(html);

		// ── تهيئة الرسوم البيانية الحديثة (ApexCharts) ───────────
		setTimeout(() => {
			initCategoryChart(by_category);
			initStatusChart(status_count);
			initTimelineChart(monthly_timeline);
			initCostCenterChart(by_cost_center);
			initLocationChart(by_location);
		}, 100);
	}

	// ── 1. Category Column Chart (ApexCharts) ──────────────────────
	function initCategoryChart(by_category) {
		const categories = Object.keys(by_category);
		const costData = categories.map((c) => Math.round(by_category[c].cost));
		const depData = categories.map((c) => Math.round(by_category[c].dep));

		const options = {
			series: [
				{ name: "التكلفة الأصلية", data: costData },
				{ name: "الإهلاك المتراكم", data: depData },
			],
			chart: {
				type: "bar",
				height: 240,
				fontFamily: "Tajawal, sans-serif",
				toolbar: { show: false },
				animations: { enabled: true, speed: 500 },
			},
			plotOptions: {
				bar: {
					horizontal: false,
					columnWidth: "40%",
					borderRadius: 6,
					borderRadiusApplication: "end",
				},
			},
			colors: ["#2563eb", "#ef4444"],
			dataLabels: { enabled: false },
			stroke: { show: true, width: 2, colors: ["transparent"] },
			xaxis: {
				categories: categories.map((c) => c.length > 18 ? c.substring(0, 18) + "..." : c),
				labels: { style: { colors: "#64748b", fontSize: "11px" } },
				axisBorder: { show: false },
				axisTicks: { show: false },
			},
			yaxis: {
				labels: {
					style: { colors: "#64748b", fontSize: "11px" },
					formatter: (val) => fmtShort(val),
				},
			},
			legend: {
				position: "top",
				horizontalAlign: "right",
				fontSize: "12px",
				fontFamily: "Tajawal",
				markers: { radius: 12 },
			},
			fill: { opacity: 1 },
			tooltip: {
				y: { formatter: (val) => fmtNum(val) + " LYD" },
			},
			grid: { borderColor: "#f1f5f9", strokeDashArray: 3 },
		};

		const elem = document.querySelector("#apex-category-chart");
		if (elem) {
			chartInstances.category = new ApexCharts(elem, options);
			chartInstances.category.render();
		}
	}

	// ── 2. Status Donut Chart (ApexCharts) ─────────────────────────
	function initStatusChart(status_count) {
		const labelsMap = {
			"In Location": "في الموقع",
			"Disposed": "مُستبعَد",
			"Scrapped": "مُهلَك",
			"Sold": "مُباع",
			"Capitalized": "مُرسمَل",
			"Partially Depreciated": "مُهلَك جزئياً",
			"Fully Depreciated": "مُهلَك كلياً",
		};
		const rawLabels = Object.keys(status_count);
		const series = Object.values(status_count);
		const labels = rawLabels.map((l) => labelsMap[l] || l);

		const options = {
			series: series,
			labels: labels,
			chart: {
				type: "donut",
				height: 240,
				fontFamily: "Tajawal, sans-serif",
			},
			colors: ["#16a34a", "#dc2626", "#ea580c", "#9333ea", "#2563eb", "#d97706", "#64748b"],
			plotOptions: {
				pie: {
					donut: {
						size: "72%",
						labels: {
							show: true,
							total: {
								show: true,
								label: "إجمالي الأصول",
								fontSize: "12px",
								fontFamily: "Tajawal",
								color: "#64748b",
								formatter: (w) => w.globals.seriesTotals.reduce((a, b) => a + b, 0),
							},
						},
					},
				},
			},
			legend: {
				position: "left",
				fontSize: "12px",
				fontFamily: "Tajawal",
				markers: { radius: 12 },
				itemMargin: { vertical: 3 },
			},
			dataLabels: { enabled: false },
			stroke: { width: 0 },
		};

		const elem = document.querySelector("#apex-status-chart");
		if (elem) {
			chartInstances.status = new ApexCharts(elem, options);
			chartInstances.status.render();
		}
	}

	// ── 3. Monthly Timeline Area Chart (ApexCharts) ────────────────
	function initTimelineChart(monthly_timeline) {
		const labels = monthly_timeline.map((m) => m.month_label);
		const seriesData = monthly_timeline.map((m) => Math.round(parseFloat(m.dep_amount) || 0));

		const options = {
			series: [{ name: "قسط الإهلاك الشهري", data: seriesData }],
			chart: {
				type: "area",
				height: 220,
				fontFamily: "Tajawal, sans-serif",
				toolbar: { show: false },
				sparkline: { enabled: false },
			},
			colors: ["#2563eb"],
			stroke: { curve: "smooth", width: 2.5 },
			fill: {
				type: "gradient",
				gradient: {
					shadeIntensity: 1,
					opacityFrom: 0.35,
					opacityTo: 0.05,
					stops: [0, 95, 100],
				},
			},
			dataLabels: { enabled: false },
			xaxis: {
				categories: labels,
				labels: { style: { colors: "#64748b", fontSize: "11px" } },
				axisBorder: { show: false },
				axisTicks: { show: false },
			},
			yaxis: {
				labels: {
					style: { colors: "#64748b", fontSize: "11px" },
					formatter: (val) => fmtShort(val),
				},
			},
			tooltip: {
				y: { formatter: (val) => fmtNum(val) + " LYD" },
			},
			grid: { borderColor: "#f1f5f9", strokeDashArray: 3 },
		};

		const elem = document.querySelector("#apex-timeline-chart");
		if (elem) {
			chartInstances.timeline = new ApexCharts(elem, options);
			chartInstances.timeline.render();
		}
	}

	// ── 4. Cost Center Horizontal Bar Chart (ApexCharts) ───────────
	function initCostCenterChart(by_cost_center) {
		const entries = Object.entries(by_cost_center).sort((a, b) => b[1].cost - a[1].cost).slice(0, 5);
		const categories = entries.map(([k]) => k.split(" - ")[0]);
		const seriesData = entries.map(([, v]) => Math.round(v.value));

		const options = {
			series: [{ name: "صافي القيمة", data: seriesData }],
			chart: {
				type: "bar",
				height: 220,
				fontFamily: "Tajawal, sans-serif",
				toolbar: { show: false },
			},
			plotOptions: {
				bar: {
					horizontal: true,
					barHeight: "45%",
					borderRadius: 6,
					borderRadiusApplication: "end",
				},
			},
			colors: ["#0d9488"],
			dataLabels: { enabled: false },
			xaxis: {
				labels: {
					style: { colors: "#64748b", fontSize: "11px" },
					formatter: (val) => fmtShort(val),
				},
			},
			yaxis: {
				labels: { style: { colors: "#475569", fontSize: "11px", fontWeight: 600 } },
			},
			tooltip: {
				y: { formatter: (val) => fmtNum(val) + " LYD" },
			},
			grid: { borderColor: "#f1f5f9", strokeDashArray: 3 },
		};

		const elem = document.querySelector("#apex-costcenter-chart");
		if (elem) {
			chartInstances.costcenter = new ApexCharts(elem, options);
			chartInstances.costcenter.render();
		}
	}

	// ── 5. Location Pie Chart (ApexCharts) ─────────────────────────
	function initLocationChart(by_location) {
		const entries = Object.entries(by_location);
		const labels = entries.map(([k]) => k);
		const seriesData = entries.map(([, v]) => Math.round(v.cost));

		const options = {
			series: seriesData,
			labels: labels,
			chart: {
				type: "pie",
				height: 220,
				fontFamily: "Tajawal, sans-serif",
			},
			colors: ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b"],
			legend: {
				position: "bottom",
				fontSize: "12px",
				fontFamily: "Tajawal",
			},
			dataLabels: { enabled: false },
			tooltip: {
				y: { formatter: (val) => fmtNum(val) + " LYD" },
			},
		};

		const elem = document.querySelector("#apex-location-chart");
		if (elem) {
			chartInstances.location = new ApexCharts(elem, options);
			chartInstances.location.render();
		}
	}

	// ── Tables Helpers ─────────────────────────────────────────────
	function renderCategoryTable(by_category, totalCost, cc) {
		const rows = Object.entries(by_category).map(([cat, v]) => {
			const pct = totalCost ? ((v.cost / totalCost) * 100).toFixed(1) : 0;
			const depPct = v.cost ? ((v.dep / v.cost) * 100).toFixed(1) : 0;
			return `<tr>
				<td style="font-weight:600; color:#0f172a">${cat}</td>
				<td style="text-align:center"><span style="background:#f1f5f9; padding:2px 8px; border-radius:6px; font-weight:700">${v.count}</span></td>
				<td style="text-align:left; font-weight:600">${fmtNum(v.cost)}</td>
				<td style="text-align:left; color:#dc2626">${fmtNum(v.dep)}</td>
				<td style="width:110px">
					<div style="display:flex; justify-content:space-between; font-size:10px; color:#64748b; margin-bottom:2px">
						<span>إهلاك</span>
						<span style="font-weight:700">${depPct}%</span>
					</div>
					<div class="progress-bar-bg">
						<div class="progress-bar-fill" style="width:${Math.min(depPct, 100)}%; background:${depPct > 80 ? '#dc2626' : '#2563eb'}"></div>
					</div>
				</td>
			</tr>`;
		}).join("");

		return `<div style="overflow-x:auto">
			<table class="clean-table">
				<thead>
					<tr>
						<th>فئة الأصل</th>
						<th style="text-align:center">العدد</th>
						<th style="text-align:left">التكلفة</th>
						<th style="text-align:left">الإهلاك</th>
						<th>نسبة الإهلاك</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>
		</div>`;
	}

	function renderUpcomingTable(upcoming, cc) {
		if (!upcoming || !upcoming.length) {
			return `<div style="text-align:center; color:#94a3b8; padding:40px 0; font-size:13px">لا توجد أقساط إهلاك قادمة خلال الـ 3 أشهر القادمة</div>`;
		}

		const rows = upcoming.slice(0, 6).map((u) => `
			<tr>
				<td>
					<a href="/app/asset/${u.asset_id}" style="font-weight:700; color:#2563eb; text-decoration:none">${u.asset_name}</a>
					<div style="font-size:10px; color:#94a3b8">${u.asset_category || ''}</div>
				</td>
				<td style="color:#64748b; font-size:11px; white-space:nowrap">${u.schedule_date}</td>
				<td style="text-align:left; font-weight:700; color:#dc2626">${fmtNum(u.depreciation_amount)} ${cc}</td>
			</tr>
		`).join("");

		return `<div style="overflow-x:auto">
			<table class="clean-table">
				<thead>
					<tr>
						<th>الأصل</th>
						<th>تاريخ القسط</th>
						<th style="text-align:left">مبلغ القسط</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>
		</div>`;
	}

	function renderAlertsBanner(alerts) {
		const chips = alerts.slice(0, 4).map((a) => `
			<div class="alert-chip">
				<span>${a.icon}</span>
				<span>${a.asset}: ${a.detail}</span>
			</div>
		`).join("");

		return `<div class="alerts-banner">
			<span style="font-weight:700; color:#991b1b; font-size:13px; white-space:nowrap">⚠️ تنبيهات الإهلاك:</span>
			<div style="display:flex; gap:8px; flex-wrap:wrap; flex:1">${chips}</div>
		</div>`;
	}

	// ── Formatters ────────────────────────────────────────────────
	function fmtNum(v) {
		return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(Math.round(v || 0));
	}
	function fmtShort(v) {
		if (v >= 1e6) return (v / 1e6).toFixed(1) + "M";
		if (v >= 1e3) return (v / 1e3).toFixed(0) + "K";
		return v;
	}

	// ── تحميل مكتبة ApexCharts إذا لم تكن محمّلة ──────────────────
	function ensureApexCharts(cb) {
		if (window.ApexCharts) return cb();
		const script = document.createElement("script");
		script.src = "https://cdn.jsdelivr.net/npm/apexcharts@3.45.1/dist/apexcharts.min.js";
		script.onload = cb;
		document.head.appendChild(script);
	}

	// ── تحميل خط Tajawal ──────────────────────────────────────────
	if (!document.getElementById("tajawal-font")) {
		const link = document.createElement("link");
		link.id = "tajawal-font";
		link.rel = "stylesheet";
		link.href = "https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;600;700;800&display=swap";
		document.head.appendChild(link);
	}

	// ── التبديل والتشغيل ─────────────────────────────────────────
	ensureApexCharts(() => loadDashboard());
};
