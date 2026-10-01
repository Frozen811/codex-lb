## Decisions

Python wheels must include frontend assets. Reuse complete prebuilt assets in release/sdist workflows; when absent, use the frontend packageManager's exact Bun version and frozen lock to build. A missing or wrong Bun prerequisite must fail clearly, before producing a misleading dashboard-less package. Do not install Bun at runtime or add a configuration toggle.

Keep historical release artifacts explicitly historical and report metadata/runtime/source separately. Bare PyPI commands cannot select this fork. Git commands need a source ref and the pinned build prerequisite; release wheels avoid that prerequisite. Retain application data paths on updates and check installed source outside the checkout.

Use isolated venvs, uv tool/cache directories, temporary data/key/SQLite, and loopback ports. Inspect public archives before executing root project code, never execute nested worktree scripts. Publish source commits on a focused branch; keep release publication governed by exact-source main CI.
