export function Loading({ label = "Loading your adventure…" }: { label?: string }) {
  return (
    <div role="status" className="flex min-h-[50dvh] flex-col items-center justify-center gap-3 text-sand-dim">
      <span aria-hidden className="size-8 animate-spin rounded-full border-4 border-canopy-2 border-t-ember" />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function ErrorNote({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="rounded-card border border-ember/40 bg-canopy p-4">
      <p className="font-semibold">Hmm, that didn&apos;t work.</p>
      <p className="mt-1 text-sm text-sand-dim">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-secondary mt-4 w-full">
          Try again
        </button>
      )}
    </div>
  );
}
