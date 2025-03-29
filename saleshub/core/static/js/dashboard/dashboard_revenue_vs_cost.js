document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("chartRevenueCost");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    const years = JSON.parse(document.getElementById("years-range").textContent);
    const revenue = JSON.parse(document.getElementById("revenue-values").textContent);
    const cost = JSON.parse(document.getElementById("cost-values").textContent);
    const ebit = JSON.parse(document.getElementById("ebit-values").textContent);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Revenue',
                    data: revenue,
                    backgroundColor: 'hsl(200, 70%, 60%)'
                },
                {
                    label: 'Cost',
                    data: cost,
                    backgroundColor: 'hsl(0, 70%, 60%)'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        afterBody: function (context) {
                            const index = context[0].dataIndex;
                            return `EBIT: €${ebit[index].toFixed(2)}`;
                        }
                    }
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
