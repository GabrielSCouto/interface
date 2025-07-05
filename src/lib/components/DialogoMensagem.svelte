<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';

    export let show = false;
    export let date: Date | null = null;
    export let initialValue = '';

    let inputValue = '';
    let textareaElement: HTMLTextAreaElement;

    const dispatch = createEventDispatcher();

    // onMount será executado cada vez que o #key no pai for alterado.
    onMount(() => {
        inputValue = initialValue;
        setTimeout(() => textareaElement?.focus(), 50);
    });

    function handleSubmit() {
        dispatch('submit', inputValue);
    }

    function handleCancel() {
        dispatch('close');
    }

    function handleDelete() {
        // Define o valor como vazio e submete, o que apaga a anotação.
        inputValue = '';
        dispatch('submit', inputValue);
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
            handleSubmit();
        }
        if (event.key === 'Escape') {
            handleCancel();
        }
    }
</script>

{#if show && date}
    <div class="dialog-overlay" on:mousedown={handleCancel} on:keydown={handleKeydown}>
        <div class="dialog-box" on:mousedown|stopPropagation>
            <header class="dialog-header">
                <h3>Anotação para {date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long' })}</h3>
                <button on:click={handleCancel} class="close-button" aria-label="Fechar">&times;</button>
            </header>

            <div class="dialog-content">
                <textarea
                    bind:this={textareaElement}
                    bind:value={inputValue}
                    placeholder="Escreva sua anotação aqui..."
                    rows="4"
                />
            </div>

            <footer class="dialog-footer">
                <button on:click={handleCancel} class="button-secondary">Cancelar</button>
                
                <button on:click={handleDelete} class="button-danger">Excluir</button>
                
                <button on:click={handleSubmit} class="button-primary">Salvar</button>
            </footer>
        </div>
    </div>
{/if}

<style>
    .dialog-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(10, 10, 10, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        -webkit-backdrop-filter: blur(4px);
        backdrop-filter: blur(4px);
    }
    .dialog-box {
        background-color: #1f2937; /* Fundo: cinza-azulado escuro */
        color: #d1d5db;
        padding: 20px 24px;
        border-radius: 12px;
        width: 90%;
        max-width: 420px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
        animation: slide-up 0.3s ease-out;
    }
    @keyframes slide-up {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    .dialog-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #374151;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }
    .dialog-header h3 {
        margin: 0;
        font-size: 1.125rem;
        font-weight: 600;
        color: #f9fafb; /* Título branco */
    }
    .close-button {
        background: none;
        border: none;
        font-size: 1.75rem;
        color: #9ca3af;
        cursor: pointer;
        line-height: 1;
        transition: color 0.2s;
    }
    .close-button:hover {
        color: #f9fafb;
    }
    .dialog-content textarea {
        width: 100%;
        padding: 10px;
        border-radius: 6px;
        background-color: #374151;
        color: #f3f4f6;
        border: 1px solid #4b5563;
        font-family: inherit;
        font-size: 1rem;
        box-sizing: border-box;
        resize: vertical;
        transition:
            border-color 0.2s,
            box-shadow 0.2s;
    }
    .dialog-content textarea::placeholder {
        color: #9ca3af;
    }
    .dialog-content textarea:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.3);
        outline: none;
    }
    .dialog-footer {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 20px;
    }
    .dialog-footer button {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    .button-primary {
        background-color: #4f46e5;
        color: white;
    }
    .button-primary:hover {
        background-color: #6366f1;
    }
    .button-secondary {
        background-color: #4b5563;
        color: #f3f4f6;
    }
    .button-secondary:hover {
        background-color: #6b7280;
    }
    /* Estilo para o novo botão Excluir */
    .button-danger {
        background-color: #dc2626; /* Vermelho */
        color: white;
    }
    .button-danger:hover {
        background-color: #ef4444; /* Vermelho mais claro no hover */
    }
</style>