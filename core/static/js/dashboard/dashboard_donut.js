document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.querySelector("canvas.donut-chart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const canvasId = canvas.id;
    const currencyCode = canvas.dataset.currency || "EUR";
    const labels = JSON.parse(document.getElementById("labels").textContent);
    const values = JSON.parse(document.getElementById("values").textContent);

    const exportBtn = document.getElementById("exportPNG");
    if (exportBtn) {
        exportBtn.addEventListener("click", function () {
            const link = document.createElement("a");
            link.download = canvasId + ".png";
            link.href = canvas.toDataURL("image/png");
            link.click();
        });
    }

    const backgroundColors = labels.map(() => {
        const hue = Math.floor(Math.random() * 360);
        return `hsl(${hue}, 70%, 70%)`;
    });

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'left',
                    align: 'start',
                    labels: {
                        boxWidth: 20,
                        padding: 15,
                        color: '#ccc'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || '';
                            return `${label}: ${Number(value).toLocaleString()} ${currencyCode}`;
                        }
                    }
                }
            },
            layout: {
                padding: {
                    left: 30
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }        
    });
});
