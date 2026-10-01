## Decision

Keep the narrow explicit Nix inputs; add scripts/hatch_build.py and scripts/build_dashboard.py to both source variants rather than copying the scripts directory or disabling the hook. Package builds reuse Nix frontend assets, editable builds retain their existing dependency-setup exemption. Their metadata now always loads the declared build plugin.

## Verification

Reproduce the current CI OSError for missing scripts/hatch_build.py, validate the exact source membership locally, then run the Nix flake job on the corrected PR head. Do not call this a full INSTALL-13 native deployment audit.
