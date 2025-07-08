<script>
    import { Bar } from 'svelte-chartjs';
	import 'chart.js/auto'; 

    export let data = [];
    let chartData = {};
    let chartOptions = {
        responsive: true,
        scales: { 
            x: { stacked: true }, 
            y: { stacked: true } 
        }
    };

    const chartColors = ['#4BC0C0', '#FF6384', '#FF9F40', '#9966FF', '#FFCD56', '#36A2EB'];

    $: {

        const allDiseases = [...new Set(data.map(d => d.DiagnosedDisease))];
        
        const dataByArea = data.reduce((acc, curr) => {
            const area = curr.HealthArea;
            if (!acc[area]) acc[area] = [];
            acc[area].push(curr);
            return acc;
        }, {});

        const labels = Object.keys(dataByArea); 

        const datasets = allDiseases.map((disease, index) => {
            return {
                label: disease,
                data: labels.map(area => {
                    return dataByArea[area].filter(d => d.DiagnosedDisease === disease).length;
                }),
                backgroundColor: chartColors[index % chartColors.length],
            };
        });

        chartData = { labels, datasets };
    }
</script>

<h3 class="text-center font-semibold mb-2">Disease Distribution by Health Area</h3>
{#if data.length > 0}
    <Bar data={chartData} options={chartOptions} />
{:else}
    <p class="text-center text-gray-500">No data to display for the current selection.</p>
{/if}