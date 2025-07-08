<script>
	import { onMount } from 'svelte';
	import Papa from 'papaparse';
	import Filters from '$lib/components/dashboard/Filters.svelte';
	import SymptomCountChart from '$lib/components/dashboard/SymptomCountChart.svelte';
	import DiseaseByAreaChart from '$lib/components/dashboard/DiseaseByAreaChart.svelte';

	let allData = []; 
	let filteredData = []; 

	let selectedAreas = [];
	let selectedAgeRanges = [];

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

	// $: is a reactive block in Svelte. It runs whenever one of its dependencies changes.
	// Here, it will filter the data whenever the user interacts with the filters.
	$: {
		if (allData.length > 0) {
			filteredData = allData.filter((item) => {
				const areaFilter = selectedAreas.length === 0 || selectedAreas.includes(item.HealthArea);
				const ageFilter =
					selectedAgeRanges.length === 0 || selectedAgeRanges.includes(item.AgeRange);
				return areaFilter && ageFilter;
			});
		}
	}
</script>

<div
	class="h-screen w-full bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 p-4 flex flex-col gap-4"
>
	<header class="text-center">
		<h1 class="text-3xl font-bold font-primary">Medical Decision Support Dashboard</h1>
	</header>

	<main class="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-grow">
		<aside class="lg:col-span-1 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
			<div class="space-y-6">
				<div class="flex justify-center">
					<img src="/logo-nutes.png" alt="Logo NUTES CISAM" class="h-20" />
				</div>

				<Filters data={allData} bind:selectedAreas bind:selectedAgeRanges />
			</div>
		</aside>

		<section class="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
			<div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
				<SymptomCountChart data={filteredData} />
			</div>
			<div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
				<DiseaseByAreaChart data={filteredData} />
			</div>
		</section>
	</main>
</div>
