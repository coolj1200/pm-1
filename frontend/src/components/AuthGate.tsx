"use client";

import { useAuth } from "@/components/AuthProvider";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";

export const AuthGate = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--surface)] text-[var(--navy-dark)]">
        Checking authentication...
      </div>
    );
  }

  if (!user) {
    return <LoginForm />;
  }

  return <KanbanBoard />;
};
