import { useEffect, useState, type Dispatch, type SetStateAction } from "react";
import type { User } from "./api-client/models/User";
import { Api } from "./api";

export function UserDebugModal({
  open,
  onClose,
  setCurrentUser,
}: {
  open: boolean;
  onClose: () => void;
  setCurrentUser: Dispatch<SetStateAction<User | null>>;
}) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setError(null);
    Api.users
      .usersList()
      .then((list) => {
        setUsers(list);
      })
      .catch(() => {
        setError("Could not load users");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 py-8 backdrop-blur-sm"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="user-debug-title"
        className="max-h-[min(90vh,640px)] w-full max-w-3xl overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/95 shadow-xl shadow-black/20"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-slate-800/80 px-6 py-4">
          <h2
            id="user-debug-title"
            className="text-lg font-semibold tracking-tight text-slate-100"
          >
            User debug menu
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-600 bg-transparent px-3 py-1.5 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:bg-slate-800/60"
          >
            Close
          </button>
        </div>
        <div className="overflow-auto p-6">
          {loading && <p className="text-sm text-slate-400">Loading users…</p>}
          {error && !loading && <p className="text-sm text-red-400">{error}</p>}
          {!loading && !error && users.length === 0 && (
            <p className="text-center text-sm text-slate-500">
              No users, run `python manage.py seed` to create test users.
            </p>
          )}
          {!loading && !error && users.length > 0 && (
            <div className="overflow-x-auto rounded-xl border border-slate-800/80">
              <table className="w-full min-w-[400px] border-collapse text-left text-sm text-slate-200">
                <thead>
                  <tr className="border-b border-slate-800/80 bg-slate-950/50">
                    <th className="px-4 py-3 font-medium text-slate-400">
                      Name
                    </th>
                    <th className="px-4 py-3 font-medium text-slate-400">
                      Account tier
                    </th>
                    <th className="px-4 py-3 font-medium text-slate-400">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr
                      key={u.id}
                      className="border-b border-slate-800/60 last:border-0"
                    >
                      <td className="px-4 py-3 text-slate-100">{u.name}</td>
                      <td className="px-4 py-3 text-slate-300">
                        {u.accountTier}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          onClick={() => {
                            setCurrentUser(u);
                            onClose();
                          }}
                          className="rounded-lg bg-sky-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition hover:bg-sky-500"
                        >
                          Set user
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
