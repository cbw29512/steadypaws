# Steady Paws commerce brief (shared)

Aligned product plan for all Cursor sessions. Do not invent a second paid pack.

## Free (site stays the free app)

- All 72 condition trackers (online worksheets + sample printables)
- Quick Phone Log
- Welcome Home Pet remains the new-pet checklist funnel

Do **not** sell the 72 condition PDFs on Gumroad. The free site already gives those away.

## Paid (one Gumroad product)

**Household Pet Care Binder & Sitter Handover** — $12

Live: https://divclass.gumroad.com/l/household-pet-care-binder

- ~29 pages
- Fillable PDF
- US Letter **and** A4
- What the free site does **not** give: pet profile (microchip/insurance), vaccines & preventatives, meds schedule, vet visit log, emergency contacts, sitter handbook, feeding & supply checklists, grooming, weight, expenses, travel go-bag

## Site changes

1. Buy button on `/packs/` points at the live Gumroad URL (`checkout_url` in `data/household_binder.json` + `data/packs.json`)
2. Free trackers and Quick Phone Log stay ungated
3. One Netlify production deploy when buy button + phone-log fix are ready together

## Abandoned approach

Dog/Cat sick-day ZIPs and “complete library of the free trackers” are **not** the product. Leave any drafts unpublished.
