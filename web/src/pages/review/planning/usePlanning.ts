import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import type { Planning } from "../../../types";
import { useReview } from "../useReview";

export function usePlanning() {
  const review = useReview();
  return useQuery({
    queryKey: ["planning", review.id],
    queryFn: () => api.get<Planning>(`/reviews/${review.id}/planning`),
  });
}

/** Mutation against the review's API that refreshes the planning data afterwards. */
export function usePlanningMutation<TArgs = void, TResult = unknown>(call: (base: string, args: TArgs) => Promise<TResult>) {
  const review = useReview();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (args: TArgs) => call(`/reviews/${review.id}`, args),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["planning", review.id] }),
  });
}
