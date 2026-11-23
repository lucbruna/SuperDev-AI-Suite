# DARKSTUDIO Character Identity Engine

## Purpose

Store reusable, explicit character identity contracts and attach them only to scenes
that name the corresponding `character_ids`. The engine is provider-neutral and
does not generate images, inspect pixels, or guarantee identity consistency.

## Profile contract

A profile contains:
- `character_id`: stable safe identifier (1–64 characters).
- `name` and `visual_identity`: authored identity description.
- `reference_asset_ids`: IDs of image assets managed by the project's asset registry;
  raw filesystem paths and arbitrary URLs are deliberately not accepted here.
- `approved_reference_asset_ids`: subset explicitly approved by a human reviewer.
- `reference_asset_reviews`: per-asset state (`pending`, `approved`, `rejected`).
- `reference_asset_metadata`: safe display metadata only; filesystem paths are not persisted.
- `invariants`: features that must remain stable.
- `forbidden_variations`: changes the generation prompt must avoid.

## Scene integration

Call `apply_character_identities(scene, profiles)` after the storyboard assigns
`character_ids` and before sending prompts to an image/video provider. It returns
a copied scene with `character_identity_prompts` and a review status. The source
scene is not mutated. Unknown IDs are surfaced instead of silently inventing a
character profile.

API-managed references are resolved against the real asset registry when a profile
is saved. The asset must belong to the same project, have image MIME/type metadata,
and point to a non-empty file. New references start as `pending` and are not sent
to generation prompts. A reviewer explicitly approves or rejects each reference
through `PUT /jobs/{job_id}/character-identities/{character_id}/references/{asset_id}`.
Only approved IDs are attached to character prompts.

Call `audit_character_identity(scenes, profiles)` before generation to summarize
which scenes have approved reference asset IDs and which require review.

## Honest validation boundary

Only approved asset IDs are included in the provider-neutral character prompt metadata.
This implementation validates and tracks those assets; it does not yet load image
bytes or transmit image-reference inputs to a generation provider. Provider adapters
must implement that transport before claiming image-conditioned character consistency.

An approved reference ID means the asset exists and a human approved its use; it does
not mean that generated pixels match the reference. The engine still cannot compare
faces, clothing, poses, or semantic identity in generated images. A later provider/vision
integration must run image-level checks and retain human review.
