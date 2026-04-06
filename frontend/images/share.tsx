import { useEffect, useRef, useState, type FormEvent } from "react";
import { FetchError, ResponseError } from "../api-client/runtime";
import { Api } from "../api";

const MIN_SECONDS = 300;
const MAX_SECONDS = 30000;
const DEFAULT_SECONDS = 3600;

function formatErrorBody(body: unknown): string {
  if (body === null || body === undefined)
    return "Could not create share link.";
  if (typeof body === "object" && body !== null && "detail" in body) {
    const d = (body as { detail?: unknown }).detail;
    if (typeof d === "string" && d.trim()) return d;
  }
  try {
    return JSON.stringify(body);
  } catch {
    return "Could not create share link.";
  }
}

async function messageFromResponseError(err: ResponseError): Promise<string> {
  let body: unknown;
  try {
    body = await err.response.json();
  } catch {
    return `Could not create share link (${err.response.status}).`;
  }
  return formatErrorBody(body);
}

type SharePopoverProps = {
  imageId: number;
  open: boolean;
  onClose: () => void;
};

export function SharePopover({ imageId, open, onClose }: SharePopoverProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [expirySeconds, setExpirySeconds] = useState(String(DEFAULT_SECONDS));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdUrl, setCreatedUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setError(null);
    setCreatedUrl(null);
    setExpirySeconds(String(DEFAULT_SECONDS));
  }, [open, imageId]);

  // Close popover when user clicks anywhere outside it
  useEffect(() => {
    if (!open) return;
    function onDocMouseDown(e: globalThis.MouseEvent) {
      const el = panelRef.current;
      const t = e.target;
      if (!el || !(t instanceof Node) || el.contains(t)) return;
      onClose();
    }
    document.addEventListener("mousedown", onDocMouseDown);
    return () => document.removeEventListener("mousedown", onDocMouseDown);
  }, [open, onClose]);

  // Close popover via keyboard escape for accessibility
  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const formSeconds = Number.parseInt(expirySeconds, 10);
    setError(null);
    setLoading(true);
    try {
      const res = await Api.shareLinks.shareLinksCreate({
        shareLinkCreate: { image: imageId, expirySeconds: formSeconds },
      });
      setCreatedUrl(res.url);
    } catch (err) {
      if (err instanceof ResponseError) {
        setError(await messageFromResponseError(err));
      } else if (err instanceof FetchError) {
        setError("Network error. Check your connection and try again.");
      } else {
        setError("Could not create share link.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      ref={panelRef}
      role="dialog"
      aria-label="Create share link"
      className="absolute left-1/2 top-full z-50 mt-2 min-w-[min(100vw-2rem,18rem)] max-w-[min(100vw-2rem,22rem)] -translate-x-1/2 rounded-lg border border-slate-800/80 bg-slate-900/95 p-4 shadow-lg shadow-black/40"
    >
      {createdUrl === null ? (
        <form className="flex flex-col gap-3" onSubmit={onSubmit}>
          <label className="flex flex-col gap-1.5 text-xs text-slate-300">
            <span>Link expires after (seconds)</span>
            <input
              type="number"
              name="expirySeconds"
              min={MIN_SECONDS}
              max={MAX_SECONDS}
              required
              value={expirySeconds}
              onChange={(e) => setExpirySeconds(e.target.value)}
              className="rounded-md border border-slate-600 bg-slate-950/80 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
            />
            <span className="text-[11px] font-normal text-slate-500">
              Between {MIN_SECONDS} and {MAX_SECONDS} seconds.
            </span>
          </label>
          {error !== null && (
            <p className="text-xs text-red-400" role="alert">
              {error}
            </p>
          )}
          <div className="flex flex-wrap justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-600 bg-transparent px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg border border-slate-600 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-100 transition hover:bg-slate-700/80 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Creating…" : "Create link"}
            </button>
          </div>
        </form>
      ) : (
        <div className="flex flex-col gap-3">
          <p className="text-xs text-slate-300">Share link:</p>
          <a
            href={createdUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="break-all text-xs text-sky-400 underline decoration-sky-500/50 underline-offset-2 hover:text-sky-300"
          >
            {createdUrl}
          </a>
          <div className="flex justify-end">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-600 bg-transparent px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
