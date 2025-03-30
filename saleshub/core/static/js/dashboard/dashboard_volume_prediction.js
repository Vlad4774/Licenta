document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("volumeProjectionChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    const labels = JSON.parse(document.getElementById("labels").textContent);
    const dataset1 = JSON.parse(document.getElementById("dataset1").textContent);
    const dataset2 = JSON.parse(document.getElementById("dataset2").textContent);
    const dataset3 = JSON.parse(document.getElementById("dataset3").textContent);
    const label1 = JSON.parse(document.getElementById("label1").textContent);
    const label2 = JSON.parse(document.getElementById("label2").textContent);
    const label3 = JSON.parse(document.getElementById("label3").textContent);

    const exportBtn = document.getElementById("exportPNG");
    if (exportBtn) {
        exportBtn.addEventListener("click", function () {
            const link = document.createElement("a");
            link.download = "volume_projection_chart.png";
            link.href = canvas.toDataURL("image/png");
            link.click();
        });
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: label1,
                    data: dataset1,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.3,
                    fill: false
                },
                {
                    label: label2,
                    data: dataset2,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.3,
                    fill: false
                },
                {
                    label: label3,
                    data: dataset3,
                    borderColor: 'rgba(255, 206, 86, 1)',
                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                    tension: 0.3,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.formattedValue}`;
                        }
                    }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    },
                    ticks: { color: '#ccc' },
                    grid: { color: '#333' }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Volume'
                    },
                    ticks: {
                        color: '#ccc',
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    },
                    grid: { color: '#333' }
                }
            }
        }
    });
});
