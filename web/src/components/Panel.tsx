import type { ReactNode } from "react";

type PanelProps = {
  title?: ReactNode;
  actions?: ReactNode;
  id?: string;
  className?: string;
  children: ReactNode;
};

export default function Panel({ title, actions, id, className = "", children }: PanelProps) {
  return (
    <section id={id} className={`panel mb-4 anchor-section ${className}`}>
      {title !== undefined && (
        <div className="panel-heading d-flex align-items-center justify-content-between gap-2">
          <span>{title}</span>
          {actions}
        </div>
      )}
      <div className="panel-body">{children}</div>
    </section>
  );
}
