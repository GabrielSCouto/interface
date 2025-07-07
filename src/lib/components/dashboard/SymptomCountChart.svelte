<script>
    import { Bar } from 'svelte-chartjs';
	import { Chart, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

	Chart.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);
    
    export let data = [];
    let chartData = {};
    let chartOptions = {
        indexAxis: 'y',
        responsive: true,
    };

    $: {
        const counts = {};
        data.forEach(item => {
            const symptom = item.Symptom;
            counts[symptom] = (counts[symptom] || 0) + 1;
        });

        const labels = Object.keys(counts);
        const dataPoints = Object.values(counts);

        chartData = {
            labels,
            datasets: [{
                label: 'Symptom Count',
                data: dataPoints,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        };
    }
</script>

<h3 class="text-center font-semibold mb-2">Count by Symptom</h3>
{#if data.length > 0}
    <Bar data={chartData} options={chartOptions} />
{:else}
    <p class="text-center text-gray-500">No data to display for the current selection.</p>
{/if}