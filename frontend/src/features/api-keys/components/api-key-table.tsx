import { Ellipsis, KeyRound, Pencil, RefreshCw, RotateCcw, Trash2 } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ApiKey, LimitRule, LimitType } from "@/features/api-keys/schemas";
import { useDateDisplayFormatStore, type DateDisplayFormat } from "@/hooks/use-date-format";
import { formatCompactNumber, formatCurrency, formatTimeLong } from "@/utils/formatters";

function formatExpiry(value: string | null, neverLabel: string, displayFormat: DateDisplayFormat): string {
  if (!value) {
    return neverLabel;
  }
  const parsed = formatTimeLong(value, displayFormat);
  return `${parsed.date} ${parsed.time}`;
}

const LIMIT_TYPE_SHORT: Record<LimitType, string> = {
  total_tokens: "Tokens",
  input_tokens: "Input",
  output_tokens: "Output",
  cost_usd: "Cost",
  credits: "Credits",
};

function formatLimitSummary(limits: LimitRule[], t: ReturnType<typeof useTranslation>["t"]): string {
  if (limits.length === 0) return "-";
  return limits
    .map((l) => {
      const type = t(`apiKeys.limitTypes.${l.limitType}`, { defaultValue: LIMIT_TYPE_SHORT[l.limitType] });
      const isCost = l.limitType === "cost_usd";
      const isCredits = l.limitType === "credits";
      const current = isCost
        ? `$${(l.currentValue / 1_000_000).toFixed(2)}`
        : formatCompactNumber(l.currentValue);
      const max = isCost
        ? `$${(l.maxValue / 1_000_000).toFixed(2)}`
        : formatCompactNumber(l.maxValue);
      const suffix = isCost ? l.limitWindow : isCredits ? `${l.limitWindow}` : l.limitWindow;
      return `${type}: ${current}/${max} ${suffix}`;
    })
    .join(" | ");
}

function formatUsageSummary(
  requestCount: number,
  totalTokens: number,
  cachedInputTokens: number,
  totalCostUsd: number,
  t: ReturnType<typeof useTranslation>["t"],
): string {
  const total = formatCompactNumber(totalTokens);
  const cached = formatCompactNumber(cachedInputTokens);
  const requests = formatCompactNumber(requestCount);
  const cost = formatCurrency(totalCostUsd);
  return t("apiKeys.table.usageSummary", { total, cached, requests, cost });
}

function getUsageValue(apiKey: ApiKey, t: ReturnType<typeof useTranslation>["t"]): string {
  if (!apiKey.usageSummary) {
    return t("apiKeys.table.noUsage");
  }

  return formatUsageSummary(
    apiKey.usageSummary.requestCount,
    apiKey.usageSummary.totalTokens,
    apiKey.usageSummary.cachedInputTokens,
    apiKey.usageSummary.totalCostUsd,
    t,
  );
}

function getLimitValue(apiKey: ApiKey, t: ReturnType<typeof useTranslation>["t"]): string {
  const parts = apiKey.usageSharePercent === null
    ? []
    : [t("apiKeys.table.usageShare", { percent: apiKey.usageSharePercent })];
  if (apiKey.limits.length > 0) {
    parts.push(formatLimitSummary(apiKey.limits, t));
  }
  return parts.join(" | ") || t("apiKeys.table.noLimit");
}

export type ApiKeyTableProps = {
  keys: ApiKey[];
  busy: boolean;
  selectedIds?: Set<string>;
  onSelectedIdsChange?: (selectedIds: Set<string>) => void;
  onEdit: (apiKey: ApiKey) => void;
  onDelete: (apiKey: ApiKey) => void;
  onRegenerate: (apiKey: ApiKey) => void;
  onResetUsage?: (apiKeys: ApiKey[]) => void;
};

