# Phone-Only Setup Guide (Telegram -> Render -> GitHub Actions Blender 5.2)

## 1. Create a Telegram Bot (1 min)
1. Open **@BotFather** in Telegram and send `/newbot`.
2. Copy the **Bot Token** (`TELEGRAM_TOKEN`).

## 2. Get a Free Gemini API Key (1 min)
1. Open https://aistudio.google.com/apikey and tap **Create API key**.
2. Copy the key (`GEMINI_API_KEY`).

## 3. Create Your GitHub Repo & Add Secrets (2 min)
1. Create a **Public** repo on https://github.com/new (public repos get unlimited free GitHub Actions minutes).
2. Upload all files from this zip into the repo (keep `.github/workflows/render_blender.yml` and `stories/` paths intact).
3. In your repo go to **Settings -> Secrets and variables -> Actions -> New repository secret**:
   - Name: `TELEGRAM_TOKEN` -> paste your BotFather token.
4. Create a GitHub token at https://github.com/settings/personal-access-tokens/new:
   - Scope it to your new repo with **Contents: Read and write** and **Actions: Read and write**.
   - Copy the token (`GITHUB_TOKEN`).

## 4. Deploy the 24/7 Bot Free on Render (2 min)
1. Open https://dashboard.render.com -> **New -> Web Service** -> connect your GitHub repo.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python bot.py`
4. Add these **Environment Variables**:
   - `TELEGRAM_TOKEN` = your BotFather token
   - `GEMINI_API_KEY` = your Gemini API key
   - `GITHUB_TOKEN` = your GitHub Personal Access Token
   - `GITHUB_REPO` = `yourusername/your-repo-name`
   - `ALLOWED_CHAT_ID` = *(optional: send `/start` to your bot first to see your chat ID, then paste it here so only you can use it)*
5. Tap **Deploy**. *(Optional: add your Render URL `https://your-app.onrender.com/health` to UptimeRobot every 5 min so it stays awake 24/7.)*

## 5. Make Shorts from Telegram!
- Send `/demo` to render the pre-built **Never Say Thank You** 60 fps short right away.
- Or send any new idea starting with:
  `In this town, nobody is allowed to blink`
- In ~8–12 minutes, the finished **1080×1920 60 fps MP4** drops straight into your Telegram chat!
