document.addEventListener("DOMContentLoaded", function () {

    const exportBtn = document.getElementById("exportPNG");
    if (!exportBtn) return;

    exportBtn.addEventListener("click", function () {
        const canvas = document.getElementById("categoryChart");
        const link = document.createElement("a");
        link.download = "revenue_by_category.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
    });

    const canvas = document.getElementById("categoryChart");
    const ctx = canvas.getContext("2d");
    const currencyCode = canvas.dataset.currency || "EUR";

    const labels = JSON.parse(document.getElementById("labels").textContent);
    const values = JSON.parse(document.getElementById("values").textContent);

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
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.formattedValue || '';
                            return `${label}: ${value} ${currencyCode}`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });
});
