const API_URL = 'http://localhost:8000';

export async function fetchExpenses(user_email) {
  const res = await fetch(`${API_URL}/expenses?user_email=${encodeURIComponent(user_email)}`);
  if (!res.ok) throw new Error('Failed to fetch expenses');
  return await res.json();
}

export async function addExpense(expense) {
  const res = await fetch(`${API_URL}/expenses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(expense)
  });
  if (!res.ok) throw new Error('Failed to add expense');
  return await res.json();
}

export async function deleteExpense(expense_id) {
  const res = await fetch(`${API_URL}/expenses/${expense_id}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete expense');
  return await res.json();
}

export async function fetchAllExpenses() {
  const res = await fetch(`${API_URL}/expenses/all`);
  if (!res.ok) throw new Error('Failed to fetch all expenses');
  return await res.json();
}

export async function updateReceiptUrl(expense_id, receipt_url) {
  const res = await fetch(`${API_URL}/expenses/${expense_id}/receipt`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(receipt_url)
  });
  if (!res.ok) throw new Error('Failed to update receipt URL');
  return await res.json();
}

export async function deleteExpensesByUser(user_email) {
  const res = await fetch(`${API_URL}/expenses/by_user/${encodeURIComponent(user_email)}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete user expenses');
  return await res.json();
}

export async function fetchUsers() {
  const res = await fetch(`${API_URL}/users_from_expenses`);
  if (!res.ok) throw new Error('Failed to fetch users');
  return await res.json();
}