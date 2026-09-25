import { KeySquare } from "lucide-react";
import { lazy, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/confirm-dialog";
import { AlertMessage } from "@/components/alert-message";
import { Button } from "@/components/ui/button";
import { useDialogState } from "@/hooks/use-dialog-state";
import { ApiKeyAuthToggle } from "@/features/api-keys/components/api-key-auth-toggle";
import { ApiKeyQuotaPrivacyToggle } from "@/features/api-keys/components/api-key-quota-privacy-toggle";
import { ApiKeyCreatedDialog } from "@/features/api-keys/components/api-key-created-dialog";
import { ApiKeyTable } from "@/features/api-keys/components/api-key-table";
import { useApiKeys } from "@/features/api-keys/hooks/use-api-keys";
import type { ApiKey, ApiKeyCreateRequest, ApiKeyUpdateRequest } from "@/features/api-keys/schemas";
import { getErrorMessageOrNull } from "@/utils/errors";

const ApiKeyCreateDialog = lazy(() =>
  import("@/features/api-keys/components/api-key-create-dialog").then((m) => ({ default: m.ApiKeyCreateDialog })),
);
const ApiKeyEditDialog = lazy(() =>
  import("@/features/api-keys/components/api-key-edit-dialog").then((m) => ({ default: m.ApiKeyEditDialog })),
);

export type ApiKeysSectionProps = {
  apiKeyAuthEnabled: boolean;
  hideUpstreamQuotaFromApiKeys: boolean;
  disabled?: boolean;
  /** The auth and quota-privacy toggles are security settings (`security:write`). */
  policyControlsDisabled?: boolean;
  onApiKeyAuthEnabledChange: (enabled: boolean) => void;
  onHideUpstreamQuotaFromApiKeysChange: (enabled: boolean) => void;
};

export function ApiKeysSection({
  apiKeyAuthEnabled,
  hideUpstreamQuotaFromApiKeys,
  disabled = false,
  policyControlsDisabled = disabled,
  onApiKeyAuthEnabledChange,
  onHideUpstreamQuotaFromApiKeysChange,
}: ApiKeysSectionProps) {
  const { t } = useTranslation();
  const {
    apiKeysQuery,
    createMutation,
    updateMutation,
    deleteMutation,
    regenerateMutation,
    resetUsageMutation,
    bulkResetUsageMutation,
  } = useApiKeys();

  const createDialog = useDialogState();
  const editDialog = useDialogState<ApiKey>();
  const deleteDialog = useDialogState<ApiKey>();
  const createdDialog = useDialogState<string>();
  const resetDialog = useDialogState<ApiKey[]>();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const keys = apiKeysQuery.data ?? [];
  const busy =
    disabled ||
    apiKeysQuery.isFetching ||
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending ||
    regenerateMutation.isPending ||
    resetUsageMutation.isPending ||
    bulkResetUsageMutation.isPending;

  const mutationError = useMemo(
    () =>
      getErrorMessageOrNull(createMutation.error) ||
      getErrorMessageOrNull(updateMutation.error) ||
      getErrorMessageOrNull(deleteMutation.error) ||
      getErrorMessageOrNull(regenerateMutation.error) ||
      getErrorMessageOrNull(resetUsageMutation.error) ||
      getErrorMessageOrNull(bulkResetUsageMutation.error),
    [
      createMutation.error,
      deleteMutation.error,
      regenerateMutation.error,
      updateMutation.error,
      resetUsageMutation.error,
      bulkResetUsageMutation.error,
    ],
  );

  const handleCreate = async (payload: ApiKeyCreateRequest) => {
    const created = await createMutation.mutateAsync(payload);
    createdDialog.show(created.key);
  };

  const handleUpdate = async (payload: ApiKeyUpdateRequest) => {
    if (!editDialog.data) {
      return;
    }
    await updateMutation.mutateAsync({ keyId: editDialog.data.id, payload });
  };

  const handleResetUsage = async () => {
    if (!resetDialog.data || resetDialog.data.length === 0) {
      return;
    }
    const keyIds = resetDialog.data.map((k) => k.id);
    await bulkResetUsageMutation.mutateAsync(keyIds);
    setSelectedIds(new Set());
    resetDialog.hide();
  };

  return (
    <section className="space-y-3 rounded-xl border bg-card p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <KeySquare className="h-4 w-4 text-primary" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-sm font-semibold">{t("apiKeys.section.title")}</h3>
            <p className="text-xs text-muted-foreground">{t("apiKeys.section.description")}</p>
          </div>
        </div>
        <Button type="button" size="sm" className="h-8 text-xs" onClick={() => createDialog.show()} disabled={busy}>
          {t("apiKeys.section.createKey")}
        </Button>
      </div>

      <ApiKeyAuthToggle
        enabled={apiKeyAuthEnabled}
        disabled={busy || policyControlsDisabled}
        onChange={onApiKeyAuthEnabledChange}
      />

      <ApiKeyQuotaPrivacyToggle
        enabled={hideUpstreamQuotaFromApiKeys}
        disabled={busy || policyControlsDisabled}
        onChange={onHideUpstreamQuotaFromApiKeysChange}
      />

      {mutationError ? <AlertMessage variant="error">{mutationError}</AlertMessage> : null}

      <ApiKeyTable
        keys={keys}
        busy={busy}
        selectedIds={selectedIds}
        onSelectedIdsChange={setSelectedIds}
        onEdit={(apiKey) => editDialog.show(apiKey)}
        onDelete={(apiKey) => deleteDialog.show(apiKey)}
        onRegenerate={(apiKey) => {
          void regenerateMutation.mutateAsync(apiKey.id).then((result) => {
            createdDialog.show(result.key);
          });
        }}
        onResetUsage={(apiKeys) => resetDialog.show(apiKeys)}
      />

      <ApiKeyCreateDialog
        open={createDialog.open}
        busy={createMutation.isPending}
        onOpenChange={createDialog.onOpenChange}
        onSubmit={handleCreate}
      />

      <ApiKeyEditDialog
        open={editDialog.open}
        busy={updateMutation.isPending}
        apiKey={editDialog.data}
        onOpenChange={editDialog.onOpenChange}
        onSubmit={handleUpdate}
      />

      <ApiKeyCreatedDialog
        open={createdDialog.open}
        apiKey={createdDialog.data}
        onOpenChange={createdDialog.onOpenChange}
      />

      <ConfirmDialog
        open={deleteDialog.open}
        title={t("apiKeys.deleteDialog.title")}
        description={t("apiKeys.deleteDialog.description")}
        confirmLabel={t("common.actions.delete")}
        onOpenChange={deleteDialog.onOpenChange}
        onConfirm={() => {
          if (!deleteDialog.data) {
            return;
          }
          void deleteMutation.mutateAsync(deleteDialog.data.id).finally(() => {
            deleteDialog.hide();
          });
        }}
      />

      <ConfirmDialog
        open={resetDialog.open}
        title={
          resetDialog.data && resetDialog.data.length === 1
            ? t("apiKeys.resetDialog.title_one")
            : t("apiKeys.resetDialog.title_other", { count: resetDialog.data?.length ?? 0 })
        }
        description={
          resetDialog.data && resetDialog.data.length === 1
            ? t("apiKeys.resetDialog.description_one", { name: resetDialog.data[0].name })
            : t("apiKeys.resetDialog.description_other", { count: resetDialog.data?.length ?? 0 })
        }
        confirmLabel={t("apiKeys.actions.resetUsage")}
        onOpenChange={resetDialog.onOpenChange}
        onConfirm={handleResetUsage}
      >
        {resetDialog.data && resetDialog.data.length > 1 ? (
          <div className="max-h-36 overflow-y-auto rounded-md border bg-muted/40 p-2 text-xs space-y-1">
            <p className="font-medium text-foreground">{t("apiKeys.resetDialog.affectedKeys")}</p>
            <ul className="list-disc pl-4 space-y-0.5 text-muted-foreground">
              {resetDialog.data.map((key) => (
                <li key={key.id} className="truncate">
                  {key.name} <span className="font-mono text-[10px]">({key.keyPrefix})</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </ConfirmDialog>
    </section>
  );
}
