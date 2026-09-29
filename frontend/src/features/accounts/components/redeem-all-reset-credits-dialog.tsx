import { ConfirmDialog } from "@/components/confirm-dialog";
import { useAccountMutations } from "@/features/accounts/hooks/use-accounts";
import { useTranslation } from "react-i18next";

export type RedeemAllResetCreditsDialogAccount = {
  accountId: string;
  displayName: string;
  email: string;
  alias?: string | null;
  availableResetCredits: number;
};

export type RedeemAllResetCreditsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  eligibleAccounts: RedeemAllResetCreditsDialogAccount[];
};

export function RedeemAllResetCreditsDialog({
  open,
  onOpenChange,
  eligibleAccounts,
}: RedeemAllResetCreditsDialogProps) {
  const { t } = useTranslation();
  const { redeemAllResetCreditsMutation } = useAccountMutations();
  const pending = redeemAllResetCreditsMutation.isPending;

  const totalCredits = eligibleAccounts.reduce(
    (sum, a) => sum + (a.availableResetCredits || 0),
    0,
  );

  const handleConfirm = () => {
    if (pending || eligibleAccounts.length === 0) {
      return;
    }
    void redeemAllResetCreditsMutation
      .mutateAsync()
      .then(() => {
        onOpenChange(false);
      })
      .catch(() => {
        // Handled by onError toast
      });
  };

  const handleOpenChange = (next: boolean) => {
    if (!next && pending) {
      return;
    }
    onOpenChange(next);
  };

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={handleOpenChange}
      title={t("accounts.bulkRedeemDialog.title", "Redeem all eligible reset credits")}
      description={t(
        "accounts.bulkRedeemDialog.description",
        "This will consume all banked rate-limit reset credits for each eligible account. Each account consumes only its own credits.",
      )}
      confirmLabel={
        pending
          ? t("accounts.bulkRedeemDialog.redeeming", "Redeeming...")
          : t("accounts.bulkRedeemDialog.confirm", "Redeem all credits ({{count}})", {
              count: totalCredits,
            })
      }
      cancelLabel={t("common.cancel", "Cancel")}
      onConfirm={handleConfirm}
      confirmDisabled={pending || eligibleAccounts.length === 0 || totalCredits === 0}
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between rounded-lg border bg-muted/30 px-3 py-2 text-sm font-medium">
          <span>{t("accounts.bulkRedeemDialog.totalLabel", "Total credits to redeem:")}</span>
          <span className="font-semibold text-primary">{totalCredits}</span>
        </div>

        <div className="max-h-56 overflow-y-auto space-y-1.5 divide-y divide-border/40 rounded-md border p-2">
          {eligibleAccounts.length === 0 ? (
            <p className="p-2 text-xs text-muted-foreground text-center">
              {t("accounts.bulkRedeemDialog.noAccounts", "No eligible accounts with banked credits found.")}
            </p>
          ) : (
            eligibleAccounts.map((account) => (
              <div
                key={account.accountId}
                className="flex items-center justify-between pt-1.5 first:pt-0 text-xs"
              >
                <div className="min-w-0 pr-2">
                  <div className="truncate font-medium">
                    {account.alias || account.displayName || account.email}
                  </div>
                  {account.alias ? (
                    <div className="truncate text-muted-foreground">{account.email}</div>
                  ) : null}
                </div>
                <div className="shrink-0 font-medium">
                  {t("accounts.bulkRedeemDialog.creditCount", "{{count}} credit", {
                    count: account.availableResetCredits,
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </ConfirmDialog>
  );
}
