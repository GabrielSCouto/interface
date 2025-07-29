<script lang="ts">
    import { toast } from 'svelte-sonner';
    import { marked } from 'marked';

    import { onMount, getContext, tick, createEventDispatcher } from 'svelte';
    import { blur, fade } from 'svelte/transition';

    const dispatch = createEventDispatcher();

    import { config, user, models as _models, temporaryChatEnabled } from '$lib/stores';
    import { sanitizeResponseContent, extractCurlyBraceWords } from '$lib/utils';
    import { WEBUI_BASE_URL } from '$lib/constants';

    import Suggestions from './Suggestions.svelte';
    import Tooltip from '$lib/components/common/Tooltip.svelte';
    import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
    import MessageInput from './MessageInput.svelte';
	import { list } from 'postcss';

    const i18n = getContext('i18n');

    export let transparentBackground = false;

    export let createMessagePair: Function;
    export let stopResponse: Function;

    export let autoScroll = false;

    export let atSelectedModel: Model | undefined;
    export let selectedModels: [''];

    export let history;

    export let prompt = '';
    export let suggestionPrompts = [];
    export let showSuggestionsPromptsFromModel =  false;
    export let files = [];

    export let selectedToolIds = [];
    export let selectedFilterIds = [];

    export let imageGenerationEnabled = false;
    export let codeInterpreterEnabled = false;
    export let webSearchEnabled = false;

    export let promptGeneratedByModel = '';
    

    export let toolServers = [];

    let models = [];

    const selectSuggestionPrompt = async (p) => {
        let text = p;

        if (p.includes('{{CLIPBOARD}}')) {
            const clipboardText = await navigator.clipboard.readText().catch((err) => {
                toast.error($i18n.t('Failed to read clipboard contents'));
                return '{{CLIPBOARD}}';
            });

            text = p.replaceAll('{{CLIPBOARD}}', clipboardText);

            console.log('Clipboard text:', clipboardText, text);
        }

        prompt = text;

        console.log(prompt);
        await tick();

        const chatInputContainerElement = document.getElementById('chat-input-container');
        const chatInputElement = document.getElementById('chat-input');

        if (chatInputContainerElement) {
            chatInputContainerElement.scrollTop = chatInputContainerElement.scrollHeight;
        }

        await tick();
        if (chatInputElement) {
            chatInputElement.focus();
            chatInputElement.dispatchEvent(new Event('input'));
        }

        await tick();
    };

    let selectedModelIdx = 0;

    let tituloVisivel = true; // Controla a visibilidade do título

    onMount(() => {
        // Define um cronômetro para esconder o título após 1.5 segundos
        const timer = setTimeout(() => {
            tituloVisivel = false;
        }, 1500); // Ajuste este tempo como quiser

        // Limpa o cronômetro se o componente for destruído antes
        return () => clearTimeout(timer);
    });
    // FIM DA MODIFICAÇÃO

    $: if (selectedModels.length > 0) {
        selectedModelIdx = models.length - 1;
    }

    $: models = selectedModels.map((id) => $_models.find((m) => m.id === id));

    let suggestionsListModel

    $: suggestionsListModel = promptGeneratedByModel.split('\n').filter(line => line.trim() !== '');

    const staticSuggestionsPrompts = [
        {
            title: ['Saúde do Coração', 'Cardiologia'],
            content: 'Quais são os principais fatores de risco para doenças cardíacas e como posso manter meu coração saudável? Quais são os sinais de alerta que indicam problemas cardíacos?'
        },
        {
            title: ['Ouvido, Nariz e Garganta', 'Otorrinolaringologia'],
            content: 'Quando devo procurar um otorrinolaringologista? Quais são os sintomas mais comuns de problemas nessas áreas e como posso cuidar da higiene diária para evitar infecções?'
        },
        {
            title: ['Cuidados com a Pele', 'Dermatologia'],
            content: 'Quais são os cuidados essenciais com a pele para prevenir doenças e o envelhecimento precoce, especialmente considerando o clima de Recife? Como identificar sinais de alerta de câncer de pele?'
        },
        {
            title: ['Ossos e Articulações', 'Ortopedia'],
            content: 'Quais são as melhores práticas para manter a saúde dos ossos e articulações, principalmente para quem pratica atividades físicas? Quando é necessário procurar um ortopedista para dores?'
        },
        {
            title: ['Saúde Ocular', 'Oftalmologia'],
            content: 'Quais são os principais sinais de alerta para problemas de visão e com que frequência devo fazer exames de vista? Como posso proteger meus olhos da exposição excessiva a telas?'
        },
        {
            title: ['Saúde Feminina e Masculina', 'Ginecologia e Urologia'],
            content: 'Quais são os exames preventivos de rotina mais importantes para a saúde feminina e masculina, e qual a periodicidade recomendada? Quais sinais de alerta exigem atenção médica imediata?'
        }
    ];

</script>

