# Steady Paws Mobile App Product Contract

Status: MVP implementation contract  
Last updated: 2026-09-18

## Product promise

Steady Paws should reduce work for a pet owner who may already be worried, tired, busy, or sitting in a veterinary waiting room. The pet is visually central, routine recording is fast, and the software stays out of the way.

Steady Paws organizes owner-recorded observations. Veterinary professionals make medical decisions.

## Non-negotiable UX rules

1. Buttons first, typing second.
2. Routine observations should ideally take 20 seconds or less.
3. Notes are optional unless free text is genuinely necessary.
4. If information is not necessary to record an observation, do not require it.
5. No account is required for MVP.
6. Core records stay on the user's device.
7. Pet-friendly and reassuring, never childish or overly clinical.
8. No streaks, guilt, alarming gamification, or unnecessary notifications.
9. Never invent treatment schedules, medication doses, diagnoses, or medical interpretations.
10. Existing printable trackers, SEO routes, accessibility, and photo-print behavior must remain intact.

## MVP Definition of Done

Mobile v1 is complete when a user can:

- open Steady Paws comfortably on a phone;
- add a pet with only name and species required;
- optionally add veterinarian contact details;
- choose a simple check-in;
- record common observations with large tap targets;
- add an optional note;
- save and reopen entries locally;
- see recent entries;
- create a vet-ready progress summary;
- preview that summary;
- email/share the summary using the device's normal capabilities;
- print the summary if desired;
- install the site as a PWA;
- open the core app shell offline after it has been loaded once.

Release still requires the existing Steady Paws production quality gate, WCAG checks, photo/print regression, and Lighthouse 100/100/100/100 on mobile and desktop.

## MVP user flow

Home -> My Pet -> Track Today -> tap answers -> optional note -> Save -> Recent Entries -> Prepare for Vet Visit -> Preview -> Email / Share / Print.

The existing printable tracker finder remains available and indexable.

## MVP data schema

### Pet
- id
- name
- species
- photo (future MVP increment; existing homepage personalization remains unchanged)
- vet_name (optional)
- clinic_name (optional)
- vet_email (optional)
- created_at
- updated_at

### Entry
- id
- pet_id
- tracker_id
- occurred_at
- observations: key/value structured answers
- note (optional)
- created_at
- updated_at

### TrackerDefinition
- id
- title
- species applicability
- fields[]
  - key
  - prompt
  - type
  - choices[]
- safety text when required

### VetSummary
Derived rather than independently persisted for MVP:
- pet
- date range
- selected entries
- owner-recorded observations
- notes
- veterinarian contact destination

### AppState
- schema_version
- active_pet_id
- onboarding_complete
- reminder preferences (reserved; reminders are not medical advice)

## Storage

MVP uses local browser storage for structured records. Data is versioned so it can migrate later. Pet photos should use IndexedDB/Blob storage when persistent app photo support is added rather than large base64 values in localStorage.

Export/import backup is a post-MVP priority before claiming device-local storage is a durable archive.

## Check-in interaction

Use large buttons for structured observations. Examples are interaction patterns, not universal medical questions:

- Yes / No
- Better / Same / Worse
- Usual / More / Less / None

Each tracker must define choices appropriate to the observation it records. Do not apply generic medical choices blindly across conditions.

Always provide an optional note field for context.

## Vet sharing

The summary screen prioritizes:

1. Email to Vet
2. Device Share
3. Print

For MVP, Steady Paws opens the user's normal email/share capability. It does not operate an email server or silently send records. The owner reviews and sends the information.

A pet profile may store Primary Vet, Clinic, and Vet Email locally to reduce repeated typing.

## Reminders

Reminders are owner-controlled and may represent schedules the owner or veterinary team has already established. Steady Paws must not independently decide medical follow-up timing.

Good reminder examples:
- owner-entered medication log time;
- owner-entered observation/check-in time;
- owner-entered veterinary appointment;
- owner-entered weight/check schedule.

A completed matching entry should clear/satisfy its reminder where practical.

## Tone and visual design

Warm companion-care aesthetic:
- pet photo/avatar prominent;
- rounded, generous controls;
- strong contrast and readable type;
- subtle paw/pet motifs;
- minimal animation;
- calm completion feedback such as "All caught up for Molly";
- no confetti for health events.

Preferred language:
- "Add a pet", not "Create patient"
- "What you noticed", not "Symptom data"
- "Save today's check-in", not "Submit record"
- "Prepare for a vet visit", not "Generate medical report"

## Accessibility

Automated WCAG compliance is the floor. Design for one-handed use, stress, low vision, shaky hands, arthritis, keyboard users, and screen readers. Important actions must not depend on gestures, tiny icons, or color alone.

## Commercial direction

Free core:
- individual trackers;
- pet profile;
- quick digital check-ins;
- recent history;
- basic vet summary;
- print/share.

Potential premium products after validation:
- polished complete pet-health binder;
- specialized tracker packs;
- premium print designs;
- multi-pet organization;
- advanced long-term reporting/export.

Do not paywall basic health recording.

## Guardrails against product drift

Before adding a feature, ask:
1. Does it make recording easier for the owner?
2. Does it make the owner's record clearer for the veterinary team?
3. Does it preserve the record-keeping/not-diagnosing boundary?
4. Can it stay simple on a phone?
5. Is it worth the cognitive cost?

If not, leave it out.
