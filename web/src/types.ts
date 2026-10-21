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
