// PusulamNet - Chart.js Visualization Layer
class ChartManager {
    static instances = {};

    static getChartColor(cssVar, fallback) {
        const val = getComputedStyle(document.documentElement).getPropertyValue(cssVar).trim();
        return val || fallback;
    }

    static destroyChart(canvasId) {
        if (window.Chart && typeof Chart.getChart === 'function') {
            const existing = Chart.getChart(canvasId);
            if (existing) {
                try { existing.destroy(); } catch (e) {}
            }
        }
        if (this.instances[canvasId]) {
            try { this.instances[canvasId].destroy(); } catch (e) {}
            delete this.instances[canvasId];
        }
    }

    // 1. Toplam Net Gelişim Trend Çizgi Grafiği
    static renderTrendChart(canvasId, trendData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;

        const labels = trendData.map(d => d.date);
        const nets = trendData.map(d => d.total_net);
        const examNames = trendData.map(d => d.exam_name);

        const primaryColor = this.getChartColor('--accent-blue', '#3b82f6');
        const textColor = this.getChartColor('--text-secondary', '#94a3b8');
        const borderColor = this.getChartColor('--border-color', 'rgba(255,255,255,0.1)');

        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Toplam Net',
                    data: nets,
                    borderColor: primaryColor,
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: primaryColor,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: (items) => examNames[items[0].dataIndex] || items[0].label,
                            label: (item) => ` Net: ${item.formattedValue}`
                        }
                    }
                },
                scales: {
                    x: { grid: { color: borderColor }, ticks: { color: textColor } },
                    y: { grid: { color: borderColor }, ticks: { color: textColor } }
                }
            }
        });
    }

    // 2. Son Denemedeki Ders Netleri Sütun Grafiği
    static renderLatestCoursesChart(canvasId, coursesData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;

        const labels = coursesData.map(c => c.course_name);
        const nets = coursesData.map(c => c.net);
        const targetNets = coursesData.map(c => c.target_net);

        const blueColor = this.getChartColor('--accent-indigo', '#6366f1');
        const emeraldColor = this.getChartColor('--accent-emerald', '#10b981');
        const textColor = this.getChartColor('--text-secondary', '#94a3b8');
        const borderColor = this.getChartColor('--border-color', 'rgba(255,255,255,0.1)');

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Son Deneme Neti',
                        data: nets,
                        backgroundColor: blueColor,
                        borderRadius: 6
                    },
                    {
                        label: 'Hedef Net',
                        data: targetNets,
                        backgroundColor: 'rgba(16, 185, 129, 0.4)',
                        borderColor: emeraldColor,
                        borderWidth: 2,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: textColor } }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: textColor } },
                    y: { grid: { color: borderColor }, ticks: { color: textColor } }
                }
            }
        });
    }

    // 3. Doğru / Yanlış / Boş Dağılım Grafiği
    static renderAnswersBreakdownChart(canvasId, breakdownData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;

        const labels = breakdownData.map(d => d.date);
        const corrects = breakdownData.map(d => d.correct);
        const wrongs = breakdownData.map(d => d.wrong);
        const blanks = breakdownData.map(d => d.blank);

        const emerald = this.getChartColor('--accent-emerald', '#10b981');
        const rose = this.getChartColor('--accent-rose', '#f43f5e');
        const muted = this.getChartColor('--text-muted', '#64748b');
        const textColor = this.getChartColor('--text-secondary', '#94a3b8');
        const borderColor = this.getChartColor('--border-color', 'rgba(255,255,255,0.1)');

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Doğru', data: corrects, backgroundColor: emerald, borderRadius: 4 },
                    { label: 'Yanlış', data: wrongs, backgroundColor: rose, borderRadius: 4 },
                    { label: 'Boş', data: blanks, backgroundColor: muted, borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, grid: { display: false }, ticks: { color: textColor } },
                    y: { stacked: true, grid: { color: borderColor }, ticks: { color: textColor } }
                },
                plugins: { legend: { labels: { color: textColor } } }
            }
        });
    }

    // 4. Target vs Last 5 Chart
    static renderTargetVsLast5Chart(canvasId, comparisonData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;

        const labels = comparisonData.map(c => c.metric);
        const nets = comparisonData.map(c => c.net);

        const purple = this.getChartColor('--accent-purple', '#8b5cf6');
        const emerald = this.getChartColor('--accent-emerald', '#10b981');
        const textColor = this.getChartColor('--text-secondary', '#94a3b8');

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Net',
                    data: nets,
                    backgroundColor: [purple, emerald],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: textColor } },
                    y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: textColor } }
                }
            }
        });
    }

    // 5. Ders Özel Trend Çizgi Grafiği
    static renderCourseTrendChart(canvasId, chartData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;

        const labels = chartData.map(d => d.date);
        const nets = chartData.map(d => d.net);

        const purple = this.getChartColor('--accent-purple', '#8b5cf6');
        const textColor = this.getChartColor('--text-secondary', '#94a3b8');
        const borderColor = this.getChartColor('--border-color', 'rgba(255,255,255,0.1)');

        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.4)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ders Neti',
                    data: nets,
                    borderColor: purple,
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: borderColor }, ticks: { color: textColor } },
                    y: { grid: { color: borderColor }, ticks: { color: textColor } }
                }
            }
        });
    }
}
