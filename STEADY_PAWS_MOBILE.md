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


## Authority vision: the sick-pet memory system

Steady Paws should become the tool an owner remembers after a difficult illness because it reduced the mental load of caring for their pet.

Target story:
> "When Fluffy was sick there was so much to remember, but Steady Paws kept the medicine, meals, bathroom changes, treatment notes, and vet updates straight."

This is not a diagnosis product. It is the reliable memory and communication layer between the owner, other caregivers, and the veterinary team.

### Core care record domains

The product architecture should support structured, timestamped records for:
- medications: owner/vet-entered name, prescribed directions, scheduled times, given/skipped status, optional note;
- treatments and home-care tasks: owner/vet-entered instructions and completion;
- food and diet: food name/type, amount offered, amount eaten, meal time, optional diet-plan note;
- water/intake observations;
- stool/bowel movements: occurrence plus simple owner observations and optional photo/note;
- urination observations;
- vomiting/regurgitation events;
- appetite;
- energy/activity/mobility;
- weight;
- symptoms/changes the owner noticed;
- photos and documents;
- veterinary appointments and owner questions.

The app records what the owner or veterinary team specified. It must not invent a dose, treatment, diet, target, or medical schedule.

### Today screen priority

For a pet under active care, the default experience should answer:
1. What did I already record today?
2. What owner/vet-entered care items are still due?
3. Did someone else already do it? (future caregiver sharing)
4. What changed today?
5. Can I show the vet an accurate timeline without reconstructing it from memory?

Medication and treatment actions should be one-tap completion wherever safe. Food, water, stool, urine, vomiting, and common observations should be quick-log actions.

### Trust requirements for authority status

Authority is earned through reliability, not medical claims:
- exact timestamps;
- edit history/auditability for important medication/treatment records;
- clear distinction between scheduled, completed, skipped, and not recorded;
- never convert "not recorded" into "missed";
- explicit units for amounts/doses/weights;
- timezone-safe dates;
- backup/export before users depend on local-only history;
- accessible and usable while stressed;
- owner-entered facts remain verbatim in vet summaries;
- report completeness should be transparent;
- no generated diagnosis or verdict.

### Product success metric

The primary success metric is not time spent in the app. It is whether an owner can reliably care for a sick pet with less memory burden and give the veterinary team a clearer, trustworthy history.


## Photo-first evidence capture

Photo capture is a first-class care-record feature, not decoration.

### Interaction
- A prominent "Take a photo" action should use the phone camera directly when supported.
- "Choose existing photo" remains available.
- Photo automatically inherits pet, date/time, and the care event/check-in it was captured from.
- Owner may add a short optional caption.
- No filename management is exposed to the owner.
- Thumbnail appears immediately in the timeline.
- Owner can remove/replace a photo with an undo opportunity before final report sharing.

### Report behavior
- Vet Summary can include selected photos inline next to the associated timestamp/event.
- Default report should use useful thumbnails rather than enormous images.
- Tapping/opening the digital report should preserve access to a clearer image where feasible.
- Photo captions remain owner-recorded observations and are not medically interpreted.
- Report generation must distinguish attached photos from missing/not-recorded photos.

### Storage and privacy
- Persistent care-record photos use IndexedDB Blob storage, not base64 localStorage.
- Keep originals locally where practical while generating appropriately sized report/display derivatives.
- Strip unnecessary metadata from exported/shared derivatives where practical, especially location metadata.
- Never upload a care photo merely to make local tracking work.
- Backup/export must eventually include photo attachments so a device loss does not destroy the care history.

### Quality
- Camera/photo capture must be tested on narrow mobile layouts.
- Large photos must not freeze or overflow the UI.
- Orientation must display correctly.
- Reports must paginate cleanly with photos.
- Existing Steady Paws photo/download/print regression remains mandatory.