export function ApiKeyTable({
  keys,
  busy,
  selectedIds: propsSelectedIds,
  onSelectedIdsChange,
  onEdit,
  onDelete,
  onRegenerate,
  onResetUsage,
}: ApiKeyTableProps) {
  const { t } = useTranslation();
  const dateDisplayFormat = useDateDisplayFormatStore((state) => state.dateDisplayFormat);
  const [internalSelectedIds, setInternalSelectedIds] = useState<Set<string>>(new Set());

  const selectedIds = propsSelectedIds ?? internalSelectedIds;
  const setSelectedIds = onSelectedIdsChange ?? setInternalSelectedIds;

  const allSelected = keys.length > 0 && keys.every((k) => selectedIds.has(k.id));
  const someSelected = keys.some((k) => selectedIds.has(k.id)) && !allSelected;

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(keys.map((k) => k.id)));
    }
  };

  const selectAllWithLimits = () => {
    const withLimits = keys.filter((k) => k.limits.length > 0).map((k) => k.id);
    setSelectedIds(new Set(withLimits));
  };

  const toggleRow = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedIds(next);
  };

  const hasKeysWithLimits = keys.some((k) => k.limits.length > 0);

  if (keys.length === 0) {
    return <EmptyState icon={KeyRound} title={t("apiKeys.table.empty")} />;
  }

  return (
    <div className="space-y-3">
      {selectedIds.size > 0 ? (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-muted/40 p-2.5 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-medium text-foreground">
              {t("apiKeys.actions.selectedCount", { count: selectedIds.size })}
            </span>
            <Button
              type="button"
              variant="ghost"
              size="xs"
              className="h-7 text-xs text-muted-foreground"
              onClick={() => setSelectedIds(new Set())}
            >
              {t("apiKeys.actions.clearSelection")}
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="xs"
              className="h-7 text-xs"
              onClick={selectAllWithLimits}
            >
              {t("apiKeys.actions.selectAllWithLimits")}
            </Button>
            <Button
              type="button"
              variant="default"
              size="xs"
              className="h-7 gap-1.5 text-xs"
              onClick={() => {
                const selected = keys.filter((k) => selectedIds.has(k.id));
                onResetUsage?.(selected);
              }}
              disabled={busy}
            >
              <RotateCcw className="size-3.5" />
              {t("apiKeys.actions.resetSelectedUsage", { count: selectedIds.size })}
            </Button>
          </div>
        </div>
      ) : hasKeysWithLimits ? (
        <div className="flex items-center justify-end">
          <Button
            type="button"
            variant="ghost"
            size="xs"
            className="h-7 text-xs text-muted-foreground hover:text-foreground"
            onClick={selectAllWithLimits}
          >
            {t("apiKeys.actions.selectAllWithLimits")}
          </Button>
        </div>
      ) : null}

      <div className="overflow-x-auto rounded-xl border">
        <Table className="table-fixed">
          <TableHeader>
            <TableRow>
              <TableHead className="w-[4%] min-w-[2.5rem] pl-4">
                <Checkbox
                  checked={allSelected ? true : someSelected ? "indeterminate" : false}
                  onCheckedChange={toggleSelectAll}
                  aria-label={t("common.actions.selectAll", { defaultValue: "Select all" })}
                />
              </TableHead>
              <TableHead className="w-[18%] min-w-[11rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.name")}</TableHead>
              <TableHead className="w-[9%] min-w-[7.5rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.prefix")}</TableHead>
              <TableHead className="w-[8%] min-w-[6rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.models")}</TableHead>
              <TableHead className="w-[8%] min-w-[6rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.traffic")}</TableHead>
              <TableHead className="w-[24%] min-w-[16rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.usage")}</TableHead>
              <TableHead className="w-[14%] min-w-[11rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.limit")}</TableHead>
              <TableHead className="w-[8%] min-w-[6.5rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.expiry")}</TableHead>
              <TableHead className="w-[6%] min-w-[5rem] text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.status")}</TableHead>
              <TableHead className="w-[5%] min-w-[4rem] pr-4 text-right text-[11px] uppercase tracking-wider text-muted-foreground/80">{t("apiKeys.table.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keys.map((apiKey) => {
              const models = apiKey.allowedModels?.join(", ") || t("common.options.all");
              const trafficClass = apiKey.trafficClass === "opportunistic" ? t("common.traffic.opportunistic") : t("common.traffic.foreground");
              const isSelected = selectedIds.has(apiKey.id);

              return (
                <TableRow key={apiKey.id} data-state={isSelected ? "selected" : undefined}>
                  <TableCell className="pl-4">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => toggleRow(apiKey.id)}
                      aria-label={apiKey.name}
                    />
                  </TableCell>
                  <TableCell className="font-medium truncate">{apiKey.name}</TableCell>
                  <TableCell className="truncate font-mono text-xs">{apiKey.keyPrefix}</TableCell>
                  <TableCell className="truncate">{models}</TableCell>
                  <TableCell className="truncate text-xs tabular-nums">{trafficClass}</TableCell>
                  <TableCell className="text-xs tabular-nums leading-tight whitespace-normal">{getUsageValue(apiKey, t)}</TableCell>
                  <TableCell className="text-xs tabular-nums leading-tight whitespace-normal">{getLimitValue(apiKey, t)}</TableCell>
                  <TableCell className="truncate text-xs text-muted-foreground">{formatExpiry(apiKey.expiresAt, t("common.time.never"), dateDisplayFormat)}</TableCell>
                  <TableCell>
                    <Badge className={apiKey.isActive ? "bg-emerald-500 text-white" : "bg-zinc-500 text-white"}>
                      {apiKey.isActive ? t("common.states.active") : t("common.states.disabled")}
                    </Badge>
                  </TableCell>
                  <TableCell className="pr-4 text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button type="button" size="icon-sm" variant="ghost" disabled={busy}>
                          <Ellipsis className="size-4" />
                          <span className="sr-only">{t("apiKeys.table.actions")}</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onEdit(apiKey)}>
                          <Pencil className="size-4" />
                          {t("common.actions.edit")}
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onRegenerate(apiKey)}>
                          <RefreshCw className="size-4" />
                          {t("common.actions.regenerate")}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => onResetUsage?.([apiKey])}
                          disabled={apiKey.limits.length === 0}
                        >
                          <RotateCcw className="size-4" />
                          {t("apiKeys.actions.resetUsage")}
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem variant="destructive" onClick={() => onDelete(apiKey)}>
                          <Trash2 className="size-4" />
                          {t("common.actions.delete")}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
