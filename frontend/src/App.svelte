<script>
  import Login from './routes/Login.svelte';
  import UserManager from './routes/UserManager.svelte';
  import { supabase } from './lib/supabase.js';
  import { onMount } from 'svelte';
  import EventExpenses from './routes/EventExpenses.svelte';
  let user = null;

  onMount(async () => {
    const { data } = await supabase.auth.getUser();
    user = data.user;
    supabase.auth.onAuthStateChange((_event, session) => {
      user = session?.user ?? null;
    });
  });
</script>

<main class="center-main">
  <div class="center-content">
    <h1 class="title">Event Budget Tracker</h1>
    {#if user}
      <UserManager />
      <EventExpenses />
    {:else}
      <Login />
    {/if}
  </div>
</main>

<style>
.center-main {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
}
.center-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>