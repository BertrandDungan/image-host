import { useEffect, useState } from "react";
import { Link } from "react-router";
import type { User } from "../api-client/models/User";
import { AccountTierEnum } from "../api-client/models/AccountTierEnum";
import {
  ImagesRetrieveImageSizeEnum,
  type ImagesRetrieveImageSizeEnum as ImageSizeEnum,
} from "../api-client/apis/ImagesApi";
import { Api } from "../api";

type ThumbnailSize = "small" | "medium";

type UrlsState = {
  smallThumbnails: string[] | null;
  mediumThumbnails: string[] | null;
};

function canUseMediumThumbnails(user: User | null): boolean {
  if (!user) return false;
  return (
    user.accountTier === AccountTierEnum.Premium ||
    user.accountTier === AccountTierEnum.Enterprise
  );
}

function GridView({ currentUser }: { currentUser: User | null }) {
  const [urls, setUrls] = useState<UrlsState>({
    smallThumbnails: null,
    mediumThumbnails: null,
  });
  const [thumbnailSize, setThumbnailSize] = useState<ThumbnailSize>("small");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentUser) {
      setUrls({ smallThumbnails: null, mediumThumbnails: null });
      setThumbnailSize("small");
      setError(null);
      setLoading(false);
      return;
    }
    setUrls({ smallThumbnails: null, mediumThumbnails: null });
    setThumbnailSize("small");
    setError(null);
  }, [currentUser?.id]);

  useEffect(() => {
    if (!currentUser) return;

    const thumbnailKey: keyof UrlsState =
      thumbnailSize === "small" ? "smallThumbnails" : "mediumThumbnails";
    const cached = urls[thumbnailKey];
    if (cached !== null) {
      setLoading(false);
      return;
    }

    const imageSize: ImageSizeEnum =
      thumbnailSize === "small"
        ? ImagesRetrieveImageSizeEnum._200
        : ImagesRetrieveImageSizeEnum._400;

    let cancelled = false;
    setLoading(true);
    setError(null);
    Api.images
      .imagesRetrieve({
        imageSize,
        userId: currentUser.id,
      })
      .then((res) => {
        if (!cancelled) {
          setUrls((prev) => ({
            ...prev,
            [thumbnailKey]: res.urls,
          }));
        }
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
  }, [
    currentUser?.id,
    thumbnailSize,
    urls.smallThumbnails,
    urls.mediumThumbnails,
  ]);

  const displayUrls =
    thumbnailSize === "small" ? urls.smallThumbnails : urls.mediumThumbnails;

  const premiumToggle = canUseMediumThumbnails(currentUser);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-16">
      <div className="w-full max-w-3xl rounded-2xl border border-slate-800/80 bg-slate-900/40 p-10 shadow-xl shadow-black/20 backdrop-blur-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
            Your images
          </h1>
          <div className="flex flex-wrap items-center gap-3">
            {currentUser && (
              <button
                type="button"
                disabled={!premiumToggle}
                onClick={() =>
                  setThumbnailSize((s) => (s === "small" ? "medium" : "small"))
                }
                className="shrink-0 rounded-lg border border-slate-600 bg-transparent px-4 py-2 text-center text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60 disabled:cursor-not-allowed disabled:opacity-40"
                aria-label={
                  thumbnailSize === "small"
                    ? "Switch to medium thumbnails"
                    : "Switch to small thumbnails"
                }
              >
                {thumbnailSize === "small"
                  ? "Switch to medium thumbnails (400px)"
                  : "Switch to small thumbnails (200px)"}
              </button>
            )}
            <Link
              to="/"
              className="shrink-0 rounded-lg border border-slate-600 bg-transparent px-5 py-2.5 text-center text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60"
            >
              Back
            </Link>
          </div>
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
        {currentUser &&
          !loading &&
          !error &&
          displayUrls !== null &&
          displayUrls.length === 0 && (
            <p className="mt-8 text-center text-sm text-slate-500">
              No images yet for this user.
            </p>
          )}
        {currentUser &&
          !loading &&
          !error &&
          displayUrls !== null &&
          displayUrls.length > 0 && (
            <div
              className="mt-8 grid gap-4"
              style={{
                gridTemplateColumns: `repeat(auto-fill, minmax(min(100%, ${thumbnailSize === "small" ? 200 : 400}px), 1fr))`,
              }}
            >
              {displayUrls.map((url) => (
                <img
                  key={url}
                  src={url}
                  loading="lazy"
                  className="h-auto w-auto max-w-full justify-self-center rounded-lg border border-slate-800/80 object-contain"
                  style={{
                    maxWidth: thumbnailSize === "small" ? 200 : 400,
                    maxHeight: thumbnailSize === "small" ? 200 : 400,
                  }}
                />
              ))}
            </div>
          )}
      </div>
    </div>
  );
}

export default GridView;
