import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal, Spinner, Table } from "react-bootstrap";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import ErrorAlert from "../../../components/ErrorAlert";
import type { Article } from "../../../types";
import { useReview } from "../useReview";

type Group = { articles: Article[] };

/** Lists groups found by DOI/title similarity; the chosen article stays, the rest become "Duplicado". */
export default function DuplicatesModal({ onHide }: { onHide: () => void }) {
  const review = useReview();
  const queryClient = useQueryClient();
  const [keep, setKeep] = useState<Record<number, number>>({});
  const find = useMutation({ mutationFn: () => api.post<Group[]>(`/reviews/${review.id}/articles/find-duplicates`) });
  const resolve = useMutation({
    mutationFn: (groups: Group[]) =>
      api.post<{ marked: number }>(`/reviews/${review.id}/articles/resolve-duplicates`, groups.map((group, index) => ({
        keep_id: keep[index] ?? group.articles[0].id,
        duplicate_ids: group.articles.map((article) => article.id),
      }))),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles", review.id] });
      find.mutate();
    },
  });

  // Search once when the modal opens.
  useEffect(() => { find.mutate(); }, []);

  const groups = find.data ?? [];

  return (
    <Modal show onHide={onHide} size="lg" scrollable>
      <Modal.Header closeButton><Modal.Title className="h6 mb-0">Encontrar duplicados</Modal.Title></Modal.Header>
      <Modal.Body>
        <ErrorAlert error={find.error ?? resolve.error} />
        {resolve.isSuccess && <Alert variant="success" className="py-2 small">{resolve.data.marked} estudo(s) marcados como duplicados.</Alert>}
        {find.isPending && <Spinner animation="border" />}
        {!find.isPending && groups.length === 0 && <p className="text-muted mb-0">Nenhum duplicado encontrado.</p>}
        {groups.map((group, index) => (
          <Table key={index} size="sm" bordered className="small align-middle">
            <thead>
              <tr><th style={{ width: 70 }}>Manter</th><th>Título</th><th>Fonte</th><th>Ano</th><th>DOI</th></tr>
            </thead>
            <tbody>
              {group.articles.map((article) => (
                <tr key={article.id}>
                  <td className="text-center">
                    <Form.Check type="radio" name={`keep-${index}`} aria-label={`Manter ${article.title}`}
                      checked={(keep[index] ?? group.articles[0].id) === article.id}
                      onChange={() => setKeep({ ...keep, [index]: article.id })} />
                  </td>
                  <td>{article.title}</td>
                  <td>{article.source?.name}</td>
                  <td>{article.year}</td>
                  <td>{article.doi}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        ))}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide}>Fechar</Button>
        <Button disabled={groups.length === 0 || resolve.isPending} onClick={() => resolve.mutate(groups)}>
          Marcar duplicados ({groups.reduce((total, group) => total + group.articles.length - 1, 0)})
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
