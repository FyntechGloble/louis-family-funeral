# Louis Brown memorial booklet

The original interactive 15-page Louis Brown memorial booklet, with Nytjie's Afrikaans tribute added **on page 10**, after Nathan's tribute. All embedded photographs, booklet animations and existing content are preserved.

## Deploy from Portainer using Git (recommended)

1. In Portainer, go to **Stacks > Add stack**, name it `louis-memorial`.
2. Select **Git repository**.
3. Repository URL: `https://github.com/FyntechGloble/louis-family-funeral`
4. Repository reference: `refs/heads/main` (branch `main`).
5. Compose path: `memorial-booklet/portainer-stack.yml`.
6. Deploy the stack.

Portainer runs a lightweight official Nginx container. The container securely downloads the public memorial HTML from this repository at startup; this means you do not need to build or publish a custom image.

To enable GitOps polling in Portainer, use the automatic-update option in the Git stack settings. If you edit `index.html`, redeploy/recreate the container to download the latest file. Do not deploy this Compose into the existing funeral-management stack; this is a standalone website.

## Configure the domain

- In Cloudflare DNS, point an `A` record for `louis.siteforgeglobal.com` at the public IP of your reverse proxy. If the record already exists, edit it.
- In Nginx Proxy Manager create or edit a Proxy Host: Domain `louis.siteforgeglobal.com`; scheme `http`; forward hostname = Docker host LAN IP; port = `8098`.
- Enable SSL with a valid certificate and Force SSL. Check that inbound HTTPS to your reverse proxy works, or use your existing Cloudflare Tunnel.
- Avoid exposing the `8098` origin port directly to the Internet. Restrict it with a firewall or use the shared-network stack below.
- If the host's port 8098 is occupied, choose another unused port in the Portainer stack and match the reverse proxy.

### Shared reverse-proxy Docker network (no published host port)

For Nginx Proxy Manager hosted on the same Docker engine, you can use `memorial-booklet/portainer-stack-shared-network.yml`. Replace external network `proxy` with the **actual** existing Nginx Proxy Manager Docker network. Forward in NPM to host/service `louis-memorial` and port `80`. This avoids exposing any extra host port. The reverse proxy and memorial containers must share that Docker network.

## Troubleshooting

- Check Portainer container logs for `wget` errors, especially when outbound HTTPS is blocked.
- Check the container health and that the GitHub HTML file is reachable.
- If `8098` is already used, adjust it or switch to the shared-network option.
- If `louis.siteforgeglobal.com` already serves something else, change its proxy host only when ready to replace the existing page.
- The original `dad.siteforgeglobal.com` funeral-management app stays separate.

## Manual build alternative

`Dockerfile` builds an offline Nginx image when `index.html` is supplied in the Docker build context.

This memorial website has no database and needs no WordPress installation.
