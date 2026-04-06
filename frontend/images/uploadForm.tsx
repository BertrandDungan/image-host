import { useRef, useState, type ChangeEvent, type FormEvent } from "react";
import { Link } from "react-router";
import type { User } from "../api-client/models/User";
import { FetchError, ResponseError } from "../api-client/runtime";
import { Api } from "../api";

const ACCEPT =
  ".png,.jpg,.jpeg,image/png,image/jpeg" as const;

const ALLOWED_MIME = new Set(["image/png", "image/jpeg"]);

function allowedFile(file: File): boolean {
  if (ALLOWED_MIME.has(file.type)) return true;
  const lower = file.name.toLowerCase();
  return lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg");
}

function formatUploadErrorBody(body: unknown): string {
  if (body === null || body === undefined) return "Upload failed.";
  if (typeof body === "object" && body !== null && "detail" in body) {
    const d = (body as { detail?: unknown }).detail;
    if (typeof d === "string" && d.trim()) return d;
  }
  try {
    return JSON.stringify(body);
  } catch {
    return "Upload failed.";
  }
}

async function messageFromResponseError(err: ResponseError): Promise<string> {
  let body: unknown;
  try {
    body = await err.response.json();
  } catch {
    return `Upload failed (${err.response.status}).`;
  }
  return formatUploadErrorBody(body);
}

function UploadForm({ currentUser }: { currentUser: User | null }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  function clearStatus() {
    setError(null);
    setSuccess(false);
  }

  function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    clearStatus();
    const f = e.target.files?.[0] ?? null;
    if (!f) {
      setFile(null);
      return;
    }
    if (!allowedFile(f)) {
      setFile(null);
      setError("Only PNG or JPEG files are allowed.");
      e.target.value = "";
      return;
    }
    setFile(f);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!currentUser || !file) return;
    clearStatus();
    setUploading(true);
    try {
      await Api.images.imagesUpdate({
        userId: currentUser.id,
        filename: file.name,
        image: file,
      });
      setSuccess(true);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      if (err instanceof ResponseError) {
        setError(await messageFromResponseError(err));
      } else if (err instanceof FetchError) {
        setError("Network error. Check your connection and try again.");
      } else {
        setError("Upload failed.");
      }
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-16">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800/80 bg-slate-900/40 p-10 shadow-xl shadow-black/20 backdrop-blur-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
            Upload images
          </h1>
          <Link
            to="/"
            className="shrink-0 rounded-lg border border-slate-600 bg-transparent px-5 py-2.5 text-center text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60"
          >
            Back
          </Link>
        </div>

        {!currentUser && (
          <p className="mt-8 text-center text-sm text-slate-400">
            Select a user on the home page to upload images.
          </p>
        )}

        {currentUser && (
          <form className="mt-8 flex flex-col gap-6" onSubmit={onSubmit}>
            <div>
              <label
                htmlFor="image-file"
                className="block text-sm font-medium text-slate-300"
              >
                Image file (PNG or JPEG)
              </label>
              <input
                ref={inputRef}
                id="image-file"
                name="image"
                type="file"
                accept={ACCEPT}
                disabled={uploading}
                onChange={onFileChange}
                className="mt-2 block w-full text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:text-sm file:font-medium file:text-slate-200 hover:file:bg-slate-700 disabled:opacity-50"
              />
            </div>

            <button
              type="submit"
              disabled={!file || uploading}
              className="rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-sky-600"
            >
              {uploading ? "Uploading…" : "Upload"}
            </button>
          </form>
        )}

        {error && (
          <p className="mt-6 text-sm text-red-400" role="alert">
            {error}
          </p>
        )}
        {success && !error && (
          <p className="mt-6 text-sm text-emerald-400" role="status">
            Image uploaded successfully.
          </p>
        )}
      </div>
    </div>
  );
}

export default UploadForm;
