import { Badge, Button, Dropdown } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import type { NotificationRow } from "../types";

type Inbox = { unread: number; items: NotificationRow[] };

/** In-app notifications (no e-mail): refreshed every 30 s. */
export default function NotificationBell() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const inbox = useQuery({ queryKey: ["notifications"], queryFn: () => api.get<Inbox>("/notifications"), refetchInterval: 30_000 });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["notifications"] });
  const read = useMutation({ mutationFn: (id: number) => api.post(`/notifications/${id}/read`), onSuccess: refresh });
  const readAll = useMutation({ mutationFn: () => api.post("/notifications/read-all"), onSuccess: refresh });
  const unread = inbox.data?.unread ?? 0;

  return (
    <Dropdown align="end" className="me-2">
      <Dropdown.Toggle variant="link" className="text-white text-decoration-none" aria-label={`Notificações (${unread} não lidas)`}>
        <i className="bi bi-bell" />
        {unread > 0 && <Badge bg="danger" pill className="ms-1">{unread}</Badge>}
      </Dropdown.Toggle>
      <Dropdown.Menu style={{ width: 340, maxHeight: 420, overflowY: "auto" }}>
        <div className="d-flex justify-content-between align-items-center px-3 py-1">
          <strong className="small">Notificações</strong>
          <Button size="sm" variant="link" className="p-0" disabled={unread === 0} onClick={() => readAll.mutate()}>Marcar todas como lidas</Button>
        </div>
        <Dropdown.Divider />
        {inbox.data?.items.length === 0 && <div className="px-3 small text-muted">Nada por aqui.</div>}
        {inbox.data?.items.map((item) => (
          <Dropdown.Item key={item.id} className={`small text-wrap ${item.read ? "text-muted" : "fw-semibold"}`}
            onClick={() => { if (!item.read) read.mutate(item.id); if (item.link) navigate(item.link); }}>
            {item.message}
            <div className="text-muted fw-normal" style={{ fontSize: "0.75rem" }}>{new Date(item.created_at).toLocaleString("pt-BR")}</div>
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
}
