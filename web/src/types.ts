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
