## ADDED Requirements

### Requirement: Nix filtered sources include declared package build hooks

Both Nix package and editable source filters MUST include the custom build hook declared by project metadata and the helper it loads. They MUST preserve explicit exclusion of unrelated workstation state. Standard Nix builds SHALL reuse their prebuilt dashboard assets, while editable builds SHALL retain explicit frontend preparation.

#### Scenario: Project metadata declares a custom Hatch hook

- **WHEN** Nix builds a package or editable environment from filtered project source
- **THEN** the declared hook and its required helper are present
- **AND** package creation does not fail because a referenced build script is missing
