# How to Run the Wheel of Fortune MiniApp

This guide will help you start the Backend (API), the Telegram Bot, and the Frontend (User Interface).

## Prerequisites
- Python 3.8+ (Installed)
- Node.js 16+ (Installed)
- A Telegram Bot Token (from @BotFather)

---

## Step 1: Configuration

1. **Environment Variables**:
   - Locate `backend/.env`.
   - Update the following values:
     ```ini
     BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_FROM_BOTFATHER
     SECRET_KEY=some_random_secret_string
     CPA_SECRET_TOKEN=secure_token_for_postbacks
     WEBAPP_URL=https://t.me/YourBot/app
     # Comma-separated list of Telegram User IDs who are admins
     ADMIN_IDS=123456789,987654321
     ```
   - **Note**: Replace `123456789` with your actual Telegram User ID to access the Admin Panel.

---

## Step 2: Set Up the Backend (Server)

The backend handles the game logic, database, and user accounts.

1. Open a terminal.
2. Navigate to the `backend` folder:
   `cd backend`
3. Create/Activate virtual environment (optional but recommended).
4. Install dependencies:
   `pip install fastapi uvicorn sqlalchemy aiosqlite pydantic-settings python-dotenv aiogram pydantic requests`
5. Initialize the database:
   `python init_db.py`
6. **Start the server** (Must run from `backend` directory):
   `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

> **Success:** You should see "Application startup complete."
> The Backend is now running at `http://localhost:8000`.

---

## Step 3: Run the Telegram Bot

The bot handles user interactions like `/start` and Deep Linking.

1. Open a **NEW** terminal window.
2. Navigate to the project root (where `bot/` folder is).
3. Ensure dependencies are installed (same as backend).
4. Start the bot:
   `python bot/main.py`

> **Success:** The bot should start polling.
> Test it by sending `/start` to your bot in Telegram. It should reply with a Welcome message and a "Play Now" button.

---

## Step 4: Set Up the Frontend (MiniApp)

The frontend is the visual interface.

1. Open a **NEW** terminal window.
2. Navigate to the `frontend` folder:
   `cd frontend`
3. Install dependencies:
   `npm install`
4. Start the development server:
   `npm run dev`

> **Success:** Open `http://localhost:5173` in your browser.

---

## Step 5: Admin Panel & Statistics

1. **Whitelist Yourself**: Ensure your Telegram ID is in `ADMIN_IDS` in `backend/.env` and **restart the backend**.
2. **Access Dashboard**:
   - Go to `http://localhost:5173/admin`.
   - You will see statistics (Users, Tasks, Revenue) and tools to manually add spins or create tasks.
3. **Bot Admin Commands**:
   - Send `/stats` to the bot to get a quick summary.
   - Send `/broadcast <message>` to simulated mass messaging.

---

## Step 6: Testing the App

1. **Login:** In browser (`http://localhost:5173`), the app uses a Mock User (ID: 123456789).
2. **Spin:** Click "SPIN!" to play.
3. **Tasks:** Click tasks to simulate CPA offers.

## Advanced: CPAGrip Integration

- **Postback URL:** `http://YOUR_SERVER_IP:8000/tasks/cpagrip_postback`
- **Frontend Config:** Update `frontend/src/components/TaskList.tsx` with your CPAGrip URL.

---

## Troubleshooting

- **ModuleNotFoundError: No module named 'app'**:
  - Make sure you run `uvicorn` inside the `backend/` folder: `cd backend && uvicorn app.main:app --reload`.
- **403 Forbidden on Admin Panel**:
  - Your Telegram ID is not in `ADMIN_IDS` in `.env`.
  - You didn't restart the backend after editing `.env`.
