"""24/7 Telegram Bot for Option 1: Blender 5.2 + Python on GitHub Actions.
Features live auto-updating progress messages right inside Telegram (every 20s) + /status command.
"""
import os, re, json, time, base64, asyncio, threading, logging
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from story_gen import generate_blender_story

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GITHUB_TOKEN   = os.environ["GITHUB_TOKEN"]
GITHUB_REPO    = os.environ["GITHUB_REPO"]
GITHUB_BRANCH  = os.environ.get("GITHUB_BRANCH", "main")
ALLOWED_CHAT   = os.environ.get("ALLOWED_CHAT_ID", "").strip()

GH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def slugify(text: str) -> str:
    s = re.sub(r"^in this town[,:\s]*", "", text.strip().lower())
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return (s[:36] or "story").strip("_")


def gh_put_file(path: str, content_str: str, message: str):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    r = requests.get(url, headers=GH_HEADERS, params={"ref": GITHUB_BRANCH}, timeout=20)
    sha = r.json().get("sha") if r.status_code == 200 else None
    payload = {
        "message": message,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("ascii"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha
    resp = requests.put(url, headers=GH_HEADERS, json=payload, timeout=30)
    resp.raise_for_status()


def gh_trigger_workflow(slug: str, chat_id: int, sign_text: str = "THANK|YOU"):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/render_blender.yml/dispatches"
    payload = {
        "ref": GITHUB_BRANCH,
        "inputs": {
            "slug": slug,
            "chat_id": str(chat_id),
            "sign_text": sign_text,
        },
    }
    resp = requests.post(url, headers=GH_HEADERS, json=payload, timeout=30)
    resp.raise_for_status()


def gh_latest_run():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/render_blender.yml/runs"
    r = requests.get(url, headers=GH_HEADERS, params={"per_page": 1}, timeout=20)
    r.raise_for_status()
    runs = r.json().get("workflow_runs", [])
    return runs[0] if runs else None


def gh_run_jobs(run_id: int):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}/jobs"
    r = requests.get(url, headers=GH_HEADERS, params={"per_page": 50}, timeout=20)
    r.raise_for_status()
    return r.json().get("jobs", [])


def format_run_progress(run: dict, jobs: list, slug: str, elapsed_s: int) -> str:
    mins, secs = divmod(elapsed_s, 60)
    prep = next((j for j in jobs if j["name"] == "prepare"), None)
    fin  = next((j for j in jobs if j["name"] == "finish"), None)
    ren  = [j for j in jobs if j["name"].startswith("render")]

    def icon(j):
        if not j: return "⏳ Waiting"
        if j["status"] == "completed":
            return "✅ Done" if j["conclusion"] == "success" else f"❌ {j['conclusion']}"
        if j["status"] == "in_progress": return "🔄 Running"
        return "⏳ Queued"

    r_done = sum(1 for j in ren if j["status"] == "completed" and j["conclusion"] == "success")
    r_fail = sum(1 for j in ren if j["status"] == "completed" and j["conclusion"] != "success")
    r_run  = sum(1 for j in ren if j["status"] == "in_progress")
    r_tot  = max(len(ren), 20)
    bar_n  = int(round(10 * r_done / r_tot))
    bar    = "█" * bar_n + "░" * (10 - bar_n)

    status_line = run.get("status", "unknown")
    if status_line == "completed":
        status_line = f"completed ({run.get('conclusion', '')})"

    lines = [
        f"🎬 Render: {slug}",
        f"Status: {status_line} | Elapsed: {mins}m {secs:02d}s",
        "",
        f"1. Voice & Textures: {icon(prep)}",
        f"2. Blender 60fps: [{bar}] {r_done}/{r_tot} done ({r_run} running" + (f", {r_fail} failed)" if r_fail else ")"),
        f"3. Captions & MP4: {icon(fin)}",
        "",
        f"Logs: {run.get('html_url', '')}",
    ]
    return "\n".join(lines)


async def track_live_progress(msg, slug: str, prev_run_id):
    t0 = time.time()
    run = None
    # Wait up to 45s for the newly dispatched run to appear
    for _ in range(9):
        await asyncio.sleep(5)
        try:
            cand = gh_latest_run()
            if cand and cand["id"] != prev_run_id:
                run = cand
                break
        except Exception:
            pass

    if not run:
        await msg.edit_text("Triggered GitHub Actions, but couldn't fetch the live run yet. Send /status in 15 seconds.")
        return

    run_id = run["id"]
    last_text = ""
    while True:
        try:
            run = requests.get(
                f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}",
                headers=GH_HEADERS, timeout=20
            ).json()
            jobs = gh_run_jobs(run_id)
            txt = format_run_progress(run, jobs, slug, int(time.time() - t0))
            if txt != last_text:
                await msg.edit_text(txt, disable_web_page_preview=True)
                last_text = txt
            if run.get("status") == "completed":
                break
        except Exception as e:
            log.warning("Progress poll error: %s", e)
        await asyncio.sleep(20)


