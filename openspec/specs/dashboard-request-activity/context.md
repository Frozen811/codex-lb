# Daily request activity

[Requirements](spec.md). The six-calendar-month view runs from the first day of the month five months before the current UTC month through today. startDate/endDate from the server anchor the client calendar, independent of browser clock skew. Empty dates render zero and native date/count tooltips remain keyboard accessible.

Appearance selects weekly credits pace by default or a request heatmap for this browser. Donuts remain unchanged. No per-instance setting or setup step is added. Loading and error/retry states are local to the activity card. Hourly rollups use the shared atomic watermark partition and the raw complement is bounded. Normal historical traffic includes retained activity for removed accounts, while warmup is excluded. Restoring an archive is not an input to this aggregate.

Example: an October 14 display begins May 1. A request at October 13 23:59 UTC contributes to October 13 even in a browser using another timezone. Raw retention after folding does not erase these activity totals.
