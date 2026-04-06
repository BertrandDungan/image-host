import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import type { User } from "../api-client/models/User";
import { AccountTierEnum } from "../api-client/models/AccountTierEnum";
import {
  ImagesRetrieveImageSizeEnum,
  type ImagesRetrieveImageSizeEnum as ImageSizeEnum,
} from "../api-client/apis/ImagesApi";
import { Api } from "../api";
import type { ImageListItem } from "../api-client/models/ImageListItem";
import FullImage from "./fullImage";

type imageState = {
  smallThumbnails: ImageListItem[] | null;
  mediumThumbnails: ImageListItem[] | null;
  originals: ImageListItem[] | null;
};

function isHighTierAccount(user: User | null): boolean {
  return (
    user?.accountTier === AccountTierEnum.Premium ||
    user?.accountTier === AccountTierEnum.Enterprise
  );
}

function isEnterpriseAccount(user: User | null): boolean {
  return user?.accountTier === AccountTierEnum.Enterprise;
}

function GridView({ currentUser }: { currentUser: User | null }) {
  const [images, setImages] = useState<imageState>({
    smallThumbnails: null,
    mediumThumbnails: null,
    originals: null,
  });
  const [thumbnailSize, setThumbnailSize] = useState<"small" | "medium">(
    "small",
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [overlayVisible, setOverlayVisible] = useState(false);
  const closingRef = useRef(false);

  useEffect(() => {
    if (!currentUser) {
      setImages({
        smallThumbnails: null,
        mediumThumbnails: null,
        originals: null,
      });
      setThumbnailSize("small");
      setError(null);
      setLoading(false);
      return;
    }
    setImages({
      smallThumbnails: null,
      mediumThumbnails: null,
      originals: null,
    });
    setThumbnailSize("small");
    setError(null);
  }, [currentUser?.id]);

  // Load thumbnail image URLs for all user types
  useEffect(() => {
    if (!currentUser) return;

    const thumbnailKey: "smallThumbnails" | "mediumThumbnails" =
      thumbnailSize === "small" ? "smallThumbnails" : "mediumThumbnails";
    const cached = images[thumbnailKey];
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
          setImages((prev) => ({
            ...prev,
            [thumbnailKey]: res.items,
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
    images.smallThumbnails,
    images.mediumThumbnails,
  ]);

  // Load original image URLs for high-tier accounts
  useEffect(() => {
    if (!currentUser) return;
    if (!isHighTierAccount(currentUser)) return;
    if (images.originals !== null) return;
    if (images.smallThumbnails === null && images.mediumThumbnails === null)
      return;

    let cancelled = false;
    Api.images
      .imagesRetrieve({
        imageSize: ImagesRetrieveImageSizeEnum.Original,
        userId: currentUser.id,
      })
      .then((res) => {
        if (!cancelled) {
          setImages((prev) => ({
            ...prev,
            originals: res.items,
          }));
        }
      })
      .catch(() => {
        if (!cancelled) {
          console.error("Could not load original image URLs");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [
    currentUser?.id,
    images.smallThumbnails,
    images.mediumThumbnails,
    images.originals,
  ]);

  // Handle full image overlay animations
  useEffect(() => {
    if (!viewerUrl) {
      setOverlayVisible(false);
      return;
    }
    closingRef.current = false;
    const id = requestAnimationFrame(() => setOverlayVisible(true));
    return () => cancelAnimationFrame(id);
  }, [viewerUrl]);

  // Add keyboard escape so full image overlay is accessible via only keyboard
  useEffect(() => {
    if (!viewerUrl) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        closingRef.current = true;
        setOverlayVisible(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [viewerUrl]);

  const displayUrls =
    thumbnailSize === "small"
      ? images.smallThumbnails
      : images.mediumThumbnails;

  const premiumToggle = isHighTierAccount(currentUser);
  const shareEnabled = isEnterpriseAccount(currentUser);

  function dismissViewer() {
    closingRef.current = true;
    setOverlayVisible(false);
  }

  function handleOverlayTransitionEnd(
    e: React.TransitionEvent<HTMLDivElement>,
  ) {
    if (e.propertyName !== "opacity") return;
    if (closingRef.current) {
      closingRef.current = false;
      setViewerUrl(null);
    }
  }

  const thumbMax = thumbnailSize === "small" ? 200 : 400;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-16">
      {viewerUrl !== null && (
        <div
          role="presentation"
          className={`fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-md transition-opacity duration-200 ease-out ${
            overlayVisible ? "opacity-100" : "opacity-0"
          }`}
          onClick={dismissViewer}
          onTransitionEnd={handleOverlayTransitionEnd}
        >
          <FullImage key={viewerUrl} url={viewerUrl} />
        </div>
      )}

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
              {displayUrls.map((item, index) => {
                const originalUrl = images.originals?.[index]?.url;

                return (
                  <div
                    key={item.id}
                    className="flex flex-col items-center gap-2 justify-self-center"
                  >
                    {originalUrl !== undefined ? (
                      <button
                        type="button"
                        onClick={() => setViewerUrl(originalUrl)}
                        className="h-auto w-auto max-w-full cursor-pointer rounded-lg border border-slate-800/80 object-contain p-0 transition hover:border-slate-600"
                        style={{
                          maxWidth: thumbMax,
                          maxHeight: thumbMax,
                        }}
                        aria-label="View full-size image"
                      >
                        <img
                          src={item.url}
                          alt=""
                          loading="lazy"
                          className="h-auto max-h-full w-auto max-w-full rounded-lg object-contain"
                          style={{
                            maxWidth: thumbMax,
                            maxHeight: thumbMax,
                          }}
                        />
                      </button>
                    ) : (
                      <img
                        src={item.url}
                        alt=""
                        loading="lazy"
                        className="h-auto w-auto max-w-full rounded-lg border border-slate-800/80 object-contain"
                        style={{
                          maxWidth: thumbMax,
                          maxHeight: thumbMax,
                        }}
                      />
                    )}
                    <button
                      type="button"
                      disabled={!shareEnabled}
                      className="rounded-lg border border-slate-600 bg-transparent px-3 py-1 text-center text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60 disabled:cursor-not-allowed disabled:opacity-40"
                      aria-label={
                        shareEnabled ? "Share image" : "Share (Enterprise only)"
                      }
                    >
                      Share
                    </button>
                  </div>
                );
              })}
            </div>
          )}
      </div>
    </div>
  );
}

export default GridView;
