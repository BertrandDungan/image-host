import { useEffect, useState } from "react";
import { Link } from "react-router";
import type { User } from "../api-client/models/User";
import { ImagesRetrieveImageSizeEnum } from "../api-client/apis/ImagesApi";
import { Api } from "../api";

function GridView({ currentUser }: { currentUser: User | null }) {
  const [urls, setUrls] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentUser) {
      setUrls([]);
      setError(null);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    Api.images
      .imagesRetrieve({
        imageSize: ImagesRetrieveImageSizeEnum._200,
        userId: currentUser.id,
      })
      .then((res) => {
        if (!cancelled) setUrls(res.urls);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load images");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [currentUser?.id]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-16">
      <div className="w-full max-w-3xl rounded-2xl border border-slate-800/80 bg-slate-900/40 p-10 shadow-xl shadow-black/20 backdrop-blur-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
            Your images
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
            Select a user to view their images.
          </p>
        )}

        {currentUser && loading && (
          <p className="mt-8 text-sm text-slate-400">Loading images…</p>
        )}
        {currentUser && error && !loading && (
          <p className="mt-8 text-sm text-red-400">{error}</p>
        )}
        {currentUser && !loading && !error && urls.length === 0 && (
          <p className="mt-8 text-center text-sm text-slate-500">
            No images yet for this user.
          </p>
        )}
        {currentUser && !loading && !error && urls.length > 0 && (
          <div className="mt-8 grid grid-cols-1 gap-4">
            {urls.map((url) => (
              <img
                key={url}
                src={url}
                loading="lazy"
                className="w-full max-w-full rounded-lg border border-slate-800/80 object-contain"
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default GridView;
