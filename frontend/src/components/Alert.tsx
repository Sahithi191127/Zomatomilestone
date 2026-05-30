type AlertKind = "error" | "warning" | "info";

interface AlertProps {
  kind: AlertKind;
  title: string;
  body: string;
  onRetry?: () => void;
}

export function Alert({ kind, title, body, onRetry }: AlertProps) {
  return (
    <div className={`tp-alert tp-alert-${kind}`}>
      <strong>{title}</strong>
      <p>{body}</p>
      {onRetry && (
        <button type="button" className="tp-btn-primary" style={{ marginTop: "0.75rem" }} onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
