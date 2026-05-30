Design a modern, polished web app UI for an AI-powered restaurant recommendation product inspired by Zomato. The app helps users in Bangalore discover where to eat by combining structured filters with AI-generated rankings and explanations. Target: desktop-first responsive web (mobile-friendly). This is a portfolio-quality consumer product, not an admin dashboard.

Product summary

Name (working): Zomato AI Recommendations / TastePilot

One-liner:
“Tell us what you want — we filter real restaurants and AI explains your best matches.”

Core value:
Personalized, explainable picks (not just a filter list). Every result shows why it fits the user’s preferences.

User flow:
Land on home → see preference form
Submit preferences → loading state (2–15 seconds while AI ranks)
See optional AI summary + ranked restaurant cards (top 1–20)
Handle empty results, errors, and degraded AI gracefully
No login, no cart, no booking — discovery only for MVP.

Brand & visual direction

Inspiration:
Zomato’s warmth and food-forward energy — appetizing, trustworthy, urban India context

Mood:
Friendly, confident, slightly premium; avoid generic “AI purple gradient” clichés

Color:
Primary accent in Zomato-adjacent red/coral (#E23744 family) with neutral backgrounds (off-white / warm gray), strong contrast for accessibility

Typography:
Clean sans-serif (e.g. Inter, DM Sans, or similar); clear hierarchy for restaurant names vs metadata

Imagery:
Use food/restaurant placeholder imagery on cards where helpful; locality context (Bangalore neighbourhoods) can appear as subtle chips or map-pin motifs — no real map required for MVP

AI touch:
Small “AI explained” badge or sparkle icon on explanation blocks — subtle, not gimmicky

Screens to design

Screen 1 — Home / Search preferences (default)

Header

- Logo + product name
- Short subtitle:
“Personalized picks from real Zomato data — filtered by you, ranked by AI”

Preference form
(card or panel layout, 2-column on desktop, stacked on mobile)

Field | Control Type | Notes

Location (area)

- Searchable dropdown
- ~90 Bangalore neighbourhoods: Indiranagar, Bellandur, BTM, Koramangala 5th Block, HSR, Whitefield, etc.
- Show map-pin icon

Budget

- Segmented control or dropdown
- Options: Low · Medium · High (₹ for two implied)

Cuisine

- Text input with suggestions
- Placeholder:
“Italian, Chinese, North Indian…”

Minimum rating

- Slider 0.0–5.0 (step 0.5)
- Show star icon + numeric value

Additional preferences

- Multi-line text (optional)
- Placeholder:
“family-friendly, quick service, outdoor seating”

Mood / Occasion (NEW)

- Control type:
Single-select searchable dropdown
- Must visually match the Location dropdown for consistency
- Placement:
Add below “Additional preferences” and above “Get recommendations” button
- Label:
Mood / Occasion
- Helper text:
“Choose the vibe or occasion for smarter recommendations”
- Placeholder:
“Choose an occasion (optional)”
- Default:
None selected

Dropdown options:

- None
- Date Night ❤️
- Family Dinner 👨‍👩‍👧
- Quick Lunch ⚡
- Friends Hangout 🍻
- Work Meeting 💼
- Solo Dining 🍽️
- Celebration / Birthday 🎉
- Casual Dining 🍕
- Fine Dining ✨
- Cafe / Chill ☕

Dropdown UX requirements:

- Must use the same spacing, typography, border radius, hover states, focus states, and visual language as existing dropdowns
- Responsive across desktop and mobile
- Keyboard accessible
- Clear selected state
- Compact and clean (do not use chips/pills/cards UI)
- Support subtle icons/emojis in dropdown items
- Add info tooltip icon beside label with copy:
“Recommendations adapt based on dining mood and context”

Behavior:

- Single select only
- Optional field
- Selecting an option influences recommendation ranking and AI explanations
- Do not redesign or change any existing form components — only add this dropdown consistently

Recommendation influence examples:

- Date Night → cozy, romantic, quiet ambience
- Family Dinner → spacious seating, family-friendly
- Quick Lunch → fast service, affordable, nearby
- Friends Hangout → lively atmosphere, group seating
- Work Meeting → quieter, professional ambience
- Solo Dining → comfortable individual dining spaces
- Celebration / Birthday → larger seating, lively environment
- Fine Dining → premium/high-rated venues
- Cafe / Chill → relaxed ambience, cafés, slower pace

API mapping:
Add field:

mood_occasion

Example payload:

{
"location": "Indiranagar",
"budget": "medium",
"cuisine": "italian",
"min_rating": 4.0,
"additional_preferences": "family-friendly, quick service",
"top_k": 5,
"mood_occasion": "date_night"
}

Number of results

- Stepper or compact select
- 1–20, default 5

Primary CTA:
Full-width button — “Get recommendations”

Empty / idle state below form:
Light illustration or icon +
“Set your preferences and we’ll find the best spots for you.”

Screen 2 — Loading

After submit:

- Disable form / show overlay
- Skeleton cards (3–5 placeholders) OR centered loader with copy:
“Finding and ranking restaurants…”
- Optional progress hint:
“Filtering matches → Asking AI → Preparing your list”
- Do not use a blank white screen

Screen 3 — Results (success)

Section A — AI summary (optional)
Highlighted banner/card at top when present

Example copy:
“Five strong Italian options in Indiranagar within a medium budget, including family-friendly spots.”

Section B — Recommendation cards (vertical list or responsive grid)

Design a reusable Restaurant Recommendation Card with:

- Rank badge (#1, #2, …)
- Restaurant name
- Location
- Rating
- Cost (“₹800 for two”)
- Cuisine tags/chips
- AI explanation block:
“Why we picked this”
- Budget band chip

Card interaction:
Hover elevation on desktop; readable without expand for MVP.

Section C — Search details (collapsible footer)
Accordion:
“Search details”
(candidates considered, filter time, AI time)

Screen 4 — Empty results
Headline:
“No restaurants match”

Body:
“Try relaxing your area, cuisine, minimum rating, or budget.”

Secondary CTA:
“Adjust filters”

Screen 5 — Degraded AI (fallback)
Alert:
“AI ranking unavailable — showing top-rated matches from your filters.”

Screen 6 — Error states

- Validation errors
- System error + retry
- Data unavailable banner

Component library to include

- Primary / secondary buttons
- Searchable select (location)
- Budget segmented control
- Star rating slider
- Cuisine text field + chip suggestions
- Restaurant recommendation card
- AI summary banner
- Warning / info / error alerts
- Skeleton loaders
- Empty state illustration block
- Collapsible “Search details” panel
- Rank badge (#1 gold accent optional)

UX principles (must follow)

- Scannable results
- Explainability first
- Trust
- Accessibility
- Performance perception

Out of scope

- Login
- Cart / booking
- Maps
- Restaurant detail page
- Chat interface

Technical handoff notes
UI implemented in React or Streamlit.

API fields:
location, budget, cuisine, min_rating, additional_preferences, top_k, mood_occasion

Results map to:
summary, recommendations[] with restaurant metadata + explanation

Currency:
INR (₹)

Location dropdown:
Neighbourhood/area only, not city free text.

Deliverables requested from Stitch

- Home + preference form (desktop + mobile)
- Loading state
- Results page
- Empty state
- Component spec
- Export-friendly React/Tailwind-ready layout

Make the design feel like a real Zomato-inspired product someone would demo in a portfolio — polished, warm, and focused on helping users choose where to eat tonight.