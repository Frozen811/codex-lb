import type { RequestActivity } from "@/features/dashboard/schemas";

const DAY_MS = 86_400_000;

export function activityCalendar(data: RequestActivity) {
  const counts = new Map(data.days.map((day) => [day.date, day.requests]));
  const start = Date.parse(`${data.startDate}T00:00:00Z`);
  const end = Date.parse(`${data.endDate}T00:00:00Z`);
  const maximum = Math.max(1, ...data.days.map((day) => day.requests));
  const cells: ({ date: string; requests: number; level: number } | null)[] = [];
  for (let i = 0; i < new Date(start).getUTCDay(); i++) cells.push(null);
  for (let time = start; time <= end; time += DAY_MS) {
    const date = new Date(time).toISOString().slice(0, 10);
    const requests = counts.get(date) ?? 0;
    cells.push({ date, requests, level: requests === 0 ? 0 : Math.min(4, Math.ceil(requests / maximum * 4)) });
  }
  return cells;
}
