<script>
    import { Bar } from 'svelte-chartjs';
    import 'chart.js/auto';

    export let data = [];
    let chartData = {};
    const ageOrder = ['18-','18-24', '25-34', '35-44', '45-54', '55-64', '65+','Sem dados'];

    let chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: { ticks: { color: '#ccc' }, grid: { color: '#444' } },
            y: { ticks: { color: '#ccc' }, grid: { color: '#444' } }
        }
    };

    $: {
        const counts = data.reduce((acc, item) => {
        const ageRange = item.AgeRange;

        // AQUI ESTÁ A CORREÇÃO:
        // A mesma verificação para garantir que a faixa etária existe antes de contar.
        if (ageRange) {
            acc[ageRange] = (acc[ageRange] || 0) + 1;
        }
        return acc;
    }, {});

    const sortedLabels = ageOrder.filter(range => counts[range]);
    const dataPoints = sortedLabels.map(range => counts[range]);

    chartData = {
        labels: sortedLabels,
        datasets: [{
            label: 'Contagem de Pacientes',
            data: dataPoints,
            backgroundColor: '#f28e2b',
            borderRadius: 4
        }]
    };
    }
</script>

<div class="bg-[#1e1e2f] p-4 rounded-xl shadow-lg h-full flex flex-col">
    <h3 class="text-center text-lg font-semibold mb-3 text-white">Distribuição por Faixa Etária</h3>
    <div class="relative flex-grow min-h-[250px]">
        <!-- {#if data.length > 0}
            <Bar {chartData} {chartOptions} />
        {:else}
            <p class="text-center text-gray-400 italic mt-10">Sem dados para exibir.</p>
        {/if} -->
        <Bar data={chartData} options={chartOptions} />
    </div>
</div>