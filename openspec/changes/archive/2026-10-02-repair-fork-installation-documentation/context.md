Purpose: complete the bounded DOC-INSTALL-01/02/03 audit batch while preserving previous working-tree fixes.

Decision: tracked fork docs are the installation authority. Public Pages, About, release notes and OCI metadata need their own observed state; local docs cannot repair them. No external mutation is included.

Constraints: preserve upstream issue/contributor attribution; never substitute a nonexistent fork artifact. Execute in isolated stores and temporary paths, including paths with spaces. No user account login or production restart.

Failure examples: Bash treats `git checkout <source-sha>` as redirection; a Bash block cannot run `.\run.ps1`. A historical wheel with metadata 1.25.1 still runs 1.25.0-beta.9. A public About claim of 100% verification remains unsupported while the registry is incomplete.

Evidence and final command inventory are maintained in verification.md and issues-check §27; stable reader guidance is synced to user-documentation/context.md.
