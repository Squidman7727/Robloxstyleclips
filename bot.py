"""24/7 Telegram Bot for Option 1: Blender 5.2 + Python on GitHub Actions.
Host free on Render.com (Web Service) + optional UptimeRobot ping to /health.

Send in Telegram:
  In this town, nobody is allowed to say thank you
or:
  /demo   (renders the pre-built 'never_say_thank_you' short immediately)
"""
import os, re, json, base64, threading, logging
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from story_gen import generate_blender_story

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GITHUB_TOKEN   = os.environ["GITHUB_TOKEN"]       # Fine-grained PAT: Contents (RW) + Actions (RW)
GITHUB_REPO    = os.environ["GITHUB_REPO"]        # e.g. "yourname/in-this-town-bot"
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


def is_allowed(chat_id: int) -> bool:
    return not ALLOWED_CHAT or str(chat_id) == ALLOWED_CHAT


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.reply_text(
        f"Bot is live! Your chat ID is `{cid}`.\n\n"
        "Send any idea starting with:\n"
        "`In this town, ...`\n\n"
        "Or send `/demo` to render the pre-built *Never Say Thank You* 60 fps short right now.",
        parse_mode="Markdown",
    )


async def cmd_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_allowed(chat_id):
        return
    msg = await update.message.reply_text("Triggering GitHub Actions 20-runner Blender render for `never_say_thank_you`...", parse_mode="Markdown")
    try:
        gh_trigger_workflow("never_say_thank_you", chat_id, "THANK|YOU")
        await msg.edit_text("Started! 20 parallel GitHub runners are rendering all 1,200 frames (60 fps). Your MP4 will arrive here in ~8–12 minutes.")
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
        await update.message.reply_text('Start your idea with "In this town, ..." (or send /demo).')
        return

    slug = slugify(text)
    status = await update.message.reply_text(f"Writing script & Blender 3D shots for `{slug}`...", parse_mode="Markdown")

    try:
        story_json, story_py, sign_text = generate_blender_story(text, slug)
        lines_preview = "\n".join(f"{i+1}. {s['line']}" for i, s in enumerate(story_json["shots"]))

        gh_put_file(f"stories/{slug}.json", json.dumps(story_json, indent=1), f"Add story {slug}.json")
        gh_put_file(f"stories/{slug}.py", story_py, f"Add Blender scene {slug}.py")
        gh_trigger_workflow(slug, chat_id, sign_text)

        await status.edit_text(
            f"Script & Blender scene ready! Rendering 1,200 frames (60 fps) across 20 GitHub runners:\n\n"
            f"{lines_preview}\n\n"
            f"Your finished MP4 will arrive here in ~8–12 minutes."
        )
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
    app.add_handler(CommandHandler("demo", cmd_demo))
    app.add_handler(CommandHandler("make", handle_idea))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea))
    log.info("Telegram bot started (polling)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
