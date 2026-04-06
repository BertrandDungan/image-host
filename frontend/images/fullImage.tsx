export default function FullImage({ url }: { url: string }) {
  return (
    <img
      src={url}
      alt=""
      className="h-auto max-h-[90vh] w-auto max-w-[90vw] object-contain"
    />
  );
}
