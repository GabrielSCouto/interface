<script>
	import { onMount } from 'svelte';
	import Papa from 'papaparse';

	// Componentes do Filtro e Gráficos
	import Filters from '$lib/components/dashboard/Filters.svelte';
	import MonthlyTrendChart from '$lib/components/dashboard/MonthlyTrendChart.svelte';
	import SymptomCountChart from '$lib/components/dashboard/SymptomCountChart.svelte';

	// Novos componentes para a visão GERAL
	import KPIs from '$lib/components/dashboard/KPIs.svelte';
	import AreaDistributionChart from '$lib/components/dashboard/AreaDistributionChart.svelte';
	import AgeDistributionChart from '$lib/components/dashboard/AgeDistributionChart.svelte';
	import TopComplaintsChart from '$lib/components/dashboard/TopComplaintsChart.svelte';

	import HisteroscopiaKPIs from '$lib/components/dashboard/HisteroscopiaKPIs.svelte';
	import ComorbidityChart from '$lib/components/dashboard/ComorbidityChart.svelte';
	import ObstetricProfileChart from '$lib/components/dashboard/ObstetricProfileChart.svelte';
	import MedicationChart from '$lib/components/dashboard/MedicationChart.svelte';

	// Variáveis de estado
	let allData = [];
	let filteredData = [];

	let allConditionsData = [];

	let selectedAreas = [];
	let selectedAgeRanges = [];
	let selectedMonths = [];
	let selectedYears = [];

	// Variáveis para os KPIs
	let totalAppointments = 0;
	let avgAge = 0;
	let busiestArea = '-';
	let peakMonth = '-';

	// KPIs da Visão Geral
	let generalKPIs = [];

	// KPIs da Visão de Histeroscopia
	let operationalKPIs = [];
	let clinicalKPIs = [];

	onMount(async () => {
		const response = await fetch('/medical_data.csv');
		const csvText = await response.text();

		Papa.parse(csvText, {
			header: true,
			skipEmptyLines: true,
			delimiter: ';',
			complete: (results) => {
				// Filtra linhas vazias ou malformadas que o Papa.parse pode criar
				allData = results.data.filter((item) => item.PatientID);
				filteredData = allData;
			}
		});
		Papa.parse('/hd-condicoes.csv', {
			header: true,
			skipEmptyLines: true,
			delimiter: ';',
			complete: (results) => {
				allConditionsData = results.data.filter((item) => item.ID);
			}
		});
	});

	// Bloco reativo para a filtragem principal
	// $: {
	// 	if (allData.length > 0) {
	// 		filteredData = allData.filter((item) => {
	// 			const areaFilter = selectedAreas.length === 0 || selectedAreas.includes(item.HealthArea);
	// 			const ageFilter =
	// 				selectedAgeRanges.length === 0 || selectedAgeRanges.includes(item.AgeRange);
	// 			const monthFilter =
	// 				selectedMonths.length === 0 || selectedMonths.includes(item.AppointmentMonth?.trim());
	// 			const yearFilter =
	// 				selectedYears.length === 0 || selectedYears.includes(item.AppointmentYear);
	// 			return areaFilter && ageFilter && monthFilter && yearFilter;
	// 		});
	// 	}
	// }

	// Bloco reativo para calcular os KPIs
	$: {
		if (filteredData.length > 0) {
			totalAppointments = filteredData.length;

			// Média de Idade
			const totalAge = filteredData.reduce((sum, item) => sum + Number(item.Age), 0);
			avgAge = totalAge / totalAppointments;

			// Área Mais Ativa
			const areaCounts = filteredData.reduce((acc, item) => {
				acc[item.HealthArea] = (acc[item.HealthArea] || 0) + 1;
				return acc;
			}, {});
			busiestArea = Object.keys(areaCounts).reduce(
				(a, b) => (areaCounts[a] > areaCounts[b] ? a : b),
				'-'
			);

			// Mês de Pico
			const monthCounts = filteredData.reduce((acc, item) => {
				const month = item.AppointmentMonth?.trim();
				if (month) acc[month] = (acc[month] || 0) + 1;
				return acc;
			}, {});
			peakMonth = Object.keys(monthCounts).reduce(
				(a, b) => (monthCounts[a] > monthCounts[b] ? a : b),
				'-'
			);
		} else {
			// Reseta os KPIs se não houver dados
			totalAppointments = 0;
			avgAge = 0;
			busiestArea = '-';
			peakMonth = '-';
		}
	}

	// 	// Calcula KPIs para a visão de Histeroscopia
	// 	if (selectedAreas.length === 1 && selectedAreas[0] === 'Histeroscopia Diagnóstica') {
	// 		const symptomCounts = filteredData.reduce((acc, item) => {
	// 			acc[item.Symptom] = (acc[item.Symptom] || 0) + 1;
	// 			return acc;
	// 		}, {});
	// 		operationalKPIs = [
	// 			{
	// 				label: 'Total de Procedimentos',
	// 				value: filteredData.length,
	// 				color: 'text-blue-400'
	// 			},
	// 			{
	// 				label: 'Principal Indicação',
	// 				value: Object.keys(symptomCounts).reduce(
	// 					(a, b) => (symptomCounts[a] > symptomCounts[b] ? a : b),
	// 					'-'
	// 				),
	// 				color: 'text-yellow-400'
	// 			}
	// 		];

	// 		if (allConditionsData.length > 0) {
	// 			const polypCount = allConditionsData.filter(
	// 				(item) => item.Polipo?.toLowerCase() === 'sim'
	// 			).length;
	// 			const miomaCount = allConditionsData.filter(
	// 				(item) => item.Mioma?.toLowerCase() === 'sim'
	// 			).length;
	// 			clinicalKPIs = [
	// 				{
	// 					label: 'Pacientes na Amostra Clínica',
	// 					value: allConditionsData.length,
	// 					color: 'text-green-400'
	// 				},
	// 				{
	// 					label: 'Taxa de Pólipos',
	// 					value: `${((polypCount / allConditionsData.length) * 100).toFixed(1)}%`,
	// 					color: 'text-purple-400'
	// 				},
	// 				{
	// 					label: 'Taxa de Miomas',
	// 					value: `${((miomaCount / allConditionsData.length) * 100).toFixed(1)}%`,
	// 					color: 'text-red-400'
	// 				}
	// 			];
	// 		}
	// 	}
	// }

	// --- Lógica de Filtragem e Cálculo de KPIs ---
	$: {
		// Filtra o CSV principal com base nos seletores
		if (allData.length > 0) {
			filteredData = allData.filter((item) => {
				const areaFilter = selectedAreas.length === 0 || selectedAreas.includes(item.HealthArea);
				const ageFilter =
					selectedAgeRanges.length === 0 || selectedAgeRanges.includes(item.AgeRange);
				const monthFilter =
					selectedMonths.length === 0 || selectedMonths.includes(item.AppointmentMonth?.trim());
				const yearFilter =
					selectedYears.length === 0 || selectedYears.includes(item.AppointmentYear);
				return areaFilter && ageFilter && monthFilter && yearFilter;
			});
		}

		// Calcula KPIs para a visão geral
		if (selectedAreas.length === 0 && filteredData.length > 0) {
			const totalAge = filteredData.reduce((sum, item) => sum + Number(item.Age), 0);
			const areaCounts = filteredData.reduce((acc, item) => {
				acc[item.HealthArea] = (acc[item.HealthArea] || 0) + 1;
				return acc;
			}, {});
			const monthCounts = filteredData.reduce((acc, item) => {
				const m = item.AppointmentMonth?.trim();
				if (m) acc[m] = (acc[m] || 0) + 1;
				return acc;
			}, {});

			generalKPIs = [
				{
					label: 'Total de Atendimentos',
					value: filteredData.length,
					color: 'text-blue-400'
				},
				{
					label: 'Média de Idade',
					value: `${(totalAge / filteredData.length).toFixed(1)} anos`,
					color: 'text-green-400'
				},
				{
					label: 'Área Mais Ativa',
					value: Object.keys(areaCounts).reduce(
						(a, b) => (areaCounts[a] > areaCounts[b] ? a : b),
						'-'
					),
					color: 'text-purple-400'
				},
				{
					label: 'Mês de Pico',
					value: Object.keys(monthCounts).reduce(
						(a, b) => (monthCounts[a] > monthCounts[b] ? a : b),
						'-'
					),
					color: 'text-yellow-400'
				}
			];
		}

		// Calcula KPIs para a visão de Histeroscopia
		if (selectedAreas.length === 1 && selectedAreas[0] === 'Histeroscopia Diagnóstica') {
			const symptomCounts = filteredData.reduce((acc, item) => {
				acc[item.Symptom] = (acc[item.Symptom] || 0) + 1;
				return acc;
			}, {});
			operationalKPIs = [
				{
					label: 'Total de Procedimentos',
					value: filteredData.length,
					color: 'text-blue-400'
				},
				// {
				// 	label: 'Média de Idade',
				// 	value: `${(totalAge / filteredData.length).toFixed(1)} anos`,
				// 	color: 'text-green-400'
				// },
				{
					label: 'Principal Indicação',
					value: Object.keys(symptomCounts).reduce(
						(a, b) => (symptomCounts[a] > symptomCounts[b] ? a : b),
						'-'
					),
					color: 'text-yellow-400'
				}
			];

			if (allConditionsData.length > 0) {
				const polypCount = allConditionsData.filter(
					(item) => item.Polipo?.toLowerCase() === 'sim'
				).length;
				const miomaCount = allConditionsData.filter(
					(item) => item.Mioma?.toLowerCase() === 'sim'
				).length;
				clinicalKPIs = [
					{
						label: 'Pacientes na Amostra Clínica',
						value: allConditionsData.length,
						color: 'text-green-400'
					},
					{
						label: 'Taxa de Pólipos',
						value: `${((polypCount / allConditionsData.length) * 100).toFixed(1)}%`,
						color: 'text-purple-400'
					},
					{
						label: 'Taxa de Miomas',
						value: `${((miomaCount / allConditionsData.length) * 100).toFixed(1)}%`,
						color: 'text-red-400'
					}
				];
			}
		}
	}
