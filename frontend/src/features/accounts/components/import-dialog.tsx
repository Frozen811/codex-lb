import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export type ImportDialogProps = {
  open: boolean;
  busy: boolean;
  error: string | null;
  onOpenChange: (open: boolean) => void;
  onImport: (file: File) => Promise<void>;
};

const emptyTokenFields = {
  accessToken: "",
  email: "",
  accountId: "",
  workspaceId: "",
  planType: "business" as "business" | "enterprise",
};

export function ImportDialog({
  open,
  busy,
  error,
  onOpenChange,
  onImport,
}: ImportDialogProps) {
  const { t } = useTranslation();
  const [files, setFiles] = useState<File[]>([]);
  const [inputKey, setInputKey] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [mode, setMode] = useState<"files" | "token">("files");
  const [tokenFields, setTokenFields] = useState(emptyTokenFields);
  const submission = useRef(false);
  const importReady =
    mode === "files"
      ? files.length > 0
      : Boolean(
          tokenFields.accessToken.trim() &&
            tokenFields.email.trim() &&
            tokenFields.accountId.trim(),
        );

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submission.current || busy || !importReady) {
      return;
    }

    submission.current = true;
    setSubmitting(true);
    try {
      const pendingFiles =
        mode === "files"
          ? files
          : [
              new File(
                [
                  JSON.stringify({
                    tokens: { accessToken: tokenFields.accessToken },
                    email: tokenFields.email.trim(),
                    accountId: tokenFields.accountId.trim(),
                    planType: tokenFields.planType,
                    workspaceId: tokenFields.workspaceId.trim() || undefined,
                  }),
                ],
                "access-token.json",
                { type: "application/json" },
              ),
            ];
      for (const [index, file] of pendingFiles.entries()) {
        try {
          await onImport(file);
        } catch {
          if (mode === "files") {
            setFiles(files.slice(index));
            setInputKey((currentKey) => currentKey + 1);
          }
          return;
        }
        if (mode === "files") setFiles(files.slice(index + 1));
      }

      onOpenChange(false);
      setFiles([]);
      setTokenFields(emptyTokenFields);
      setMode("files");
      setInputKey((currentKey) => currentKey + 1);
    } finally {
      submission.current = false;
      setSubmitting(false);
    }
  };

  const importBusy = busy || submitting;

  return (
    <Dialog
      open={open}
      onOpenChange={(nextOpen) => {
        if (!submission.current && !busy) {
          if (!nextOpen) {
            setTokenFields(emptyTokenFields);
            setMode("files");
          }
          onOpenChange(nextOpen);
        }
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("accounts.importDialog.title")}</DialogTitle>
          <DialogDescription>
            {t("accounts.importDialog.description")}
          </DialogDescription>
        </DialogHeader>

        <form
          className="space-y-4"
          aria-busy={importBusy}
          onSubmit={handleSubmit}
        >
          <div className="flex gap-2">
            <Button
              type="button"
              variant={mode === "files" ? "secondary" : "outline"}
              aria-pressed={mode === "files"}
              disabled={importBusy}
              onClick={() => {
                setMode("files");
                setTokenFields(emptyTokenFields);
              }}
            >
              {t("accounts.importDialog.filesMode")}
            </Button>
            <Button
              type="button"
              variant={mode === "token" ? "secondary" : "outline"}
              aria-pressed={mode === "token"}
              disabled={importBusy}
              onClick={() => setMode("token")}
            >
              {t("accounts.importDialog.tokenMode")}
            </Button>
          </div>
          {mode === "files" ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="auth-json-file">
                  {t("accounts.importDialog.fileLabel")}
                </Label>
                <Input
                  key={inputKey}
                  id="auth-json-file"
                  type="file"
                  accept="application/json,.json"
                  multiple
                  disabled={importBusy}
                  onChange={(event) =>
                    setFiles(Array.from(event.currentTarget.files ?? []))
                  }
                />
              </div>

              {files.length > 0 ? (
                <div className="space-y-1 text-xs text-muted-foreground">
                  <p>{t("accounts.importDialog.selectedFiles")}</p>
                  <ul className="max-h-28 space-y-1 overflow-y-auto rounded-md border px-2 py-1">
                    {files.map((file, index) => (
                      <li
                        key={`${file.name}-${file.size}-${file.lastModified}-${index}`}
                        className="truncate"
                        title={file.name}
                      >
                        {file.name}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </>
          ) : (
            <>
              <p className="text-xs text-muted-foreground">
                {t("accounts.importDialog.tokenHelp")}
              </p>
              {(
                [
                  ["accessToken", "tokenMode", "password", true],
                  ["email", "tokenEmail", "email", true],
                  ["accountId", "tokenAccountId", "text", true],
                  ["workspaceId", "tokenWorkspaceId", "text", false],
                ] as const
              ).map(([field, label, type, required]) => (
                <div key={field} className="space-y-2">
                  <Label htmlFor={`pat-${field}`}>
                    {t(`accounts.importDialog.${label}`)}
                  </Label>
                  <Input
                    id={`pat-${field}`}
                    type={type}
                    value={tokenFields[field]}
                    autoComplete="off"
                    required={required}
                    disabled={importBusy}
                    onChange={(event) =>
                      setTokenFields((current) => ({
                        ...current,
                        [field]: event.target.value,
                      }))
                    }
                  />
                </div>
              ))}
              <div className="space-y-2">
                <Label htmlFor="pat-plan">
                  {t("accounts.importDialog.tokenPlan")}
                </Label>
                <select
                  id="pat-plan"
                  className="h-9 w-full rounded-md border bg-background px-3 text-sm"
                  disabled={importBusy}
                  value={tokenFields.planType}
                  onChange={(event) =>
                    setTokenFields((current) => ({
                      ...current,
                      planType:
                        event.target.value === "enterprise"
                          ? "enterprise"
                          : "business",
                    }))
                  }
                >
                  <option value="business">Business</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </>
          )}

          {error ? (
            <p className="rounded-md border border-destructive/30 bg-destructive/10 px-2 py-1 text-xs text-destructive">
              {error}
            </p>
          ) : null}

          <DialogFooter>
            <Button type="submit" disabled={importBusy || !importReady}>
              {t("common.actions.import")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
