frappe.pages['waste_dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Smart Waste Management Dashboard',
		single_column: true
	});

	// Load Plotly from CDN if not present
	if (!window.Plotly) {
		$.getScript("https://cdn.plot.ly/plotly-2.24.1.min.js", function() {
			render_dashboard(page, wrapper);
		});
	} else {
		render_dashboard(page, wrapper);
	}
};

function render_dashboard(page, wrapper) {
	// Add primary action
	page.set_primary_action('Refresh', function() {
		load_dashboard_data(page, wrapper);
	}, 'fa fa-refresh');

	// Create request shortcuts
	page.add_inner_button('New Request', function() {
		frappe.new_doc('Waste Collection Request');
	});
	
	page.add_inner_button('Log Complaint', function() {
		frappe.new_doc('Waste Complaint');
	});

	// Inject Template HTML
	$(frappe.render_template("waste_dashboard", {})).appendTo($(wrapper).find(".layout-main-section"));

	load_dashboard_data(page, wrapper);
}

function load_dashboard_data(page, wrapper) {
	frappe.call({
		method: "waste_management.waste_management.page.waste_dashboard.waste_dashboard.get_dashboard_data",
		callback: function(r) {
			if (r.message) {
				var data = r.message;
				
				// Update KPIs
				$("#kpi-today-collections").text(data.kpis.today_collections);
				$("#kpi-active-fleet").text(data.kpis.active_fleet);
				$("#kpi-recycled-weight").text(data.kpis.recycled_weight + " kg");
				$("#kpi-driver-rating").text(data.kpis.avg_driver_rating + " ★");
				$("#kpi-pending-complaints").text(data.kpis.pending_complaints);

				// Update Recent Requests Table
				var req_html = "";
				data.recent_requests.forEach(function(req) {
					var risk_class = "risk-low";
					if (req.ai_risk_score >= 0.7) risk_class = "risk-high";
					else if (req.ai_risk_score >= 0.4) risk_class = "risk-medium";
					
					var status_class = "status-" + req.status.toLowerCase().replace(" ", "-");

					req_html += `<tr>
						<td><a href="/app/waste-collection-request/${req.name}"><b>${req.name}</b></a></td>
						<td>${req.zone}</td>
						<td>${req.waste_category}</td>
						<td><span class="priority-label priority-${req.priority.toLowerCase()}">${req.priority}</span></td>
						<td><span class="risk-badge ${risk_class}">${Math.round(req.ai_risk_score * 100)}%</span></td>
						<td><span class="status-badge ${status_class}">${req.status}</span></td>
					</tr>`;
				});
				$("#recent-requests-table").html(req_html || "<tr><td colspan='6' class='text-center'>No collection requests logged today.</td></tr>");

				// Update Disposal Sites capacity meters
				var site_html = "";
				data.sites.forEach(function(s) {
					var pct = Math.round(s.capacity_percentage);
					var bar_class = "bar-green";
					if (pct >= 90) bar_class = "bar-red";
					else if (pct >= 75) bar_class = "bar-orange";

					site_html += `<div class="site-item">
						<div class="site-header-info">
							<span class="site-name"><b>${s.site_name}</b> <small>(${s.site_type})</small></span>
							<span class="site-capacity">${s.current_capacity_used_tons} / ${s.total_capacity_tons} Tons</span>
						</div>
						<div class="progress-bar-container">
							<div class="progress-bar-fill ${bar_class}" style="width: ${pct}%"></div>
						</div>
						<div class="site-footer-info">
							<span>Used: ${pct}%</span>
							<a href="/app/waste-disposal-site/${s.name}" class="view-link">View Details →</a>
						</div>
					</div>`;
				});
				$("#site-capacity-list").html(site_html || "<div class='text-center'>No active disposal sites configured.</div>");

				// Build Charts
				build_trends_chart(data.trends);
				build_category_chart(data.categories);
			}
		}
	});
}

function build_trends_chart(trends) {
	var dates = trends.map(t => t.date);
	var actuals = trends.map(t => t.actual);
	var predictions = trends.map(t => t.predicted);

	var trace_actual = {
		x: dates,
		y: actuals,
		type: 'bar',
		name: 'Actual weight Collected',
		marker: {
			color: '#2ecc71',
			opacity: 0.8
		}
	};

	var trace_predict = {
		x: dates,
		y: predictions,
		type: 'scatter',
		mode: 'lines+markers',
		name: 'AI Forecast',
		line: {
			color: '#9b59b6',
			dash: 'dash',
			width: 3
		},
		marker: {
			size: 8,
			color: '#8e44ad'
		}
	};

	var layout = {
		paper_bgcolor: 'rgba(0,0,0,0)',
		plot_bgcolor: 'rgba(0,0,0,0)',
		font: { color: '#a0a0a0', family: 'Inter, sans-serif' },
		margin: { t: 30, b: 40, l: 55, r: 20 },
		legend: { orientation: 'h', y: -0.2 },
		xaxis: { gridcolor: '#f0f0f0', zeroline: false },
		yaxis: { gridcolor: '#f0f0f0', title: 'Weight (kg)' }
	};

	Plotly.newPlot('chart-weight-trends', [trace_actual, trace_predict], layout, {responsive: true, displayModeBar: false});
}

function build_category_chart(categories) {
	var labels = categories.map(c => c.waste_category);
	var values = categories.map(c => c.total_weight);

	var data = [{
		values: values,
		labels: labels,
		type: 'pie',
		hole: 0.4,
		marker: {
			colors: ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22', '#1abc9c']
		}
	}];

	var layout = {
		paper_bgcolor: 'rgba(0,0,0,0)',
		plot_bgcolor: 'rgba(0,0,0,0)',
		font: { color: '#a0a0a0', family: 'Inter, sans-serif' },
		margin: { t: 30, b: 30, l: 30, r: 30 },
		legend: { orientation: 'h', y: -0.1 }
	};

	Plotly.newPlot('chart-category-dist', data, layout, {responsive: true, displayModeBar: false});
}
