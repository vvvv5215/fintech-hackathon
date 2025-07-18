# Event Management App

A event budget tracking platform for college events, featuring Google OAuth authentication, expense tracking, and role-based access for event handlers and payers.

## Features
- **Google OAuth** authentication (via Supabase)
- **Role-based access**: Event Handler & User
- **Expense tracking** per user
- **Receipt upload & view** (Supabase Storage)
- **Event handler dashboard**: view all expenses, grand total, manage users
- **First event handler**: claimable via secret code
- **Modern, responsive UI** (Svelte)

## Tech Stack
- **Frontend**: Svelte
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase-hosted)
- **Auth & Storage**: Supabase

## Setup Instructions

### 1. Clone the repo

### 2. Environment Variables
- Create a `.env` file in `backend/` with:
  ```env
  DATABASE_URL=  {add your own}
  HANDLER_SECRET_CODE= {your own choice!!}
  ```
- Set up Supabase project and get your credentials for Auth and Storage.

### 3. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Frontend (Svelte)
```bash
cd frontend
npm install
npm run dev
```
- Configure Supabase keys in `frontend/src/lib/supabase.js`.

## Usage
- Visit the frontend URL (default: `http://localhost:5173`)
- Sign in with your Google (college) account
- If no event handler exists, claim the role with the secret code
- Add expenses, upload/view receipts, and manage users as an event handler



## Credits
- Built with [Svelte](https://svelte.dev/), [FastAPI](https://fastapi.tiangolo.com/), and [Supabase](https://supabase.com/)
- Developed for IIITDM FinTech Hackathon
