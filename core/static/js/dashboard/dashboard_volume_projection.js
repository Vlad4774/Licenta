document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("chartVolumeProjection");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    const years = JSON.parse(document.getElementById("years-range").textContent);
    const minVol = JSON.parse(document.getElementById("volume-min").textContent);
    const expVol = JSON.parse(document.getElementById("volume-exp").textContent);
    const maxVol = JSON.parse(document.getElementById("volume-max").textContent);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Min Volume',
                    data: minVol,
                    borderColor: 'hsl(200, 70%, 60%)',
                    backgroundColor: 'transparent',
                    tension: 0.3
                },
                {
                    label: 'Expected Volume',
                    data: expVol,
                    borderColor: 'hsl(120, 70%, 60%)',
                    backgroundColor: 'transparent',
                    tension: 0.3
                },
                {
                    label: 'Max Volume',
                    data: maxVol,
                    borderColor: 'hsl(300, 70%, 60%)',
                    backgroundColor: 'transparent',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
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
