document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("chartProduct");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    const labels = JSON.parse(document.getElementById("product-labels").textContent);
    const values = JSON.parse(document.getElementById("product-values").textContent);

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
                hoverOffset: 10
            }]
        },
        options: {
            plugins: {
                legend: { display: false },
                title: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let value = context.formattedValue;
                            return `${context.label}: €${value}`;
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
