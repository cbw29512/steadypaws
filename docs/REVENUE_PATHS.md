# Revenue paths — 2026-09-30

## Objective and definition of done

Extend the site's established optional-support model to Quick Phone Log after
a visitor prepares a useful summary. The homepage already offers support after
a download. Completion means the summary, sharing, and print actions continue
to work and the support note never appears on printed veterinary records.

## Data and state

Pet/check-in records retain their existing local storage and photo handling.
The existing `setup`, `home`, `checkin`, and `summary` views remain authoritative.
The support note belongs to the summary view; it adds no application state,
tracking event, medical recommendation, or data collection.

The existing owner support URL is `https://buymeacoffee.com/divclass016`.
Links use `noopener noreferrer` and include no pet data, notes, or identifiers.
Support is optional and does not unlock features or change access.

## Logic flow

1. Visitor records observations using the existing local app.
2. Prepare for a vet visit displays the existing summary and sharing controls.
3. A secondary support note links to the owner's existing support page.
4. Print CSS hides the support note and keeps the clinical record focused.

## Validation and publishing

Exercise setup, check-in, summary, and print preview at phone/desktop sizes.
Keep new modules under 150 lines; larger existing files should be split when
their behavior is next changed. The new stylesheet is in the existing offline
precache. Use `[skip netlify]` on the commit and PR title. Do not publish.
