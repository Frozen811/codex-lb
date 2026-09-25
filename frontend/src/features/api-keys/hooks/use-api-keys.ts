import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";

import {
  createApiKey,
  deleteApiKey,
  listApiKeys,
  regenerateApiKey,
  updateApiKey,
} from "@/features/api-keys/api";
import type {
  ApiKeyCreateRequest,
  ApiKeyUpdateRequest,
} from "@/features/api-keys/schemas";

export function useApiKeys() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data, error, isFetching, isLoading, isPending, isSuccess, refetch } = useQuery({
    queryKey: ["api-keys", "list"],
    queryFn: listApiKeys,
  });
  const apiKeysQuery = { data, error, isFetching, isLoading, isPending, isSuccess, refetch };

  const createMutation = useMutation({
    mutationFn: (payload: ApiKeyCreateRequest) => createApiKey(payload),
    onSuccess: () => {
      toast.success(t("apiKeys.toasts.created"));
      void queryClient.invalidateQueries({ queryKey: ["api-keys", "list"] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("apiKeys.toasts.createFailed"));
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ keyId, payload }: { keyId: string; payload: ApiKeyUpdateRequest }) =>
      updateApiKey(keyId, payload),
    onSuccess: () => {
      toast.success(t("apiKeys.toasts.updated"));
      void queryClient.invalidateQueries({ queryKey: ["api-keys", "list"] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("apiKeys.toasts.updateFailed"));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (keyId: string) => deleteApiKey(keyId),
    onSuccess: () => {
      toast.success(t("apiKeys.toasts.deleted"));
      void queryClient.invalidateQueries({ queryKey: ["api-keys", "list"] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("apiKeys.toasts.deleteFailed"));
    },
  });

  const regenerateMutation = useMutation({
    mutationFn: (keyId: string) => regenerateApiKey(keyId),
    onSuccess: () => {
      toast.success(t("apiKeys.toasts.regenerated"));
      void queryClient.invalidateQueries({ queryKey: ["api-keys", "list"] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("apiKeys.toasts.regenerateFailed"));
    },
  });

  const resetUsageMutation = useMutation({
    mutationFn: (keyId: string) => updateApiKey(keyId, { resetUsage: true }),
    onSuccess: () => {
      toast.success(t("apiKeys.toasts.usageReset"));
      void queryClient.invalidateQueries({ queryKey: ["api-keys", "list"] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("apiKeys.toasts.usageResetFailed"));
    },
  });

  const bulkResetUsageMutation = useMutation({
    mutationFn: async (keyIds: string[]) => {
      const results = await Promise.allSettled(
        keyIds.map((keyId) => updateApiKey(keyId, { resetUsage: true }))
      );
      const succeeded: string[] = [];
      const failed: { keyId: string; error: Error }[] = [];
      results.forEach((res, index) => {
        if (res.status === "fulfilled") {
          succeeded.push(keyIds[index]);
        } else {
          failed.push({
            keyId: keyIds[index],
            error: res.reason instanceof Error ? res.reason : new Error(String(res.reason)),
          });
        }
      });
      return { succeeded, failed, total: keyIds.length };
    },
    onSuccess: (data) => {
      if (data.succeeded.length > 0 && data.failed.length === 0) {
        toast.success(
          data.succeeded.length === 1
            ? t("apiKeys.toasts.usageReset")
            : t("apiKeys.toasts.usageResetMany", { count: data.succeeded.length })
        );
      } else if (data.succeeded.length > 0) {
        toast.warning(
          t("apiKeys.toasts.usageResetPartial", {
            succeeded: data.succeeded.length,
            failed: data.failed.length,
          })
        );
      } else {
        toast.error(t("apiKeys.toasts.usageResetFailed"));
      }
      void queryClient.invalidateQueries({ queryKey: ["api-keys", "list"] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("apiKeys.toasts.usageResetFailed"));
    },
  });

  return {
    apiKeysQuery,
    createMutation,
    updateMutation,
    deleteMutation,
    regenerateMutation,
    resetUsageMutation,
    bulkResetUsageMutation,
  };
}
