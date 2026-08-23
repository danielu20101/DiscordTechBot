# DiscordTechBot
Created a discord bot to scrape 2 webpages: Amazon.com and techdeals.in webpages to deliever quality deals to a discord server

## Weekly email digest

Every 7 days the bot emails a digest of the deals collected that week to `unguryan77@gmail.com`. The email
includes a "What specific tech deals are you looking for?" prompt — reply to that email with a search term
(e.g. "gaming laptop") and the bot will scrape Amazon for it, post matches to the Discord channel, and email
the results back.

Setup:
1. Enable 2-Step Verification on the Gmail account used to send the digest, then create an
   [App Password](https://myaccount.google.com/apppasswords).
2. Make sure IMAP is enabled in Gmail settings (Settings → Forwarding and POP/IMAP → Enable IMAP), since
   replies are read via IMAP.
3. Fill in `.env`:
   ```
   EMAIL_ADDRESS=your_bot_gmail@gmail.com
   EMAIL_APP_PASSWORD=your_16_char_app_password
   ```

The digest send-time and reply-check both run automatically once the bot is online (checked daily and every
30 minutes respectively) — no extra process needed.
