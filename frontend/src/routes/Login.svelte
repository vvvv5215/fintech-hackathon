<script>
    import { supabase } from '../lib/supabase.js';
    import { onMount } from 'svelte';
    import googleLogo from '../assets/google.png';
  
    let user = null;
  
    async function signInWithGoogle() {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
      });
      if (error) alert(error.message);
    }
  
    async function signOut() {
      await supabase.auth.signOut();
      user = null;
    }
  
    onMount(async () => {
      const { data } = await supabase.auth.getUser();
      user = data.user;
      supabase.auth.onAuthStateChange((_event, session) => {
        user = session?.user ?? null;
      });
    });
  </script>
  
  {#if user}
    <p>Welcome, {user.email}!</p>
    <button on:click={signOut}>Sign out</button>
  {:else}
    <div class="login-center">
      <button on:click={signInWithGoogle}>
        <img src={googleLogo} alt="Google" class="google-logo" />
        Sign in with Google
      </button>
    </div>
  {/if}

<style>
.login-center {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2.5rem;
}
.google-logo {
  height: 1.2em;
  margin-right: 0.6em;
  vertical-align: middle;
}
</style>