def is_allowed(chat_id: int) -> bool:
    return not ALLOWED_CHAT or str(chat_id) == ALLOWED_CHAT


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.reply_text(
        f"Bot is live! Your chat ID is `{cid}`.\n\n"
        "Commands:\n"
        "• Send `In this town, ...` to create a new 60 fps short\n"
        "• Send `/demo` to render Never Say Thank You\n"
        "• Send `/status` to check live GitHub Actions progress anytime",
        parse_mode="Markdown",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_allowed(chat_id):
        return
    try:
        run = gh_latest_run()
        if not run:
            await update.message.reply_text("No workflow runs found yet.")
            return
        jobs = gh_run_jobs(run["id"])
        txt = format_run_progress(run, jobs, run.get("display_title", "latest"), 0)
        await update.message.reply_text(txt, disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"Error checking status: {e}")


async def cmd_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_allowed(chat_id):
        return
    msg = await update.message.reply_text("Starting GitHub Actions render for never_say_thank_you...")
    try:
        prev = gh_latest_run()
        prev_id = prev["id"] if prev else None
        gh_trigger_workflow("never_say_thank_you", chat_id, "THANK|YOU")
        asyncio.create_task(track_live_progress(msg, "never_say_thank_you", prev_id))
    except Exception as e:
        log.exception("Demo trigger failed")
        await msg.edit_text(f"Error triggering GitHub Actions: {e}")


async def handle_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    chat_id = update.effective_chat.id
    if not is_allowed(chat_id):
        return

    text = update.message.text.strip()
    if text.startswith("/make "):
        text = text[6:].strip()
    elif not text.lower().startswith("in this town"):
        await update.message.reply_text('Start your idea with "In this town, ..." (or send /demo or /status).')
        return

    slug = slugify(text)
    status = await update.message.reply_text(f"Writing script & Blender 3D shots for {slug}...")

    try:
        story_json, story_py, sign_text = generate_blender_story(text, slug)
        lines_preview = "\n".join(f"{i+1}. {s['line']}" for i, s in enumerate(story_json["shots"]))

        gh_put_file(f"stories/{slug}.json", json.dumps(story_json, indent=1), f"Add story {slug}.json")
        gh_put_file(f"stories/{slug}.py", story_py, f"Add Blender scene {slug}.py")

        prev = gh_latest_run()
        prev_id = prev["id"] if prev else None
        gh_trigger_workflow(slug, chat_id, sign_text)

        await update.message.reply_text(f"Script for {slug}:\n\n{lines_preview}")
        asyncio.create_task(track_live_progress(status, slug, prev_id))
    except Exception as e:
        log.exception("Failed handling idea")
        await status.edit_text(f"Error: {e}")


web = Flask(__name__)

@web.route("/")
@web.route("/health")
def health():
    return "OK", 200


def run_web():
    port = int(os.environ.get("PORT", "10000"))
    web.run(host="0.0.0.0", port=port, use_reloader=False)


def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("demo", cmd_demo))
    app.add_handler(CommandHandler("make", handle_idea))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea))
    log.info("Telegram bot started (polling)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()