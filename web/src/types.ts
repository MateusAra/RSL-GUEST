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
