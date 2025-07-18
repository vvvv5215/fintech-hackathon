import { writable } from 'svelte/store';

const LOCAL_STORAGE_KEY = 'users';

function loadUsers() {
  if (typeof localStorage === 'undefined') return [];
  const users = localStorage.getItem(LOCAL_STORAGE_KEY);
  return users ? JSON.parse(users) : [];
}

function saveUsers(users) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(users));
}

function createUserStore() {
  const { subscribe, set, update } = writable(loadUsers());

  return {
    subscribe,
    addUser: (user) => {
      update(users => {
        const newUsers = [...users, user];
        saveUsers(newUsers);
        return newUsers;
      });
    },
    removeUser: (id) => {
      update(users => {
        const newUsers = users.filter(u => u.id !== id);
        saveUsers(newUsers);
        return newUsers;
      });
    },
    updateUser: (updatedUser) => {
      update(users => {
        const newUsers = users.map(u => u.id === updatedUser.id ? updatedUser : u);
        saveUsers(newUsers);
        return newUsers;
      });
    },
    getUserById: (id) => {
      let user;
      update(users => {
        user = users.find(u => u.id === id);
        return users;
      });
      return user;
    },
    reset: () => {
      set([]);
      saveUsers([]);
    }
  };
}

export const userStore = createUserStore(); 