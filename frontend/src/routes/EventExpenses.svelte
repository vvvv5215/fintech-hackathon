<script>
  import { fetchExpenses, addExpense, deleteExpense, fetchAllExpenses, updateReceiptUrl, fetchUsers } from '../lib/api.js';
  import { onMount } from 'svelte';
  import { supabase } from '../lib/supabase.js';

  let user = null;
  let eventName = '';
  let eventCost = '';
  let expenses = [];
  let expenseError = '';
  let showAll = false;
  let isEventHandler = false;
  let allExpenses = [];
  let users = [];

  function groupByUser(expenses) {
    const grouped = {};
    for (const exp of expenses) {
      if (!grouped[exp.user_email]) grouped[exp.user_email] = [];
      grouped[exp.user_email].push(exp);
    }
    return grouped;
  }

  $: grandTotal = showAll ? allExpenses.reduce((sum, e) => sum + e.cost, 0) : 0;

  onMount(async () => {
    const { data } = await supabase.auth.getUser();
    user = data.user;
    await loadUsers();
    if (user?.email) loadExpenses();
    supabase.auth.onAuthStateChange((_event, session) => {
      user = session?.user ?? null;
      if (user?.email) loadExpenses();
      else expenses = [];
    });
  });

  async function loadUsers() {
    try {
      users = await fetchUsers();
      const me = users.find(u => u.email === user?.email);
      isEventHandler = me && me.role === 'handler';
    } catch {}
  }

  async function loadExpenses() {
    if (user?.email) {
      try {
        expenses = await fetchExpenses(user.email);
      } catch (e) {
        expenseError = e.message;
      }
    }
  }

  async function loadAllExpenses() {
    try {
      allExpenses = await fetchAllExpenses();
    } catch (e) {
      expenseError = e.message;
    }
  }

  async function handleAddExpense() {
    expenseError = '';
    if (!eventName.trim() || !eventCost) {
      expenseError = 'Event name and cost required';
      return;
    }
    try {
    
      let name = user?.email;
      let role = 'user';
      if (users && users.length > 0) {
        const me = users.find(u => u.email === user.email);
        if (me) {
          name = me.name;
          role = me.role;
        }
      }
      await addExpense({ user_email: user.email, event_name: eventName, cost: parseFloat(eventCost), name, role });
      eventName = '';
      eventCost = '';
      await loadExpenses();
      if (showAll && isEventHandler) await loadAllExpenses();
      await loadUsers();
    } catch (e) {
      expenseError = e.message;
    }
  }

  async function handleDeleteExpense(id) {
    try {
      await deleteExpense(id);
      if (showAll && isEventHandler) await loadAllExpenses();
      else await loadExpenses();
    } catch (e) {
      expenseError = e.message;
    }
  }

  async function toggleShowAll() {
    showAll = !showAll;
    expenseError = '';
    if (showAll) await loadAllExpenses();
  }

  async function handleReceiptUpload(event, expense) {
    const file = event.target.files[0];
    if (!file) return;
    const filePath = `${expense.user_email}/${expense.id}_${file.name}`;
    const { data, error } = await supabase.storage.from('reciepts').upload(filePath, file, { upsert: true });
    if (error) {
      expenseError = 'Failed to upload receipt.';
      return;
    }
    // Get public URL
    const { data: publicUrlData } = supabase.storage.from('reciepts').getPublicUrl(filePath);
    const publicUrl = publicUrlData.publicUrl;
    try {
      await updateReceiptUrl(expense.id, publicUrl);
      if (showAll && isEventHandler) await loadAllExpenses();
      else await loadExpenses();
    } catch (e) {
      expenseError = e.message;
    }
  }
</script>

<style>
.expense-section {
  margin: 2em auto 0 auto;
  background: #181818;
  border-radius: 12px;
  padding: 1.5em 3em 2em 3em;
  box-shadow: 0 2px 12px #0006;
  max-width: 800px;
  width: 90vw;
}
.expense-form {
  display: flex;
  gap: 1em;
  margin-bottom: 1em;
}
.expense-form input {
  flex: 1;
}
.expense-list {
  list-style: none;
  padding: 0;
}
.expense-list li {
  margin-bottom: 0.7em;
  background: #222;
  border-radius: 6px;
  padding: 0.7em 1em;
  color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}
