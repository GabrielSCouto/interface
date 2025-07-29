<script>
    export let data = [];
    export let selectedAreas = [];
    export let selectedAgeRanges = [];
    export let selectedMonths = []; 
    export let selectedYears = [];  

    let uniqueAreas = [];
    let uniqueAgeRanges = [];
    let uniqueMonths = []; 
    let uniqueYears = [];  


    const orderedMonths = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];

    $: {
        if(data.length > 0) {
            uniqueAreas = [...new Set(data.map(item => item.HealthArea))];
            uniqueAgeRanges = [...new Set(data.map(item => item.AgeRange))].sort();
            uniqueYears = [...new Set(data.map(item => item.AppointmentYear))].sort();


            const monthsInData = new Set(data.map(item => item.AppointmentMonth));
            uniqueMonths = orderedMonths.filter(month => monthsInData.has(month));
        }
    }
</script>

<div>
    <h3 class="text-lg font-semibold mb-2">Área Médica</h3>
    <div class="space-y-1">
        {#each uniqueAreas as area}
            <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" bind:group={selectedAreas} value={area} />
                <span>{area}</span>
            </label>
        {/each}
    </div>
</div>

<div class="mt-4">
    <h3 class="text-lg font-semibold mb-2">Faixa Etária</h3>
    <div class="space-y-1">
        {#each uniqueAgeRanges as range}
            <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" bind:group={selectedAgeRanges} value={range} />
                <span>{range}</span>
            </label>
        {/each}
    </div>
</div>

<div class="mt-4">
    <h3 class="text-lg font-semibold mb-2">Ano</h3>
    <div class="space-y-1">
        {#each uniqueYears as year}
            <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" bind:group={selectedYears} value={year} />
                <span>{year}</span>
            </label>
        {/each}
    </div>
</div>

<div class="mt-4">
    <h3 class="text-lg font-semibold mb-2">Mês</h3>
    <div class="max-h-48 overflow-y-auto border dark:border-gray-600 p-2 rounded-md space-y-1">
        {#each uniqueMonths as month}
            <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" bind:group={selectedMonths} value={month} />
                <span>{month}</span>
            </label>
        {/each}
    </div>
</div>