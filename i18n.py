TEXTS = {
    "en": {
        "start_prompt": "👋 Welcome! Please choose your language:",
        "btn_en": "🇬 English",
        "btn_uz": "🇺 O'zbek",
        "lang_set": "✅ Language set to {lang}!",
        "main_menu": "📖 Main Menu\n\nSend a GitHub repo URL to track it, or use the buttons below:",
        "btn_list": "📋 Manage Repos",
        "btn_help": "❓ Help",
        "btn_change_lang": " Change Language",
        "help_text": " How to use:\n1. Send a GitHub URL (e.g. `https://github.com/owner/repo`)\n2. I'll fetch the latest ZIP download link.\n3. Use `/repos` to view and remove tracked repos.\n4. Use `/lang` to change language.",
        "lang_change_prompt": "🌐 Choose a new language:",
        "invalid_url": "❌ Please send a valid GitHub repository URL.",
        "fetching": "🔍 Fetching `{owner}/{repo}`...",
        "repo_found": "✅ Found `{owner}/{repo}`!\n🔖 Latest commit: `{sha}`\n📝 `{message}`\n\n📦 Sending download link...",
        "repo_not_found": "❌ Repo not found or is private.",
        "no_repos": "📭 You haven't tracked any repos yet.",
        "tracked_repos": "📂 *Tracked Repositories*\n\nTap ❌ to remove a repository:",
        "repo_item": "• `{owner}/{repo}`\n  🔹 SHA: `{sha}`\n",
        "download_caption": "📂 **{repo}**\n {sha}\n📝 {message}",
        "repo_removed": "✅ Repository removed successfully!"
    },
    "uz": {
        "start_prompt": "👋 Xush kelibsiz! Iltimos, tilni tanlang:",
        "btn_en": "🇬 English",
        "btn_uz": "🇺🇿 O'zbek",
        "lang_set": "✅ Til {lang} ga o'rnatildi!",
        "main_menu": "📖 Asosiy menyu\n\nKuzatish uchun GitHub repo URL manzilini yuboring yoki tugmalardan foydalaning:",
        "btn_list": " Repo'lar",
        "btn_help": "❓ Yordam",
        "btn_change_lang": "🌐 Tilni o'zgartirish",
        "help_text": "📘 Foydalanish qo'llanmasi:\n1. GitHub URL manzilini yuboring (masalan: `https://github.com/owner/repo`)\n2. Men eng so'nggi ZIP yuklab olish havolasini jo'nataman.\n3. `/repos` orqali repo'larni ko'ring va o'chiring.\n4. `/lang` orqali tilni o'zgartiring.",
        "lang_change_prompt": "🌐 Yangi tilni tanlang:",
        "invalid_url": "❌ Iltimos, to'g'ri GitHub repo URL manzilini yuboring.",
        "fetching": "🔍 `{owner}/{repo}` qidirilmoqda...",
        "repo_found": "✅ `{owner}/{repo}` topildi!\n🔖 So'nggi commit: `{sha}`\n📝 `{message}`\n\n📦 Yuklab olish havolasi yuborilmoqda...",
        "repo_not_found": "❌ Repo topilmadi yoki yopiq.",
        "no_repos": " Hali hech qanday repo kuzatilmagan.",
        "tracked_repos": " *Kuzatilayotgan repo'lar*\n\nO'chirish uchun ❌ tugmasini bosing:",
        "repo_item": "• `{owner}/{repo}`\n  🔹 SHA: `{sha}`\n",
        "download_caption": "📂 **{repo}**\n🔖 {sha}\n📝 {message}",
        "repo_removed": "✅ Repo muvaffaqiyatli o'chirildi!"
    }
}

def get_text(user_id: int, key: str) -> str:
    from database import get_language
    lang = get_language(user_id) or "en"
    return TEXTS.get(lang, TEXTS["en"]).get(key, f"[Missing: {key}]")
