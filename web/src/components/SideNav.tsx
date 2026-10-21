import { ListGroup } from "react-bootstrap";
import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

export type SideNavItem = { to: string; label: string; end?: boolean; children?: { href: string; label: string }[] };

/** Left navigation of Planning/Conducting; anchors under the active item mirror Parsifal's protocol page. */
export default function SideNav({ items, footer }: { items: SideNavItem[]; footer?: ReactNode }) {
  return (
    <div className="side-nav position-sticky" style={{ top: "1rem" }}>
      <ListGroup>
        {items.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end} className="list-group-item list-group-item-action">
            {({ isActive }) => (
              <>
                {item.label}
                {isActive && item.children && (
                  <div className="mt-2 small">
                    {item.children.map((child) => (
                      <a key={child.href} href={child.href} className="d-block text-reset text-decoration-none ps-2 py-1 opacity-75">
                        {child.label}
                      </a>
                    ))}
                  </div>
                )}
              </>
            )}
          </NavLink>
        ))}
      </ListGroup>
      {footer}
    </div>
  );
}
