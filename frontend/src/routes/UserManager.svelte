<script>
  import { supabase } from '../lib/supabase.js';
  import { onMount } from 'svelte';
  import { fetchUsers, deleteExpensesByUser } from '../lib/api.js';

  let users = [];
  let error = '';
  let user = null;
  let roleChangeMessage = '';
  let secretCode = '';
  let becomeHandlerMessage = '';

  onMount(async () => {
    const { data } = await supabase.auth.getUser();
    user = data.user;
    await loadUsers();
    supabase.auth.onAuthStateChange((_event, session) => {
      user = session?.user ?? null;
      loadUsers();
    });
  });

  async function loadUsers() {
    try {
      users = await fetchUsers();
    } catch (e) {
      error = 'Failed to fetch users';
    }
  }

  async function logout() {
    await supabase.auth.signOut();
    location.reload();
  }

  function amIEventHandler() {
    const me = users.find(u => u.email === user?.email);
    return me && me.role === 'handler';
  }

  async function removeMyself() {
    const me = users.find(u => u.email === user?.email);
    if (me) {
      await deleteExpensesByUser(user.email);
      await loadUsers();
      await logout();
    }
  }

  async function handleRemoveUser(email) {
    await deleteExpensesByUser(email);
    await loadUsers();
  }

  async function handleRoleChange(email, name, newRole) {
    roleChangeMessage = '';
    try {
      // Add a zero-cost expense to record the role change
      await fetch('/api/role_change', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: email, name, role: newRole })
      });
      await loadUsers();
      roleChangeMessage = `Role updated for ${email}`;
    } catch (e) {
      roleChangeMessage = `Failed to update role for ${email}`;
    }
  }

  function hasHandler() {
    return users.some(u => u.role === 'handler');
  }

  async function handleBecomeHandler() {
    becomeHandlerMessage = '';
    try {
      const res = await fetch('http://localhost:8000/become_handler', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: user.email, name: user.user_metadata?.name || user.email, secret_code: secretCode })
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed');
      }
      becomeHandlerMessage = 'You are now an event handler!';
      secretCode = '';
      await loadUsers();
    } catch (e) {
      becomeHandlerMessage = e.message;
    }
  }
</script>

<style>
  :global(body) {
    background: #000000;
    color: #f5f5f5;
    font-family: 'Segoe UI', Arial, sans-serif;
    margin: 0;
    min-height: 100vh;
  }
  .logout-bar-global {
    position: fixed;
    top: 1.5em;
    right: 2em;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 1em;
    background: rgba(24,24,24,0.95);
    padding: 0.7em 1.2em;
    border-radius: 10px;
    box-shadow: 0 2px 8px #0006;
  }
  .logout-btn {
    background: #ff6b6b;
    color: #fff;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.5em 1.2em;
    cursor: pointer;
    transition: background 0.2s;
  }
  .logout-btn:hover {
    background: #ff3b3b;
  }
  main {
    max-width: 500px;
    margin: 2em auto;
    background: #181818;
    border-radius: 16px;
    box-shadow: 0 4px 24px #000a;
    padding: 2em 2.5em 2.5em 2.5em;
    position: relative;
  }
  h2 {
    margin-top: 0;
    color: #fff;
    letter-spacing: 1px;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 1em;
    margin-bottom: 1.5em;
  }
  input, select, button {
    padding: 0.7em 1em;
    border-radius: 8px;
    border: none;
    font-size: 1em;
    background: #222;
    color: #f5f5f5;
  }
  input, select {
    border: 1px solid #333;
  }
  button {
    background: #646cff;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }
  button:hover {
    background: #535bf2;
  }
  .user-email {
    color: #aaa;
    font-size: 0.98em;
    margin-bottom: 1em;
  }
  ul {
    list-style: none;
    padding: 0;
  }
  li {
    background: #222;
    margin-bottom: 1em;
    padding: 1em;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    box-shadow: 0 2px 8px #0004;
  }
  .user-role {
    font-size: 0.95em;
    color: #8ec6ff;
    margin-bottom: 0.2em;
  }
  .user-email-list {
    font-size: 0.92em;
    color: #aaa;
    margin-bottom: 0.5em;
  }
  .error {
    color: #ff6b6b;
    margin-bottom: 1em;
  }
</style>

{#if user?.email}
  <div class="logout-bar-global">
    <span class="user-email">Signed in as <strong>{user.email}</strong></span>
    <button class="logout-btn" on:click={logout}>Log out</button>
    {#if amIEventHandler()}
      <button class="logout-btn" style="background:#ffb347; color:#222; margin-left:1em;" on:click={removeMyself}>Remove Myself</button>
    {/if}
  </div>
{/if}
{#if roleChangeMessage}
  <div class="error">{roleChangeMessage}</div>
{/if}
{#if user?.email && !hasHandler()}
  <form on:submit|preventDefault={handleBecomeHandler} style="margin:2em auto;max-width:400px;background:#181818;padding:1.5em 2em;border-radius:12px;box-shadow:0 2px 12px #0006;display:flex;flex-direction:column;gap:1em;align-items:center;">
    <label for="handler-secret" style="color:#fff;">Enter secret code to become the first Event Handler:</label>
    <input id="handler-secret" type="password" bind:value={secretCode} placeholder="Secret code" required style="width:100%;" />
    <button type="submit">Become Event Handler</button>
    {#if becomeHandlerMessage}
      <div class="error">{becomeHandlerMessage}</div>
    {/if}
  </form>
{/if}
<main>
  <h2>Users</h2>
  {#if users.length === 0}
    <p>No users yet.</p>
  {:else}
    <ul>
      {#each users as u}
        <li>
          <span class="user-role">{u.role === 'handler' ? 'Event Handler' : 'User'}</span>
          <strong>{u.name}</strong>
          <span class="user-email-list">{u.email}</span>
          {#if amIEventHandler() && u.email !== user.email}
            <select on:change={(e) => { const value = e.target && (e.target instanceof HTMLSelectElement ? e.target.value : undefined); handleRoleChange(u.email, u.name, value); }} bind:value={u.role} style="margin-top:0.5em;">
              <option value="user">User</option>
              <option value="handler">Event Handler</option>
            </select>
          {/if}
          {#if amIEventHandler() && u.role !== 'handler'}
            <button on:click={() => handleRemoveUser(u.email)} style="margin-top: 0.5em;">Remove</button>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</main> 