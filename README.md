# Louis Brown — Private family funeral planner

A mobile-friendly private web app designed for one family's funeral arrangements. Includes independent family logins, administrator invitations, read-only/viewer roles, shared 90+ item checklists, task assignment, notes, arrangements, budget estimates vs actuals, audit activity, and an installable web-app manifest. Default checklist and service details are in English and editable; the app can be translated later.

## Run on Docker / Portainer

1. Upload or clone this folder to a server that runs Docker Compose. **This archive is source code, not an already-deployed service.**
2. Copy `.env.example` to `.env`. Replace all placeholder values. Generate `APP_SECRET` using `openssl rand -hex 32`.
3. Set `ALLOWED_ORIGIN` to the exact public URL including `https://`, e.g. `https://memorial.yourdomain.co.za`.
4. `docker compose up -d --build`.
5. Place an HTTPS reverse proxy (Nginx Proxy Manager, Traefik, etc.) in front of `http://127.0.0.1:8087`. The included Compose port is host-local intentionally; HTTPS must be set up before remote family access.
6. Open the URL, sign in using `ADMIN_EMAIL` and `ADMIN_PASSWORD`, then go to **Family & access** to create separate logins. Ask invitees to change their password immediately.

**Portainer:** If Portainer's stack UI cannot build from a local folder, use its Git repository deployment with `docker-compose.yml` and a Docker build-capable deployment path, or build this image on the host first and replace the `build: .` line with your pushed image. No repo, domain, proxy, or remote server is configured by this package.

## Security and maintenance

- Use HTTPS and keep the site private. Do not post login credentials to the public family group.
- Login cookies are HTTP-only, SameSite Strict and Secure by default. Passwords are salted scrypt hashes.
- Configure reverse-proxy request rate limits for `/api/login` and add IP-based throttling. A family administrator should change the initial admin password after first sign-in.
- Accounts can be created, but this MVP does not yet support deactivation, password reset by admin, file attachments, email delivery, calendar invitations, or granular per-task access rights. Do not use the app to store ID scans, death certificates, medical records, or financial account details; only non-sensitive coordination information.
- All coordinators/family editors can change all task and budget data; the viewer role is read-only. Admin-only deletion applies to tasks via API, but there is no UI delete action.
- Back up Docker volume `family_data` regularly; SQLite database is at `/data/family.db`. Prefer SQLite's online backup API / `VACUUM INTO` or volume snapshot rather than a live file-only copy. Restrict access to backups.
- When using a proxy, pass the original `Origin` faithfully. Set `ALLOWED_ORIGIN` to your web app's exact HTTPS origin. `SECURE_COOKIES=false` is intended **only** for local HTTP development; never use on a public website.
- This is a family planning tool, not a substitute for Home Affairs, funeral director, broker, or estate legal advice.