</script>

<div class="min-h-screen w-full bg-[#0f0f1a] text-gray-200 p-4 md:p-6 lg:p-8 flex flex-col gap-6">
	<header class="text-center">
		<h1 class="text-3xl font-bold font-primary text-white">Dashboard de Apoio à Decisão Médica</h1>
	</header>

	<main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow">
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

		<section class="lg:col-span-3 flex flex-col gap-6">
			{#if selectedAreas.length === 0}
				<KPIs {totalAppointments} {avgAge} {busiestArea} {peakMonth} />
				<!-- <KPIs kpis={generalKPIs} /> -->

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<AreaDistributionChart data={filteredData} />
					<AgeDistributionChart data={filteredData} />
				</div>

				<MonthlyTrendChart data={filteredData} />
				<!-- <TopComplaintsChart data={filteredData} /> -->
				{:else if selectedAreas.length === 1 && selectedAreas[0] === 'Histeroscopia Diagnóstica'}
				<div>
					<h2 class="text-xl font-semibold text-gray-300 mb-4 border-b border-gray-700 pb-2">
						Visão Operacional (Atendimentos)
					</h2>
					<HisteroscopiaKPIs kpis={operationalKPIs} />
				</div>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<SymptomCountChart data={filteredData} />
					<AgeDistributionChart data={filteredData} />
				</div>
				<div>
					<MonthlyTrendChart data={filteredData} />
				</div>
				<!-- <hr class="border-gray-700 my-4" /> -->
				{:else if selectedAreas.length === 1 && selectedAreas[0] === 'Planejamento Reprodutivo'}
				<!-- <div>
					<h2 class="text-xl font-semibold text-gray-300 mb-4 border-b border-gray-700 pb-2">
						Visão Operacional (Atendimentos)
					</h2>
					<HisteroscopiaKPIs kpis={operationalKPIs} />
				</div> -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<SymptomCountChart data={filteredData} />
					<AgeDistributionChart data={filteredData} />
				</div>
				<div>
					<MonthlyTrendChart data={filteredData} />
				</div>
				<!-- <div>
					<h2 class="text-xl font-semibold text-gray-300 mb-4 border-b border-gray-700 pb-2">
						Visão Clínica (Amostra de Pacientes)
					</h2>
					<HisteroscopiaKPIs kpis={clinicalKPIs} />
				</div>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<ComorbidityChart data={allConditionsData} />
					<ObstetricProfileChart data={allConditionsData} />
					<div class="md:col-span-2">
						<MedicationChart data={allConditionsData} />
					</div>
				</div> -->

			<!-- {:else}
				<div
					class="bg-[#1e1e2f] p-8 rounded-xl shadow-lg text-center h-full flex flex-col justify-center"
				>
					<h2 class="text-2xl font-bold text-white mb-2">
						Dashboard para: {selectedAreas.join(', ')}
					</h2>
					<p class="text-gray-400">
						(Aqui serão exibidos os gráficos específicos para a(s) área(s) selecionada(s))
					</p>
				</div> -->
			{/if}

			<!-- {#if selectedAreas.length === 1 && selectedAreas[0] === 'Histeroscopia Diagnóstica'}
				<div>
					<h2 class="text-xl font-semibold text-gray-300 mb-4 border-b border-gray-700 pb-2">
						Visão Operacional (Atendimentos)
					</h2>
					<HisteroscopiaKPIs kpis={operationalKPIs} />
				</div>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<SymptomCountChart data={filteredData} />
					<AgeDistributionChart data={filteredData} />
				</div>

				<hr class="border-gray-700 my-4" />

				<div>
					<h2 class="text-xl font-semibold text-gray-300 mb-4 border-b border-gray-700 pb-2">
						Visão Clínica (Amostra de Pacientes)
					</h2>
					<HisteroscopiaKPIs kpis={clinicalKPIs} />
				</div>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<ComorbidityChart data={allConditionsData} />
					<ObstetricProfileChart data={allConditionsData} />
					<div class="md:col-span-2">
						<MedicationChart data={allConditionsData} />
					</div>
				</div>
			{:else}
				<KPIs kpis={generalKPIs} />
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<AreaDistributionChart data={filteredData} />
					<AgeDistributionChart data={filteredData} />
				</div>
				<MonthlyTrendChart data={filteredData} />
				<TopComplaintsChart data={filteredData} />
			{/if} -->
		</section>
	</main>
</div>
