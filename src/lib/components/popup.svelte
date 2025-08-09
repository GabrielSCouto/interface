<script>
  import { createEventDispatcher } from 'svelte';
  import { fade, fly } from 'svelte/transition';

  const dispatch = createEventDispatcher();

  function fecharPopup() {
    dispatch('close');
  }

  // Permite fechar com a tecla Escape
</script>

<svelte:window on:keydown={(event) => event.key === 'Escape' && fecharPopup()} />

<div class="overlay" on:click={fecharPopup} transition:fade>
  <div class="popup" on:click|stopPropagation transition:fly={{ y: -50, duration: 300 }}>
    
    <slot></slot>

  </div>
</div>

<style>
  /* Estilo Dark Mode para o Popup */
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7); 
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .popup {
    background: #202020;
    color: #d1d5db;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    width: 90%;
    border: 1px solid #374151;
    
    /* ALTERADO: Aumentamos a largura máxima de 500px para 700px */
    max-width: 1080px; 
  }
</style>