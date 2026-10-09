# Runtime Portability Context

See `openspec/specs/runtime-portability/spec.md` for normative requirements.

## Bounded retag planning and progress

Planning reads a fixed 64 KiB header per session and reuses grouped SQLite
provider counts. A leading canonical session_meta record or consecutive legacy
provider records establish the metadata region. The remaining transcript is
copied as opaque bytes, including CRLF or non-UTF-8 content. An incomplete large
tail after recognized legacy metadata is preserved; malformed or oversized
initial metadata fails before backups or writes. Targeted discovery reuses its
header observations, and a database lacking session identity cannot be broadly
updated by a targeted command.

For example, a 2 MiB transcript contributes only its leading provider tag to
planning and summaries. JSONL backups prefer hard links, and rewriting replaces
the working file so the original linked backup survives. SQLite snapshots and
the existing mount fallback remain in use. Keep Codex clients stopped throughout
the operation: multiple file/database updates are not a transaction. A partial
failure reports its retained backup directory for manual recovery.

Use `--progress-json` to consume phase events on stderr while the human summary
stays on stdout. Counts describe completed files/databases, so a large backup
copy or SQL query can take time between events. Closing that pipe disables
progress without aborting work; the Windows CRT's EINVAL and POSIX broken-pipe
forms are handled. Other I/O failures still propagate. No progress is required
for normal command use, and no new settings are introduced.

## Codex Session Retagging

`codex resume` filters sessions by `model_provider`. Sessions created before
switching to codex-lb may still be tagged as `openai`, so they will not appear
until the stored provider tag is updated.

Use the built-in command instead of editing Codex files by hand:

```bash
# Preview what will change first.
codex-lb codex-sessions retag --from openai --to codex-lb --dry-run

# Then close Codex/Codex CLI and apply the retag.
codex-lb codex-sessions retag --from openai --to codex-lb --yes
```

The command updates both Codex storage formats when they exist: JSONL session
files under `~/.codex/sessions` and `state_*.sqlite` thread rows created by
newer Codex CLI versions. It uses Python's built-in SQLite support, creates a
backup under `~/.codex/backups/provider-retag/`, and refuses non-interactive
writes unless `--yes` is provided.

On native Windows, macOS, Linux, and WSL, use `--codex-home PATH` if your Codex
data directory is not detected. In WSL, autodetect only considers the current
Windows `USERPROFILE`; pass `--codex-home /mnt/c/Users/<name>/.codex` to retag
another Windows profile explicitly.

To switch back, reverse the providers:

```bash
codex-lb codex-sessions retag --from codex-lb --to openai --dry-run
codex-lb codex-sessions retag --from codex-lb --to openai --yes
```

For Docker, mount your Codex data directory only for this one-off command:

```bash
docker run --rm \
  -v ~/.codex:/codex-home \
  ghcr.io/soju06/codex-lb:latest \
  codex-lb codex-sessions retag --from openai --to codex-lb \
    --codex-home /codex-home --dry-run

docker run --rm \
  -v ~/.codex:/codex-home \
  ghcr.io/soju06/codex-lb:latest \
  codex-lb codex-sessions retag --from openai --to codex-lb \
    --codex-home /codex-home --yes
```
