import { useState } from "react";
import type { ImageListItem } from "../api-client/models/ImageListItem";
import { SharePopover } from "./share";

type ImageGridItemProps = {
  item: ImageListItem;
  thumbMax: number;
  originalUrl: string | undefined;
  shareEnabled: boolean;
  onViewFull: (url: string) => void;
};

function ImageGridItem({
  item,
  thumbMax,
  originalUrl,
  shareEnabled,
  onViewFull,
}: ImageGridItemProps) {
  const [shareOpen, setShareOpen] = useState(false);

  return (
    <div className="flex flex-col items-center gap-2 justify-self-center">
      {originalUrl !== undefined ? (
        <button
          type="button"
          onClick={() => onViewFull(originalUrl)}
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
      <div className="relative flex justify-center">
        <button
          type="button"
          disabled={!shareEnabled}
          onClick={() => {
            if (shareEnabled) setShareOpen((o) => !o);
          }}
          aria-expanded={shareEnabled ? shareOpen : undefined}
          className="rounded-lg border border-slate-600 bg-transparent px-3 py-1 text-center text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label={shareEnabled ? "Share image" : "Share (Enterprise only)"}
        >
          Share
        </button>
        <SharePopover
          imageId={item.id}
          open={shareOpen}
          onClose={() => setShareOpen(false)}
        />
      </div>
    </div>
  );
}

export default ImageGridItem;
