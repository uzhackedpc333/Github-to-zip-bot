import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN
from database import (
    init_db, set_language, get_language, add_repo, get_user_repos,
    get_all_repos_for_polling, update_repo_sha, remove_repo
)
from github_ops import parse_url, get_latest_zipball
from i18n import get_text

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)
    if lang:
        await show_menu(update, context, lang)
    else:
        kb = [[
            InlineKeyboardButton(get_text(uid, "btn_en"), callback_data="lang_en"),
            InlineKeyboardButton(get_text(uid, "btn_uz"), callback_data="lang_uz")
        ]]
        await update.message.reply_text(get_text(uid, "start_prompt"), reply_markup=InlineKeyboardMarkup(kb))

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang_", "")
    if lang not in ("en", "uz"):
        return

    set_language(query.from_user.id, lang)
    lang_name = "English" if lang == "en" else "O'zbek"
    await query.edit_message_text(get_text(query.from_user.id, "lang_set").format(lang=lang_name))
    await show_menu(update, context, lang, query.message)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str, msg=None):
    uid = update.effective_user.id
    kb = [
        [InlineKeyboardButton(get_text(uid, "btn_list"), callback_data="menu_list"),
         InlineKeyboardButton(get_text(uid, "btn_help"), callback_data="menu_help")],
        [InlineKeyboardButton(get_text(uid, "btn_change_lang"), callback_data="menu_lang")]
    ]
    target = msg if msg else update.message
    await target.reply_text(get_text(uid, "main_menu"), reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    action = query.data.replace("menu_", "")

    if action == "lang":
        kb = [[
            InlineKeyboardButton(get_text(uid, "btn_en"), callback_data="lang_en"),
            InlineKeyboardButton(get_text(uid, "btn_uz"), callback_data="lang_uz")
        ]]
        await query.message.reply_text(get_text(uid, "lang_change_prompt"), reply_markup=InlineKeyboardMarkup(kb))
    elif action == "help":
        await query.message.reply_text(get_text(uid, "help_text"), parse_mode="Markdown")
    elif action == "list":
        repos = get_user_repos(uid)
        if not repos:
            await query.message.reply_text(get_text(uid, "no_repos"))
        else:
            keyboard = []
            text = get_text(uid, "tracked_repos")
            for r in repos:
                # Add repo info to text
                text += get_text(uid, "repo_item").format(owner=r["owner"], repo=r["repo"], sha=r["last_sha"][:8])
                # Add button to remove this repo
                keyboard.append([InlineKeyboardButton(f"❌ Remove {r['owner']}/{r['repo']}", callback_data=f"remove_{r['id']}")])
            
            await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def remove_repo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    repo_id = int(query.data.split("_")[1])
    
    remove_repo(uid, repo_id)
    await query.message.reply_text(get_text(uid, "repo_removed"))

async def handle_repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    owner, repo = parse_url(text)

    if not owner:
        await update.message.reply_text(get_text(uid, "invalid_url"))
        return

    status = await update.message.reply_text(get_text(uid, "fetching").format(owner=owner, repo=repo))
    data = get_latest_zipball(owner, repo)

    if not data:
        await status.edit_text(get_text(uid, "repo_not_found"))
        return

    add_repo(uid, text, owner, repo, data["sha"])
    await status.edit_text(get_text(uid, "repo_found").format(
        owner=owner, repo=repo, sha=data["sha"][:8], message=data["message"]
    ), parse_mode="Markdown")

    await update.message.reply_document(
        document=data["zip_url"],
        filename=f"{repo}-{data['sha'][:8]}.zip",
        caption=get_text(uid, "download_caption").format(
            repo=repo, sha=data["sha"][:8], message=data["message"]
        ),
        parse_mode="Markdown"
    )

async def poll_repo_updates(context: ContextTypes.DEFAULT_TYPE):
    repos = get_all_repos_for_polling()
    if not repos:
        return

    for user_id, url, owner, repo, last_sha in repos:
        try:
            latest = get_latest_zipball(owner, repo)
            if latest and latest["sha"] != last_sha:
                update_repo_sha(url, latest["sha"])
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🔄 New commit in `{owner}/{repo}`!\n `{latest['sha'][:8]}`\n {latest['message']}",
                    parse_mode="Markdown"
                )
                await context.bot.send_document(
                    chat_id=user_id,
                    document=latest["zip_url"],
                    filename=f"{repo}-{latest['sha'][:8]}.zip",
                    caption=f"📦 Auto-updated ZIP",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logging.warning(f"Poll error for {owner}/{repo}: {e}")

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(remove_repo_callback, pattern="^remove_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_repo))

    app.job_queue.run_repeating(poll_repo_updates, interval=120, first=10)

    print("✨ Bot is running with auto-update and management...")
    app.run_polling()

if __name__ == "__main__":
    main()
