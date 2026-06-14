Security
========

Short guidance:
- Do not commit credentials or session files. Keep secrets in a local
  `.env` (which is ignored) or use a secrets manager.
- Ensure `.env` and any session/media files are listed in `.gitignore`.
- If you accidentally commit secrets, rotate them and remove the
  sensitive items from the repository history.

If you need help with rotation or history cleanup, open an issue.
