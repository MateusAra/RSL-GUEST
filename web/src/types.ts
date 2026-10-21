export type UserPublic = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
};

export type Me = UserPublic & { email: string; created_at: string };

export type ReviewSummary = {
  id: number;
  name: string;
  title: string;
  description: string;
  author: UserPublic;
  co_authors: UserPublic[];
  is_owner: boolean;
  created_at: string;
  updated_at: string;
};

export type Invite = {
  id: number;
  code: string;
  review: { id: number; title: string };
  invited_by: UserPublic;
  invitee_email: string;
  status: "pending" | "accepted" | "rejected";
  date_sent: string;
  date_answered: string | null;
};

export type Activity = { user: UserPublic; verb: string; target: string; created_at: string };

export type Picoc = { population: string; intervention: string; comparison: string; outcome: string; context: string };
export type KeywordRow = { id: number; description: string; related_to: "" | "P" | "I" | "C" | "O"; synonyms: { id: number; description: string }[] };
export type SourceRow = { id: number; name: string; url: string };
export type DescriptionRow = { id: number; description: string };
export type ExtractionField = {
  id: number;
  description: string;
  field_type: "B" | "S" | "F" | "I" | "D" | "O" | "M";
  field_type_label: string;
  order: number;
  lookups: { id: number; value: string }[];
};

export type Planning = {
  objective: string;
  picoc: Picoc;
  questions: { id: number; question: string; order: number }[];
  keywords: KeywordRow[];
  search_string: string;
  sources: SourceRow[];
  inclusion_criteria: DescriptionRow[];
  exclusion_criteria: DescriptionRow[];
  quality_questions: (DescriptionRow & { order: number })[];
  quality_answers: (DescriptionRow & { weight: number })[];
  quality_max_score: number;
  quality_cutoff_score: number;
  data_extraction_fields: ExtractionField[];
  field_types: Record<ExtractionField["field_type"], string>;
};

export type ArticleStatus = "U" | "A" | "R" | "D";
export type Article = {
  id: number;
  bibtex_key: string;
  title: string;
  author: string;
  journal: string;
  year: string;
  pages: string;
  volume: string;
  abstract: string;
  document_type: string;
  doi: string;
  url: string;
  affiliation: string;
  author_keywords: string;
  keywords: string;
  publisher: string;
  issn: string;
  language: string;
  note: string;
  source: { id: number; name: string } | null;
  status: ArticleStatus;
  status_label: string;
  comments: string;
  selection_criteria_id: number | null;
  finished_data_extraction: boolean;
  created_at: string;
  updated_at: string;
};
export type ArticleList = {
  items: Article[];
  total: number;
  page: number;
  page_size: number;
  ids: number[];
  status_counts: Record<ArticleStatus, number>;
  source_counts: Record<string, number>;
};
export type SearchInfo = {
  base_string: string;
  sources: { source: SourceRow; search_string: string; version: number }[];
};
export type ImportSummary = {
  source: { id: number; name: string };
  articles: number;
  files: { id: number; file_name: string; imported_count: number; created_at: string }[];
}[];

export type ArticleBrief = {
  id: number;
  title: string;
  author: string;
  year: string;
  journal: string;
  source: string | null;
  finished_data_extraction: boolean;
};
export type QualityAssessmentData = {
  questions: { id: number; description: string }[];
  answers: { id: number; description: string; weight: number }[];
  max_score: number;
  cutoff_score: number;
  articles: (ArticleBrief & { answers: Record<string, number>; score: number; complete: boolean; passed: boolean })[];
};
export type ExtractionValue = string | number | number[] | null;
export type DataExtractionData = {
  fields: { id: number; description: string; field_type: ExtractionField["field_type"]; lookups: { id: number; value: string }[] }[];
  articles: (ArticleBrief & { values: Record<string, ExtractionValue> })[];
};
export type AnalysisData = {
  per_source: { source: string; total: number; accepted: number }[];
  status_totals: Record<ArticleStatus, number>;
  final_per_year: { year: string; count: number }[];
  final_total: number;
};

