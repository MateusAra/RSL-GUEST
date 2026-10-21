import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import type { Code, CodingOverview } from "../../../types";
import { useReview } from "../useReview";

export function useCodes() {
  const review = useReview();
  return useQuery({ queryKey: ["synthesis", review.id, "codes"], queryFn: () => api.get<Code[]>(`/reviews/${review.id}/codes`) });
}

export function useCoding() {
  const review = useReview();
  return useQuery({ queryKey: ["synthesis", review.id, "coding"], queryFn: () => api.get<CodingOverview>(`/reviews/${review.id}/coding`) });
}

/** Mutation on the review's synthesis API; refreshes every synthesis query afterwards. */
export function useSynthesisMutation<TArgs = void, TResult = unknown>(call: (base: string, args: TArgs) => Promise<TResult>) {
  const review = useReview();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (args: TArgs) => call(`/reviews/${review.id}`, args),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["synthesis", review.id] }),
  });
}

export function codeNames(codes: Code[] | undefined): Map<number, string> {
  return new Map((codes ?? []).map((code) => [code.id, code.name]));
}
