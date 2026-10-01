# Verification — Nix hook source filtering

Both tasks complete. The initial PR Nix build failed with OSError for scripts/hatch_build.py missing from its explicit source filter.

Package and editable source variants now include only scripts/hatch_build.py and scripts/build_dashboard.py alongside their original explicit inputs. Existing prebuilt frontend and editable dependency-setup behavior is preserved; no flake lock or runtime setting changed. Local input membership and strict OpenSpec validation passed.

Actual Nix flake check succeeded on f61669d62acfe69a15e982d3afadf8a28c1b8b14: https://github.com/Frozen811/codex-lb/actions/runs/36917479916/job/110555586516. Its full PR CI Required also succeeded; PR #5 subsequently merged into main as 8a2b706e4d5ec86f71ec84bd704be8cfde98b7d8. Normative requirement/context were synchronized before merge.

This verifies the packaging compatibility seam. Native Nix installs across every advertised platform and user data/update behavior remain INSTALL-13 audit work. The archive/report commit adds no new build behavior.
