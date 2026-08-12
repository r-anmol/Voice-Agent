export type Role = "user" | "kavya" | "system";

export type ChatMessage = {
  id: string;
  role: Exclude<Role, "system">;
  text: string;
  ts: number;
};
