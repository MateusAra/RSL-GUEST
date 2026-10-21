import type { ArticleStatus } from "../types";

export const STATUS_LABELS: Record<ArticleStatus, string> = {
  U: "Não classificado",
  A: "Aceito",
  R: "Rejeitado",
  D: "Duplicado",
};

const ICONS: Record<ArticleStatus, string> = {
  U: "bi-question-circle",
  A: "bi-check-circle",
  R: "bi-x-circle",
  D: "bi-files",
};

/** Status shown with icon + text + colour (never colour alone). */
export default function StatusBadge({ status }: { status: ArticleStatus }) {
  return (
    <span className={`badge status-${status}`}>
      <i className={`bi ${ICONS[status]} me-1`} />
      {STATUS_LABELS[status]}
    </span>
  );
}
