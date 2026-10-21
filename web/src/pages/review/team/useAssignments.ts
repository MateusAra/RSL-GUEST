import { useQuery } from "@tanstack/react-query";
import { api } from "../../../api";
import { useAuth } from "../../../auth";
import type { Assignments, Stage } from "../../../types";
import { useReview } from "../useReview";

export const STAGE_LABELS: Record<Stage, string> = {
  selection: "Seleção",
  quality: "Avaliação de qualidade",
  extraction: "Extração",
  coding: "Codificação",
};

export function useAssignments(stage: Stage) {
  const review = useReview();
  return useQuery({
    queryKey: ["assignments", review.id, stage],
    queryFn: () => api.get<Assignments>(`/reviews/${review.id}/assignments?stage=${stage}`),
  });
}

/** Ids of the articles assigned to the current user in a stage (undefined while loading). */
export function useMyAssignments(stage: Stage): Set<number> | undefined {
  const { user } = useAuth();
  const assignments = useAssignments(stage);
  if (!assignments.data || !user) return undefined;
  return new Set(Object.entries(assignments.data.assignments)
    .filter(([, value]) => value.user_id === user.id).map(([articleId]) => Number(articleId)));
}
