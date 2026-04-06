import { useState } from "react";
import type { User } from "./api-client/models/User";

function Home() {
  const [currentUser] = useState<User | null>(null);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-16">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800/80 bg-slate-900/40 p-10 shadow-xl shadow-black/20 backdrop-blur-sm">
        <h1 className="text-center text-3xl font-semibold tracking-tight text-slate-100 sm:text-4xl">
          {currentUser ? `Welcome ${currentUser.name}` : "Please select a user"}
        </h1>
        <p className="mt-3 text-center text-sm text-slate-400">
          Your images, organized
        </p>
        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            type="button"
            className="rounded-lg border border-slate-600 bg-transparent px-5 py-2.5 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60"
          >
            View images
          </button>
          <button
            type="button"
            className="rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-sky-500"
          >
            Upload images
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
