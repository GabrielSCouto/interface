<script>
	import { onMount } from 'svelte';
	import Papa from 'papaparse';

	import Filters from '$lib/components/dashboard/Filters.svelte';
	import SymptomCountChart from '$lib/components/dashboard/SymptomCountChart.svelte';
	import DiseaseByAreaChart from '$lib/components/dashboard/DiseaseByAreaChart.svelte';
    import MonthlyTrendChart from '$lib/components/dashboard/MonthlyTrendChart.svelte';

    let allData = [];
	let filteredData = [];
	
    let selectedAreas = [];
	let selectedAgeRanges = [];
    let selectedMonths = [];
    let selectedYears = [];

	onMount(async () => {
		const response = await fetch('/medical_data.csv');
		const csvText = await response.text();
		
		Papa.parse(csvText, {
			header: true,
			skipEmptyLines: true,
			complete: (results) => {
				allData = results.data;
				filteredData = allData;
			}
		});
	});


	$: {
		if (allData.length > 0) {
			filteredData = allData.filter(item => {
				const areaFilter = selectedAreas.length === 0 || selectedAreas.includes(item.HealthArea);
				const ageFilter = selectedAgeRanges.length === 0 || selectedAgeRanges.includes(item.AgeRange);
                const monthFilter = selectedMonths.length === 0 || selectedMonths.includes(item.AppointmentMonth.trim());
                const yearFilter = selectedYears.length === 0 || selectedYears.includes(item.AppointmentYear);

                return areaFilter && ageFilter && monthFilter && yearFilter;
			});
		}
	}
</script>

<div class="h-full min-h-screen w-full bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 p-4 flex flex-col gap-4">
	
	<header class="text-center">
		<h1 class="text-3xl font-bold font-primary">Dashboard de Apoio à Decisão</h1>
	</header>
	
	<main class="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-grow">
		
		<aside class="lg:col-span-1 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
			<div class="space-y-6">
				<div class="flex justify-center">
                    <img src="/logo-nutes.png" alt="Logo NUTES CISAM" class="h-20" /> 
                    </div>
				<Filters 
					data={allData} 
					bind:selectedAreas
					bind:selectedAgeRanges
                    bind:selectedMonths
                    bind:selectedYears
				/>
			</div>
		</aside>

		<section class="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
			<div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
				<SymptomCountChart data={filteredData} />
			</div>
			<div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
				<DiseaseByAreaChart data={filteredData} />
			</div>

            <!-- <div class="md:col-span-2 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                <MonthlyTrendChart data={filteredData} />
            </div> -->
		</section>

	</main>
</div>