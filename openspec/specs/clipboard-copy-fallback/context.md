# Clipboard copy context

The clipboard contract is defined in [spec.md](spec.md). Copying preserves the secure API and synchronous dialog-scoped fallback path, including keyboard focus and pointer activation behavior.

The OAuth-local control uses a two-second copied indicator. It owns one reset timer and cancels it during unmount, following the existing shared copy control's lifecycle pattern while retaining the OAuth button's presentation. Pending clipboard completion is ignored after unmount, including failure feedback.

For example, copying a browser authorization URL and immediately closing the dialog leaves no delayed feedback update. Copying again one second later restarts the two-second interval. A clipboard operation completing after dialog closure does not create a timer or toast. Browser and device flows have unmount regression coverage in `oauth-dialog.test.tsx`; global test teardown is not used to hide application timer leaks.
