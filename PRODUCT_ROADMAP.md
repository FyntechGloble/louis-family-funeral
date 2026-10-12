# Roadmap: From Brown family funeral planner to a family-ready product

## Current release
- Existing **single-family** private workspace, for Louis Brown.
- Login, task assignment, expenses, service details and shared activity stay unchanged.
- Calm mobile-first styling and guided checklists.
- No family self-signup or multi-family data separation yet. **Do not onboard unrelated families on this instance.**

## Phase 1 — Reliability and usability (ship before external launch)
- Verify that Portainer stack container is healthy and reverse proxy reaches the running application.
- Add public `/health` endpoint with no sensitive data and simple diagnostics.
- Add safe rollback/version pinning and automated database backup + restore testing.
- Replace secret placeholder configuration with validation and deployment checks.
- Add login rate limiting, user account deactivation/recovery and first-login password change.
- Add automated smoke tests for login, tasks, settings, finance and static HTML.

## Phase 2 — Guided arrangements
- Priority grouping: Do now / This week / Before service / Funeral day / Afterward.
- A timeline, optional dates/reminders, assigned owner and meaningful next-step instructions.
- Customizable ceremony template: Christian, secular, other faiths; burial/cremation options.
- Service programme and printed PDF, contact directory, supplier quotes, WhatsApp-ready announcements.
- Optional memorial/gallery with explicit permission from the family.
- Clear 'optional' vs 'legally required' labels; country/region-specific requirements should be independently reviewed.
- Accessibility and Afrikaans/English localisation.

## Phase 3 — Separate families (required before selling)
- Dedicated family/workspace ID on all user-owned records, including tasks, expenses and activity.
- Tenant-scoped access controls on EVERY API endpoint and robust cross-family isolation tests.
- Invite-only family accounts, explicit roles, no data leakage in searches, logs, exports or links.
- Family settings for name, memorial text, photo, dates, colour theme and ceremony.
- Optional managed platform with verified payments and subscriptions; avoid unnecessary data collection.
- Data retention, backups, export, deletion, consent, privacy notice and South African POPIA review.
- A migration plan for the existing Louis Brown database, with backup and tested restore before any tenancy migration.

Do not merge unrelated families into the current SQLite tables without proper tenancy scoping.
