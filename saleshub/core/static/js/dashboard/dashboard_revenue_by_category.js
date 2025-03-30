document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("chartCategory");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    const labels = JSON.parse(document.getElementById("category-labels").textContent);
    const values = JSON.parse(document.getElementById("category-values").textContent);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor:  ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
                hoverOffset: 10
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let value = context.formattedValue;
                            return `${context.label}: EUR${value}`;
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