export type Code = {
  id: number;
  name: string;
  definition: string;
  limits: string;
  kind: "deductive" | "emergent";
  kind_label: string;
  status: "draft" | "active" | "merged" | "removed";
  status_label: string;
  origin_field_id: number | null;
  origin_lookup_id: number | null;
  merged_into_id: number | null;
  created_by_id: number | null;
  segments: number;
};
export type CodeEvent = {
  sequence: number;
  code_id: number | null;
  action: string;
  previous: Record<string, unknown> | null;
  new: Record<string, unknown> | null;
  justification: string;
  user: string | null;
  created_at: string;
};
export type CodingSettings = {
  dual_enabled: boolean;
  sample_percent: number;
  coder_a_id: number | null;
  coder_b_id: number | null;
  codebook_verified_by_id: number | null;
  codebook_verified_at: string | null;
  closed_at: string | null;
  close_justification: string;
  sample: { article_id: number; coder_a_done: boolean; coder_b_done: boolean }[];
};
export type CodingOverview = {
  settings: CodingSettings;
  my_slot: "a" | "b" | null;
  articles: { id: number; title: string; author: string; year: string; segments: number; in_sample: boolean }[];
};
export type SegmentRow = {
  id: number;
  article_id: number;
  text: string;
  page: string;
  created_by_id: number | null;
  codes: { final: number[]; mine?: number[]; coder_a?: number[]; coder_b?: number[] };
};
export type Agreement = {
  enabled: boolean;
  articles_done: number;
  segments: number;
  agreed_segments: number;
  alpha: number | null;
  kappa: number | null;
  metric: "alpha" | "kappa";
  value: number | null;
  threshold: number;
  below_threshold: boolean;
  divergences: { segment_id: number; article_id: number; text: string; page: string; coder_a: number[]; coder_b: number[]; final: number[]; resolved: boolean }[];
};
export type ThemeRow = {
  id: number;
  name: string;
  description: string;
  parent_id: number | null;
  codes: (Code & { justification: string; evidence: { id: number; text: string; page: string; article_id: number; article_title: string }[] })[];
};
export type SynthesisChecklist = {
  items: { item: number; text: string; met: boolean | null; justification: string }[];
  evaluated: boolean;
};

export type Hypothesis = {
  id: number;
  code: string;
  statement: string;
  independent_variables: string;
  dependent_variables: string;
  operational_criteria: string;
  order: number;
};
export type VerdictKey = "supports" | "partial" | "refutes" | "inconclusive";
export type Verdicts = Record<string, Record<string, { verdict: VerdictKey; justification: string }>>;
export type Ranked = { label: string; count: number }[];
export type InsightFilters = {
  min_quality_pct: number | null;
  year_from: number | null;
  year_to: number | null;
  source_ids: number[];
  categories: string[];
};
export type AnalysisWeighting = {
  high_min_pct: number;
  high_weight: number;
  moderate_min_pct: number;
  moderate_weight: number;
  author_concentration_pct: number;
};
export type HypothesisSynthesis = {
  id: number;
  code: string;
  statement: string;
  rated: number;
  missing: number;
  verdicts: { verdict: VerdictKey; label: string; count: number; pct: number; weighted: number; weighted_pct: number; moderate_band: number }[];
};
export type Insights = {
  filters: InsightFilters;
  settings: AnalysisWeighting;
  corpus: number;
  final_total: number;
  quality_bands: Record<"high" | "moderate" | "low" | "none", number>;
  bibliometrics: {
    per_year: Ranked;
    per_source: Ranked;
    per_venue: Ranked;
    per_category: Ranked;
    top_keywords: Ranked;
    top_authors: Ranked;
    coauthor_pairs: Ranked;
    author_concentration: { author: string; count: number; pct: number }[];
  };
  fields: { field_id: number; field: string; field_type: string; values: Ranked; unanswered: number }[];
  hypotheses: HypothesisSynthesis[];
  comparison?: { corpus: number; hypotheses: HypothesisSynthesis[] };
};
export type Crosstab = { field_a: string; field_b: string; rows: string[]; columns: string[]; matrix: number[][]; corpus: number };
export type Snapshot = {
  id: number;
  label: string;
  filters: InsightFilters;
  settings: AnalysisWeighting;
  created_by_id: number | null;
  created_at: string;
  corpus: number;
  results?: Insights;
};

export type Stage = "selection" | "quality" | "extraction" | "coding";
export type Assignments = { stage: Stage; assignments: Record<string, { user_id: number; user: UserPublic | null }> };
export type CommentRow = { id: number; user: UserPublic | null; body: string; is_resolution: boolean; resolution_status: string | null; created_at: string };
export type NotificationRow = { id: number; kind: string; message: string; link: string; review_id: number | null; read: boolean; created_at: string };
export type Dashboard = {
  selection: Record<ArticleStatus, number>;
  quality: { accepted: number; complete: number; incomplete: number };
  extraction: { final: number; finished: number };
  coding: { studies_coded: number; final: number; segments: number; agreement: number | null; agreement_metric: string; agreement_threshold: number };
  members: { user: UserPublic; stages: Partial<Record<Stage, { assigned: number; pending: number }>> }[];
};
export type EvidenceChain = {
  question_id: number;
  question: string;
  conclusion: string;
  field_ids: number[];
  theme_ids: number[];
  themes: string[];
  studies: { article_id: number; title: string; fields: { field: string; value: string }[]; segments: { segment_id: number; text: string; page: string; code: string; theme: string }[] }[];
  gaps: string[];
}[];
