interface StatusPanelProps {
  title: string
  message: string
  tone?: 'neutral' | 'error'
}

export function StatusPanel({
  title,
  message,
  tone = 'neutral',
}: StatusPanelProps) {
  const isError = tone === 'error'

  return (
    <section
      aria-live={isError ? 'assertive' : 'polite'}
      className={`rounded-2xl border p-6 ${
        isError
          ? 'border-danger/40 bg-danger-soft text-danger'
          : 'border-line bg-surface text-foreground'
      }`}
      role={isError ? 'alert' : 'status'}
    >
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-sm text-muted">{message}</p>
    </section>
  )
}
