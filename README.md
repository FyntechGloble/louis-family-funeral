# Louis Brown — Private family funeral planner

A private mobile-friendly funeral coordination app for the Brown family. Supports individual family logins, administrator invitations, coordinator and read-only viewer roles, shared checklists, task assignment, funeral details, expense tracking, and an installable web-app manifest.

## Portainer web installation

Repository: https://github.com/FyntechGloble/louis-family-funeral

1. In Portainer, go to **Stacks → Add stack → Git Repository**, use the repository URL above, branch **main**, and Compose path **docker-compose.yml**. Configure Git credentials if Portainer cannot access this private repository.
2. Under **Environment variables** (these are *Portainer Stack variables*, NOT just container labels or values in a local file), add:
   - `APP_SECRET`: generate 64 random hexadecimal characters using a trusted password generator or `openssl rand -hex 32`. **Never use the example placeholder or post the value in chat.**
   - `ADMIN_EMAIL`: your private administrator email address.
   - `ADMIN_PASSWORD`: a strong random password of at least 12 characters.
   - `ALLOWED_ORIGIN`: your exact external address, e.g. `https://family.siteforgeglobal.com`.
   - `SECURE_COOKIES`: `true` for HTTPS production access.
3. Deploy the stack. This repository now uses the same local Docker build pattern as your working FarmFinder stack: `build: .` plus `pull_policy: build`. It does not request any image from GHCR. Git-based Stack deployment must support building from the repository checkout; if it reports that the build context is unavailable, the current Portainer deployment method cannot build from Git and needs a build-capable setup.
4. In Portainer **Containers**, check that the app container is **running/healthy**, then open **Logs** if it restarts. A previous error `APP_SECRET must be at least 32 characters` means the secret is missing or too short **inside the container**. Adding it to Portainer's Stack variables and updating the Stack fixes that only if the updated container inherits those variables. If an existing stack was created in Web Editor mode, GitHub commits are *not* automatically pulled: recreate or switch it to a Git repository deployment after preserving its database volume.
5. The host port is **8087**, mapped to **8080 inside the container** (`8087:8080`). Test `http://SERVER-IP:8087` from a trusted network only. A remote firewall may block this port; do not publicly expose an HTTP login as a production arrangement.
6. For production, configure **Nginx Proxy Manager** with domain `family.siteforgeglobal.com`, Let's Encrypt HTTPS, and an upstream reachable from the proxy. For a proxy on the same Docker network, use the service/container name and internal port **8080**. For a proxy connecting to the server's host address, use the server IP and external port **8087**. Do not use localhost inside a different container.
7. Access the HTTPS URL and sign in as administrator. Add relatives under **Family & access** and have them change temporary passwords.

## Data and privacy

The app persists its SQLite database in the named Docker volume `family_data` at `/data/family.db`. **Do not delete this volume when redeploying.** In Compose deployments, Docker may prefix the volume name with the Stack project name. Back it up securely.

This is a small family planning app. It does not yet support document uploads, self-service password recovery, account revocation UI, or full offline access. Avoid storing ID numbers, certificates, medical files or bank information. Configure HTTPS and reverse-proxy login rate limits before inviting family.

## Local Docker Compose

Copy `.env.example` to `.env`, replace ALL placeholders with secure values and run `docker compose up -d --build`. Use `docker compose logs -f` for diagnosis.
