import { UsersApi } from "./api-client/apis/UsersApi";
import { ImagesApi } from "./api-client/apis/ImagesApi";
import { ShareLinksApi } from "./api-client/apis/ShareLinksApi";
import { Configuration, type Middleware } from "./api-client/runtime";

function readCookie(name: string): string | undefined {
  const match = document.cookie.match(
    new RegExp(
      `(?:^|; )${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}=([^;]*)`,
    ),
  );
  return match ? decodeURIComponent(match[1]) : undefined;
}

/**
 * Adds the Django CSRF token to the request headers.
 */
const csrfMiddleware: Middleware = {
  async pre({ url, init }) {
    const token = readCookie("csrftoken");
    if (!token) return;
    const headers = new Headers(init.headers);
    headers.set("X-CSRFToken", token);
    return { url, init: { ...init, headers } };
  },
};

const config = new Configuration({
  basePath: "",
  middleware: [csrfMiddleware],
});

/**
 * This is a single entry point for all API clients.
 * It is used to avoid dupliation of configuration or middleware.
 */
export const Api = {
  users: new UsersApi(config),
  images: new ImagesApi(config),
  shareLinks: new ShareLinksApi(config),
};
