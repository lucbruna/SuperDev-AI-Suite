# DARKSTUDIO Character Identity Engine

## Purpose

Store reusable, explicit character identity contracts and attach them only to scenes
that name the corresponding `character_ids`. The engine is provider-neutral and
does not generate images, inspect pixels, or guarantee identity consistency.

## Profile contract

A profile contains:
- `character_id`: stable safe identifier (1–64 characters).
- `name` and `visual_identity`: authored identity description.
- `reference_asset_ids`: IDs of approved assets managed by the application; raw
  filesystem paths and arbitrary URLs are deliberately not accepted here.
- `invariants`: features that must remain stable.
- `forbidden_variations`: changes the generation prompt must avoid.

## Scene integration

Call `apply_character_identities(scene, profiles)` after the storyboard assigns
`character_ids` and before sending prompts to an image/video provider. It returns
a copied scene with `character_identity_prompts` and a review status. The source
scene is not mutated. Unknown IDs are surfaced instead of silently inventing a
character profile.

Call `audit_character_identity(scenes, profiles)` before generation to summarize
which scenes have approved reference asset IDs and which require review.

## Honest validation boundary

A profile with reference IDs is marked `references_attached`, not visually verified.
The engine cannot know whether those IDs resolve to existing approved images until
the asset registry is integrated. It also cannot compare faces, clothing, poses,
or semantic identity in generated pixels. A later provider/vision integration must
resolve approved asset IDs, run image-level checks, and retain human approval.