.expense-total {
  margin-top: 1em;
  font-weight: bold;
  color: #8ec6ff;
}
.delete-btn {
  background: #960404;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.3em 0.9em;
  cursor: pointer;
  font-size: 0.95em;
  margin-left: 1em;
  transition: background 0.2s;
}
.delete-btn:hover {
  background: #ff0000;
}
.toggle-btn {
  background: #646cff;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.5em 1.2em;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 1em;
  margin-right: 1em;
  transition: background 0.2s;
}
.toggle-btn:hover {
  background: #535bf2;
}
.user-group {
  margin-bottom: 2em;
}
.user-group-title {
  color: #8ec6ff;
  font-size: 1.1em;
  margin-bottom: 0.5em;
}
.receipt-img {
  max-width: 100px;
  max-height: 80px;
  border-radius: 4px;
  margin-left: 1em;
  background: #fff;
}
.receipt-link {
  color: #8ec6ff;
  margin-left: 1em;
  font-size: 0.95em;
}
.upload-label {
  margin-left: 1em;
  color: #aaa;
  font-size: 0.95em;
  cursor: pointer;
}
input[type="file"] {
  display: none;
}
.grand-total {
  font-size: 1.3em;
  color: #4ade80;
  margin-bottom: 1.5em;
  margin-top: 1em;
  text-align: center;
}
</style>

<div class="expense-section">
  <h2>Your Event Expenses</h2>
  {#if isEventHandler}
    <button class="toggle-btn" on:click={toggleShowAll}>
      {showAll ? 'Show My Expenses' : 'Show All Users Expenses'}
    </button>
  {/if}
  {#if !showAll}
    <form class="expense-form" on:submit|preventDefault={handleAddExpense}>
      <input type="text" placeholder="Event name" bind:value={eventName} required />
      <input type="number" placeholder="Cost" bind:value={eventCost} min="0" step="0.01" required />
      <button type="submit">Add Expense</button>
    </form>
    {#if expenseError}
      <p class="error">{expenseError}</p>
    {/if}
    <ul class="expense-list">
      {#each expenses as exp}
        <li>
          <span>
            <strong>{exp.event_name}</strong>: ₹{exp.cost} <span style="color:#888; font-size:0.95em;">({new Date(exp.timestamp).toLocaleString()})</span>
            {#if exp.receipt_url}
              <a class="receipt-link" href={exp.receipt_url} target="_blank">View Receipt</a>
              <img class="receipt-img" src={exp.receipt_url} alt="Receipt" />
            {/if}
            {#if exp.user_email === user.email}
              <label class="upload-label">
                Upload Receipt
                <input type="file" accept="image/*" on:change={(e) => handleReceiptUpload(e, exp)} />
              </label>
            {/if}
          </span>
          <button class="delete-btn" on:click={() => handleDeleteExpense(exp.id)}>Delete</button>
        </li>
      {/each}
    </ul>
    <p class="expense-total">Total: ₹{expenses.reduce((sum, e) => sum + e.cost, 0)}</p>
  {:else}
    <div class="grand-total">
      <strong>Grand Total: ₹{grandTotal}</strong>
    </div>
    {#if expenseError}
      <p class="error">{expenseError}</p>
    {/if}
    {#each Object.entries(groupByUser(allExpenses)) as [email, exps]}
      <div class="user-group">
        <div class="user-group-title">{email}</div>
        <ul class="expense-list">
          {#each exps as exp}
            <li>
              <span>
                <strong>{exp.event_name}</strong>: ₹{exp.cost} <span style="color:#888; font-size:0.95em;">({new Date(exp.timestamp).toLocaleString()})</span>
                {#if exp.receipt_url}
                  <a class="receipt-link" href={exp.receipt_url} target="_blank">View Receipt</a>
                  <img class="receipt-img" src={exp.receipt_url} alt="Receipt" />
                {/if}
              </span>
            </li>
          {/each}
        </ul>
        <p class="expense-total">Total: ₹{exps.reduce((sum, e) => sum + e.cost, 0)}</p>
      </div>
    {/each}
  {/if}
</div> 