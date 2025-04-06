document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("revenueCostChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const years = JSON.parse(document.getElementById("years").textContent);
    const revenues = JSON.parse(document.getElementById("revenues").textContent);
    const costs = JSON.parse(document.getElementById("costs").textContent);
    const ebits = JSON.parse(document.getElementById("ebits").textContent);
    const currency = JSON.parse(document.getElementById("currency").textContent);

    // Export PNG
    const exportBtn = document.getElementById("exportPNG");
    if (exportBtn) {
        exportBtn.addEventListener("click", function () {
            const link = document.createElement("a");
            link.download = "revenue_vs_cost_ebit.png";
            link.href = canvas.toDataURL("image/png");
            link.click();
        });
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Revenue',
                    data: revenues,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                },
                {
                    label: 'Cost',
                    data: costs,
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.formattedValue || '0';
                            const year = context.label;
                
                            // Caută EBIT-ul pentru acel an
                            const ebit = ebitData[year] !== undefined ? ebitData[year].toLocaleString() : 'N/A';
                
                            if (label === 'Revenue') {
                                return [`Revenue: ${value} ${currency}`, `EBIT: €${ebit}`];
                            } else if (label === 'Cost') {
                                return `Cost: ${value} ${currency}`;
                            } else {
                                return `${label}: ${value} ${currency}`;
                            }
                        }
                    }
                },                
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + ' ' + currency;
                        }
                    }
                }
            },
            animation: {
                onComplete: function() {
                    const chart = this.chart;
                    const ctx = chart.ctx;
                    ctx.font = 'bold 12px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillStyle = '#fff';

                    chart.data.labels.forEach((label, i) => {
                        const meta = chart.getDatasetMeta(0); // Revenue dataset
                        const bar = meta.data[i];
                        const ebit = ebits[i];
                        const x = bar.x;
                        const y = bar.y - 10;

                        ctx.fillText(`${ebit} ${currency}`, x, y);
                    });
                }
            }
        }
    });
});
