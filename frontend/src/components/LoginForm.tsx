"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { useAuth } from "@/components/AuthProvider";

export const LoginForm = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState("user");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--surface)] px-4 py-12">
      <div className="w-full max-w-md rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
        <h1 className="text-2xl font-semibold text-[var(--navy-dark)]">Sign in</h1>
        <p className="mt-2 text-sm text-[var(--gray-text)]">Use user / password to enter the Kanban board.</p>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="text-sm font-semibold text-[var(--gray-text)]">Username</span>
            <input
              className="mt-2 w-full rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 outline-none"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              type="text"
              aria-label="Username"
            />
          </label>

          <label className="block">
            <span className="text-sm font-semibold text-[var(--gray-text)]">Password</span>
            <input
              className="mt-2 w-full rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 outline-none"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              type="password"
              aria-label="Password"
            />
          </label>

          {error ? (
            <p className="text-sm text-red-600">{error}</p>
          ) : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-2xl bg-[var(--primary-blue)] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[var(--navy-dark)] disabled:opacity-50"
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
};
