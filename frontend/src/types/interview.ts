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
  evaluation: string | null;   // 新增：整场结束后的总评
  messages: MessageOut[];
}

export interface InterviewCreate {
  topic: string;
}

export interface AnswerCreate {
  content: string;
}

export interface InterviewOut {
  id: number;
  topic: string;
  status: string;
  created_at: string;
  evaluation: string | null;   // 新增：整场结束后的总评
  messages: MessageOut[];
}
