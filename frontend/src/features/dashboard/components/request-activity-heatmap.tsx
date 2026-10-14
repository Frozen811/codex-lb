import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { getRequestActivity } from "@/features/dashboard/api";
import { activityCalendar } from "@/features/dashboard/activity-calendar";

const LEVELS = ["bg-muted", "bg-emerald-200 dark:bg-emerald-950", "bg-emerald-400 dark:bg-emerald-800", "bg-emerald-500 dark:bg-emerald-600", "bg-emerald-700 dark:bg-emerald-400"];

export function RequestActivityHeatmap() {
  const { t } = useTranslation();
  const query = useQuery({ queryKey: ["dashboard", "request-activity"], queryFn: getRequestActivity, refetchInterval: 60_000 });
  return <section className="min-w-0 rounded-xl border bg-card p-4" aria-label={t("dashboard.activity.title")}>
    <h3 className="mb-3 text-sm font-semibold">{t("dashboard.activity.title")}</h3>
    {query.isPending ? <p role="status" className="text-xs text-muted-foreground">{t("common.loading")}</p> : null}
    {query.error ? <div role="alert" className="space-y-2 text-xs">
      <p>{t("dashboard.activity.error")}</p><Button size="sm" onClick={() => void query.refetch()}>{t("common.actions.retry")}</Button>
    </div> : null}
    {query.data ? <>
      <div className="overflow-x-auto pb-2">
        <div className="grid grid-flow-col grid-rows-7 gap-1" style={{ gridAutoColumns: "10px", width: "max-content" }}>
          {activityCalendar(query.data).map((cell, i) => cell ? <Tooltip key={cell.date}>
            <TooltipTrigger asChild><button type="button" aria-label={t("dashboard.activity.day", { date: cell.date, count: cell.requests })}
              className={`h-2.5 w-2.5 rounded-[2px] focus-visible:outline-2 focus-visible:outline-ring ${LEVELS[cell.level]}`} /></TooltipTrigger>
            <TooltipContent>{t("dashboard.activity.day", { date: cell.date, count: cell.requests })}</TooltipContent>
          </Tooltip> : <span key={`empty-${i}`} />)}
        </div>
      </div>
      <div className="mt-2 flex items-center justify-end gap-1 text-[10px] text-muted-foreground">
        <span>{t("dashboard.activity.less")}</span>{LEVELS.map((level) => <span key={level} className={`h-2.5 w-2.5 rounded-[2px] ${level}`} />)}<span>{t("dashboard.activity.more")}</span>
      </div>
    </> : null}
  </section>;
}
