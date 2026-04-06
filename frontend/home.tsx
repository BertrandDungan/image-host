import { useState } from "react";
import type { User } from "./api-client/models/User";
import { UserDebugModal } from "./users.tsx";

function Home() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userDebugOpen, setUserDebugOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-16">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800/80 bg-slate-900/40 p-10 shadow-xl shadow-black/20 backdrop-blur-sm">
        <div className="flex flex-wrap items-center justify-center gap-3">
          <h1 className="text-center text-3xl font-semibold tracking-tight text-slate-100 sm:text-4xl">
            {currentUser
              ? `Welcome ${currentUser.name}`
              : "Welcome to Image Host"}
          </h1>
          <button
            type="button"
            onClick={() => setUserDebugOpen(true)}
            className="shrink-0 rounded-lg border border-slate-700/80 bg-slate-900/50 px-3 py-1.5 text-xs font-medium text-slate-400 transition hover:border-slate-600 hover:bg-slate-800/60 hover:text-slate-200"
          >
            {currentUser ? "Select another user" : "Select a user"}
          </button>
          <UserDebugModal
            open={userDebugOpen}
            onClose={() => setUserDebugOpen(false)}
            setCurrentUser={setCurrentUser}
          />
        </div>
        <p className="mt-3 text-center text-sm text-slate-400">
          Cheap basic image hosting
        </p>
        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            type="button"
            disabled={!currentUser}
            className="rounded-lg border border-slate-600 bg-transparent px-5 py-2.5 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/60 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-slate-600 disabled:hover:bg-transparent"
          >
            View images
          </button>
          <button
            type="button"
            disabled={!currentUser}
            className="rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-sky-600"
          >
            Upload images
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
