const ctx = document.getElementById('rankingChart').getContext('2d');
const topNSelect = document.getElementById('topN');

// Asegurar fuentes e interfaz legible
Chart.defaults.color = '#cbd5e1';
Chart.defaults.font.family = "'Inter', sans-serif";

let rankingChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Frecuencia',
            data: [],
            backgroundColor: (context) => {
                const chart = context.chart;
                const {ctx, chartArea} = chart;
                if (!chartArea) return null;
                const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                gradient.addColorStop(0, 'rgba(59, 130, 246, 0.8)'); // Blue
                gradient.addColorStop(1, 'rgba(192, 132, 252, 0.9)'); // Purple
                return gradient;
            },
            borderColor: 'rgba(192, 132, 252, 1)',
            borderWidth: 0,
            borderRadius: 8,
            hoverBackgroundColor: '#60a5fa', // Lighter hover
            barThickness: 'flex',
            maxBarThickness: 50
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
            easing: 'easeOutQuart'
        },
        plugins: {
            legend: { 
                display: false 
            },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                titleFont: { size: 14, family: "'Inter', sans-serif" },
                bodyFont: { size: 15, family: "'Inter', sans-serif", weight: 'bold' },
                padding: 15,
                cornerRadius: 10,
                displayColors: false,
                callbacks: {
                    label: function(context) {
                        return `Utilizaciones: ${context.parsed.y}`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)',
                    drawBorder: false
                },
                ticks: { 
                    font: { size: 12 },
                    padding: 10
                }
            },
            x: {
                grid: { 
                    display: false, 
                    drawBorder: false 
                },
                ticks: {
                    font: { size: 13, weight: '500' },
                    maxRotation: 45,
                    minRotation: 45,
                    padding: 10
                }
            }
        }
    }
});

let isFetching = false;

async function fetchRanking() {
    if (isFetching) return;
    isFetching = true;

    try {
        const topN = topNSelect.value;
        const response = await fetch(`/api/ranking?top=${topN}`);
        if (!response.ok) throw new Error("Fallo en red al obtener el ranking");
        
        const data = await response.json();
        
        const labels = data.ranking.map(item => item.word);
        const values = data.ranking.map(item => item.score);
        
        rankingChart.data.labels = labels;
        rankingChart.data.datasets[0].data = values;
        rankingChart.update();
    } catch (e) {
        console.error('Error fetching ranking:', e);
    } finally {
        isFetching = false;
    }
}

// Carga inicial y polling
fetchRanking();
setInterval(fetchRanking, 3000);

// Detectar cambios en el menú desplegable
topNSelect.addEventListener('change', fetchRanking);
