<script lang="ts">
	import { onMount } from 'svelte';
	// 1. Importe o novo componente de diálogo
	import DialogoMensagem from './DialogoMensagem.svelte';

	// --- ESTADO DO CALENDÁRIO ---
	let dataAtual = new Date();
	let diasComMensagem = new Map<string, string>();
	let dadosCarregados = false;

	// 2. Crie variáveis de estado para controlar o diálogo
	let showDialogo = false;
	let dataSelecionada: Date | null = null;
	let mensagemInicialParaDialogo = '';

	// --- FUNÇÕES ---
	function formatarData(data: Date): string {
		const ano = data.getFullYear();
		const mes = (data.getMonth() + 1).toString().padStart(2, '0');
		const dia = data.getDate().toString().padStart(2, '0');
		return `${ano}-${mes}-${dia}`;
	}

	// ... (outras funções do calendário como nomeMes, ano, etc. permanecem iguais) ...
	let nomeMes = '';
	let ano = 0;
	let diasDoGrid: (Date | null)[] = [];
	$: {
		const anoAtual = dataAtual.getFullYear();
		const mesAtual = dataAtual.getMonth();
		const nomesDosMeses = [
			'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
			'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
		];
		nomeMes = nomesDosMeses[mesAtual];
		ano = anoAtual;
		const primeiroDiaDoMes = new Date(anoAtual, mesAtual, 1);
		const diasNoMes = new Date(anoAtual, mesAtual + 1, 0).getDate();
		const diaDaSemanaDoPrimeiroDia = primeiroDiaDoMes.getDay();
		const novoGrid = [];
		for (let i = 0; i < diaDaSemanaDoPrimeiroDia; i++) {
			novoGrid.push(null);
		}
		for (let i = 1; i <= diasNoMes; i++) {
			novoGrid.push(new Date(anoAtual, mesAtual, i));
		}
		diasDoGrid = novoGrid;
	}
	function mesAnterior() { dataAtual = new Date(dataAtual.getFullYear(), dataAtual.getMonth() - 1, 1); }
	function proximoMes() { dataAtual = new Date(dataAtual.getFullYear(), dataAtual.getMonth() + 1, 1); }
	// --- FIM DAS FUNÇÕES INALTERADAS ---

	// 3. MODIFICADO: Esta função agora abre o diálogo em vez de chamar o prompt
	function handleDateClick(data: Date) {
		dataSelecionada = data;
		mensagemInicialParaDialogo = diasComMensagem.get(formatarData(data)) || '';
		showDialogo = true;
	}

	// 4. NOVO: Função para tratar o salvamento do diálogo
	function handleDialogoSubmit(event: CustomEvent<string>) {
		const novaMensagem = event.detail;
		if (dataSelecionada) {
			const dataString = formatarData(dataSelecionada);
			if (novaMensagem) {
				diasComMensagem.set(dataString, novaMensagem);
			} else {
				diasComMensagem.delete(dataString);
			}
			diasComMensagem = diasComMensagem; // Trigger reactivity
		}
		handleDialogoClose(); // Fecha o diálogo após salvar
	}

	// 5. NOVO: Função para fechar o diálogo
	function handleDialogoClose() {
		showDialogo = false;
		dataSelecionada = null;
		mensagemInicialParaDialogo = '';
	}

	// --- PERSISTÊNCIA DE DADOS (sem alterações) ---
	onMount(() => {
		const salvos = localStorage.getItem('meusDiasMarcados');
		if (salvos) {
			diasComMensagem = new Map(JSON.parse(salvos));
		}
		dadosCarregados = true;
	});

	$: {
		if (typeof window !== 'undefined' && dadosCarregados) {
			localStorage.setItem('meusDiasMarcados', JSON.stringify(Array.from(diasComMensagem.entries())));
		}
	}
</script>

<DialogoMensagem
	bind:show={showDialogo}
	date={dataSelecionada}
	initialValue={mensagemInicialParaDialogo}
	on:submit={handleDialogoSubmit}
	on:close={handleDialogoClose}
/>

<div class="calendario-container">
	<header class="calendario-header">
		<button on:click={mesAnterior} class="nav-button">&lt;</button>
		<h2>{nomeMes} de {ano}</h2>
		<button on:click={proximoMes} class="nav-button">&gt;</button>
	</header>
	<div class="dias-semana">
		<span>Dom</span><span>Seg</span><span>Ter</span><span>Qua</span><span>Qui</span><span>Sex</span><span>Sáb</span>
	</div>
	<div class="grid-dias">
		{#each diasDoGrid as dia}
			{#if dia}
				<button
					class="dia"
					class:marcado={diasComMensagem.has(formatarData(dia))}
					on:click={() => handleDateClick(dia)}
					title={diasComMensagem.get(formatarData(dia))}
				>
					{dia.getDate()}
				</button>
			{:else}
				<div class="dia-vazio" />
			{/if}
		{/each}
	</div>
</div>

<style>
	.calendario-container { width: 100%; max-width: 800px; margin: 2rem auto; padding: 1rem; border: 1px solid #ddd; border-radius: 8px; font-family: sans-serif; background-color: white; color: black; }
    .calendario-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .calendario-header h2 { font-size: 1.1rem; font-weight: 600; }
    .nav-button { font-size: 1.5rem; font-weight: bold; background: none; border: none; cursor: pointer; padding: 0 0.5rem; }
    .dias-semana, .grid-dias { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; }
    .dias-semana span { font-weight: 500; font-size: 0.8rem; color: #666; }
    .grid-dias { margin-top: 0.5rem; gap: 4px; }
    .dia { display: flex; justify-content: center; align-items: center; width: 100%; aspect-ratio: 1 / 1; border-radius: 50%; border: none; background-color: transparent; cursor: pointer; transition: background-color 0.2s; }
    .dia:hover { background-color: #f0f0f0; }
    .dia.marcado { background-color: #ff7c7c; color: #333; font-weight: bold; }
    .dia-vazio {}
</style>