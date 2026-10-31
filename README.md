# Realt listing monitor

Every 20 minutes, GitHub Actions checks the newest page of Realt apartment listings in Grodno. New listings marked **Контактное лицо** are sent to Telegram. Seen listing IDs are saved in `seen_ids.json` and committed to this repository.

## Setup

1. Create a Telegram bot with [@BotFather](https://t.me/BotFather), then open the bot and send `/start`.
2. Find your numeric chat ID by opening `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` after sending `/start`. Use the value in `message.chat.id`.
3. Push this repository to GitHub. In **Settings → Secrets and variables → Actions**, add repository secrets named `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
4. In **Settings → Actions → General**, allow workflows to have read and write permissions for the repository. The workflow needs this to commit `seen_ids.json`.
5. In **Actions**, run **Monitor Realt listings** once with **Run workflow**. The first run records the current page without sending old listings. New matching listings will be sent on later runs.

Keep the repository public to use GitHub-hosted Actions without a monthly minutes quota. In a private repository, the free plan has a limited number of Actions minutes; a run every 20 minutes is about 2,160 runs per 30 days, and short jobs may still be billed as one minute each. Check the current limits for your GitHub plan before relying on a private repository.

The bot token is stored as a GitHub secret and must not be added to this repository.# flatbot
