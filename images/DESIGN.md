---
name: TastePilot
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#5b403f'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#7e5700'
  on-secondary: '#ffffff'
  secondary-container: '#ffba34'
  on-secondary-container: '#6e4c00'
  tertiary: '#5c5c5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#757474'
  on-tertiary-container: '#fffcfb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffdeab'
  secondary-fixed-dim: '#ffba34'
  on-secondary-fixed: '#281900'
  on-secondary-fixed-variant: '#5f4100'
  tertiary-fixed: '#e4e2e1'
  tertiary-fixed-dim: '#c8c6c6'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#474747'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: DM Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: DM Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: DM Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: DM Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: DM Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: DM Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: DM Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: DM Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1200px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style

The design system for TastePilot is built on a foundation of "Appetizing Intelligence." It departs from the cold, robotic aesthetic of typical AI tools to embrace a warm, food-forward energy that feels communal and reliable. The brand personality is that of a knowledgeable local foodie friend: confident, enthusiastic, and sophisticated but accessible.

The visual direction follows a **Corporate / Modern** aesthetic with **Minimalist** leanings, prioritizing high-quality food photography and clear information hierarchy. Every interface element is designed to recede, allowing the vibrant colors of food and the clarity of AI-driven recommendations to take center stage. We avoid "AI purple" gradients in favor of a "human-first" digital experience that feels premium and trustworthy.

## Colors

The palette is anchored by **Zomato Coral (#E23744)**, used strategically for primary actions and brand presence. This color is chosen for its ability to stimulate appetite and convey energy. 

- **Primary:** #E23744 (Brand Red) — Used for primary buttons, active states, and key highlights.
- **Secondary:** #FFBA33 (Saffron Glow) — Used for star ratings, "Top Pick" badges, and warmth.
- **Neutral Background:** #F8F8F8 — A soft off-white that reduces eye strain and feels more organic than pure white.
- **Surface:** #FFFFFF — Used for cards and elevated containers to create depth against the background.
- **Typography:** #1C1C1C (Charcoal) — High-contrast for maximum legibility, avoiding absolute black for a softer premium feel.
- **AI Accent:** #F0F4FF (Subtle Blue Tint) — Used exclusively for the background of "AI Explained" components to denote a logic layer without breaking the food-centric palette.

## Typography

**DM Sans** is the sole typeface for this design system, chosen for its geometric purity and modern, approachable character. The hierarchy is intentionally steep to guide users through dense restaurant data quickly.

- **Headlines:** Bold weights (700) are used for restaurant names and section headers to provide a strong anchor.
- **Currency (INR ₹):** Should always match the weight of the accompanying price text but may use a slightly reduced opacity (80%) to keep the focus on the value.
- **AI Badges:** Use `label-sm` in all-caps with increased letter spacing for a technical, precise feel that contrasts with the fluid body text.

## Layout & Spacing

The design system utilizes a **12-column fluid grid** for desktop and a **4-column grid** for mobile. We follow an 8px linear scale for all spacing to ensure mathematical harmony across the UI.

- **Desktop:** 1200px max-width container, centered. Gutters are fixed at 24px to provide ample breathing room between food cards.
- **Mobile:** Full-width layout with 16px side margins. Vertical spacing between cards is increased to 20px to prevent accidental taps.
- **Density:** We prefer "Generous" density for discovery phases (browsing restaurants) and "Compact" density for utility phases (checkout or filter sidebars).

## Elevation & Depth

Hierarchy is established through **Tonal Layers** and **Ambient Shadows**. This design system avoids heavy borders, preferring light-based depth cues to feel "airy" and modern.

- **Level 0 (Background):** #F8F8F8.
- **Level 1 (Cards/Surfaces):** White (#FFFFFF) with a very soft, diffused shadow: `0px 4px 20px rgba(0, 0, 0, 0.04)`.
- **Level 2 (Hover/Active):** Slightly more pronounced shadow: `0px 8px 30px rgba(0, 0, 0, 0.08)` to indicate interactivity.
- **Interactive Elements:** Use 1px borders in #E8E8E8 for input fields and segmented controls to define boundaries without adding visual weight.

## Shapes

The shape language is **Rounded**, reflecting the organic nature of food and hospitality. 

- **Standard Elements:** 0.5rem (8px) radius for input fields, buttons, and small UI elements.
- **Cards:** 1rem (16px) radius for restaurant cards to give them a friendly, modern look.
- **Pills:** Used for AI badges and category filters (e.g., "Biryani", "North Indian") to differentiate them from functional buttons.

## Components

### Buttons & Controls
- **Primary Button:** Solid #E23744 with white text. 8px border radius.
- **Segmented Controls:** Used for switching between "Delivery" and "Dining Out". Features a subtle grey track (#F0F0F0) with a white elevated "thumb" for the active state.
- **Star Rating Sliders:** A custom track where the "filled" portion uses Saffron Glow (#FFBA33). The handle is a clean white circle with a subtle shadow.

### AI Touchpoints
- **AI Explained Badge:** A small pill with a light blue background (#F0F4FF) and dark blue text. It includes a 12px "sparkle" icon (SVG) to indicate the insight was generated by the TastePilot engine.
- **Insight Cards:** Bordered with a 1px dashed line in Coral to indicate "active" AI calculation/reasoning.

### Restaurant Cards
- **Image-First:** Top 60% of the card is a high-resolution food/ambiance image.
- **Content:** Name in `headline-md`, followed by a sub-line with cuisine type and price-range (e.g., "₹₹ · South Indian").
- **Badge Overlay:** AI "Match Score" displayed in the top-right corner of the image as a semi-transparent white pill.

### Searchable Dropdowns
- Features a "recent searches" section with micro-icons for "location" and "history".
- High-contrast focus states using a 2px Coral outer glow.