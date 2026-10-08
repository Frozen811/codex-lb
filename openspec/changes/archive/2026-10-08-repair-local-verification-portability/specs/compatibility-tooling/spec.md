## ADDED Requirements

### Requirement: Reference capture catalogs preserve exact bytes across checkouts

Committed reference catalog JSON files MUST retain their canonical LF bytes in Windows and POSIX checkouts. Their recorded capture digests MUST remain unchanged unless a newly verified capture replaces that evidence.

#### Scenario: Windows checkout retains historical capture provenance
- **WHEN** Git checks out a committed reference catalog with automatic CRLF conversion enabled
- **THEN** the catalog's bytes and SHA256 still match its recorded capture provenance

### Requirement: Traffic evidence atomic writes respect platform durability capabilities

Traffic evidence writes MUST flush and fsync the temporary file before atomic replacement and remove abandoned temporary files. On platforms supporting POSIX directory handles they MUST fsync the destination directory and propagate directory-open or sync errors. On Windows they MUST NOT require a POSIX directory handle. POSIX file mode enforcement MUST remain intact on supported platforms; Windows writes MUST retain their requested writable/read-only semantics without claiming POSIX permission masks.

#### Scenario: Windows writer atomically replaces an artifact
- **WHEN** a Windows capture or sanitizer writes an artifact
- **THEN** the file is flushed, fsynced and atomically replaced without attempting an unsupported directory handle

#### Scenario: POSIX directory persistence error remains visible
- **WHEN** a supported platform fails to open or sync the destination directory
- **THEN** the write reports the persistence error instead of claiming durable success
