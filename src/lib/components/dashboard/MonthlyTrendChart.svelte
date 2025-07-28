<script>
    import { Line } from 'svelte-chartjs';
	import { Chart, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js';

	Chart.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale);
    
    export let data = [];

    const monthsOfTheYear = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];

    let chartData = {};
    let chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
        },
        tension: 0.1 
    };

    $: {
        const monthlyCounts = {};
        monthsOfTheYear.forEach(month => {
            monthlyCounts[month] = 0;
        });

        data.forEach(item => {
            const month = item.AppointmentMonth.trim();
            if (monthlyCounts[month] !== undefined) {
                monthlyCounts[month]++;
            }
        });

        chartData = {
            labels: monthsOfTheYear,
            datasets: [{
                label: 'Number of Appointments per Month',
                data: Object.values(monthlyCounts), 
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
            }]
        };
    }
</script>

<h3 class="text-center font-semibold mb-2">Monthly Appointment Trends</h3>
{#if data.length > 0}
    <Line {chartData} {chartOptions} />
{:else}
    <p class="text-center text-gray-500">No data to display for the current selection.</p>
{/if}