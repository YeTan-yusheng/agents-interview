export interface MessageOut {
  id: number;
  role: string;        // "interviewer" | "candidate"
  content: string;
  created_at: string;
}

export interface InterviewOut {
  id: number;
  topic: string;
  status: string;
  created_at: string;
  messages: MessageOut[];
}

export interface InterviewCreate {
  topic: string;
}
