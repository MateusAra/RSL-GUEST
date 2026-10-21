import { useQuery } from "@tanstack/react-query";
import { useOutletContext, useParams } from "react-router-dom";
import { api } from "../../api";
import type { ReviewSummary } from "../../types";

export function useReviewQuery() {
  const { reviewId } = useParams();
  return useQuery({
    queryKey: ["review", reviewId],
    queryFn: () => api.get<ReviewSummary>(`/reviews/${reviewId}`),
  });
}

/** The current review, provided by ReviewLayout to its nested pages. */
export function useReview(): ReviewSummary {
  return useOutletContext<ReviewSummary>();
}