<div class="m-auto w-full max-w-6xl px-2 @2xl:px-20 translate-y-6 py-24 text-center">
    {#if $temporaryChatEnabled}
        <Tooltip
            content={$i18n.t('This chat won’t appear in history and your messages will not be saved.')}
            className="w-full flex justify-center mb-0.5"
            placement="top"
        >
            <div class="flex items-center gap-2 text-gray-500 font-medium text-lg my-2 w-fit">
                <EyeSlash strokeWidth="2.5" className="size-5" />{$i18n.t('Temporary Chat')}
            </div>
        </Tooltip>
    {/if}

    <div
        class="w-full text-3xl text-gray-800 dark:text-gray-100 text-center flex items-center gap-4 font-primary"
    >
        <div class="w-full flex flex-col justify-center items-center">
            
            <div class="flex flex-row justify-center gap-3 @sm:gap-3.5 w-fit px-5">
                {#if tituloVisivel}
                    <div
                        class="text-3xl @sm:text-3xl line-clamp-1"
                        transition:fade={{ duration: 400 }}
                    >
				            Bem Vindo, {$user?.name ?? $user?.username ?? 'Usuário'}!
                    </div>
                {/if}
            </div>
            <div class="flex mt-1 mb-2">
                <div in:fade={{ duration: 100, delay: 50 }}>
                    {#if models[selectedModelIdx]?.info?.meta?.description ?? null}
                        <Tooltip
                            className=" w-fit"
                            content={marked.parse(
                                sanitizeResponseContent(models[selectedModelIdx]?.info?.meta?.description ?? '')
                            )}
                            placement="top"
                        >
                            <div
                                class="mt-0.5 px-2 text-sm font-normal text-gray-500 dark:text-gray-400 line-clamp-2 max-w-xl markdown"
                            >
                                {@html marked.parse(
                                    sanitizeResponseContent(models[selectedModelIdx]?.info?.meta?.description)
                                )}
                            </div>
                        </Tooltip>

                        {#if models[selectedModelIdx]?.info?.meta?.user}
                            <div class="mt-0.5 text-sm font-normal text-gray-400 dark:text-gray-500">
                                By
                                {#if models[selectedModelIdx]?.info?.meta?.user.community}
                                    <a
                                        href="https://openwebui.com/m/{models[selectedModelIdx]?.info?.meta?.user
                                            .username}"
                                        >{models[selectedModelIdx]?.info?.meta?.user.name
                                            ? models[selectedModelIdx]?.info?.meta?.user.name
                                            : `@${models[selectedModelIdx]?.info?.meta?.user.username}`}</a
                                    >
                                {:else}
                                    {models[selectedModelIdx]?.info?.meta?.user.name}
                                {/if}
                            </div>
                        {/if}
                    {/if}
                </div>
            </div>

            <div class="text-base font-normal @md:max-w-3xl w-full py-3 {atSelectedModel ? 'mt-2' : ''}">
                <MessageInput
                    {history}
                    {selectedModels}
                    bind:files
                    bind:prompt
                    bind:promptGeneratedByModel
                    bind:showSuggestionsPromptsFromModel
                    bind:autoScroll
                    bind:selectedToolIds
                    bind:selectedFilterIds
                    bind:imageGenerationEnabled
                    bind:webSearchEnabled
                    bind:atSelectedModel
                    {toolServers}
                    {transparentBackground}
                    {stopResponse}
                    {createMessagePair}
                    placeholder={$i18n.t('Como posso ajudar?')}
                    onChange={(input) => {
                        if (input.prompt !== null) {
                            localStorage.setItem(`chat-input`, JSON.stringify(input));
                        } else {
                            localStorage.removeItem(`chat-input`);
                        }
                    }}
                    on:upload={(e) => {
                        dispatch('upload', e.detail);
                    }}
                    on:submit={(e) => {
                        dispatch('submit', e.detail);
                    }}
                />
            </div>
        </div>
    </div>
    
    <div class="mx-auto max-w-2xl font-primary mt-2" in:fade={{ duration: 200, delay: 200 }}>
        <div class="mx-5">    
            {#if suggestionsListModel.length > 0 && showSuggestionsPromptsFromModel}
               
               <div class="relative w-full">
                        <button
                            on:click={() => (showSuggestionsPromptsFromModel = false)}
                            
                            class="absolute top-2 -right-2 z-10 p-1 rounded-full text-gray-500 hover:bg-red-500/20 hover:text-red-500 transition-colors"
                            aria-label="Fechar sugestões"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="h-4 w-4"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                stroke-width="2.5"
                            >
                                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>

                        <Suggestions
                            showSuggestionsPromptsFromModel={showSuggestionsPromptsFromModel}
                            suggestionsListModel={
                                [

                                    {
                                        id: 'p1',
                                        content: suggestionsListModel ? suggestionsListModel[0] : 'ocorreu um erro ao gerar o prompt'
                                    },
                                    {
                                        id: 'p2',
                                        content: suggestionsListModel ? suggestionsListModel[1] : 'ocorreu um erro ao gerar o prompt'
                                    },
                                    {
                                        id: 'p3',
                                        content: suggestionsListModel ? suggestionsListModel[2] : 'ocorreu um erro ao gerar o prompt'
                                    },
                                    {
                                        id: 'p4',
                                        content: suggestionsListModel ? suggestionsListModel[3] : 'ocorreu um erro ao gerar o prompt'
                                    }
                                ]

                            }
                                inputValue={prompt}
                                on:select={(e) => {
                                    selectSuggestionPrompt(e.detail);
                                }}    
                        />
                </div>

            {:else}
                <Suggestions
                        showSuggestionsPromptsFromModel={showSuggestionsPromptsFromModel}
                        suggestionPrompts={staticSuggestionsPrompts}
                            inputValue={prompt}
                            on:select={(e) => {
                                selectSuggestionPrompt(e.detail);
                            }}    
                />
            {/if}
                


        </div>
    </div>
</div>