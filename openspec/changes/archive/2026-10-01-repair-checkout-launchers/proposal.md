## Why

INSTALL-09/10/11 need clean checkout and source-launcher verification. Current scripts run uv from the caller's working directory, editable dependency setup leaves dashboard assets absent, PowerShell/batch failure status is not preserved, and run.sh is not executable in Git. A clean clone can report ready while its dashboard is missing.

## What Changes

- Anchor launchers at their own checkout, preserve argument forwarding and exit status, and make the Bash script executable.
- Prepare missing dashboard assets through the existing pinned frontend helper before starting the owned CLI; keep CLI help independent of frontend build prerequisites.
- Verify clean Windows/PowerShell/cmd and Linux/WSL source startup on isolated data, paths with spaces, failure paths and shutdown; document source/native-helper prerequisites without claiming untested macOS behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: checkout launcher preparation, path/argument/exit contracts and prerequisites.

## Impact

run.ps1, start.bat, run.sh, shared source-start helper, focused launcher tests and installation docs/context. No new runtime setting, account operation or production deployment.
