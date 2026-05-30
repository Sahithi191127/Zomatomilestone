export const MOOD_OPTIONS: { label: string; value: string }[] = [
  { label: "Choose an occasion (optional)", value: "" },
  { label: "Date Night", value: "date_night" },
  { label: "Family Dinner", value: "family_dinner" },
  { label: "Quick Lunch", value: "quick_lunch" },
  { label: "Friends Hangout", value: "friends_hangout" },
  { label: "Work Meeting", value: "work_meeting" },
  { label: "Solo Dining", value: "solo_dining" },
  { label: "Celebration", value: "celebration_birthday" },
  { label: "Fine Dining", value: "fine_dining" },
  { label: "Cafe / Chill", value: "cafe_chill" },
];

export const BUDGET_OPTIONS: { label: string; value: "low" | "medium" | "high" }[] = [
  { label: "BUDGET", value: "low" },
  { label: "MEDIUM", value: "medium" },
  { label: "PREMIUM", value: "high" },
];

export const RESULT_COUNTS = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20,
] as const;

export const LOADING_MIN_MS = 4500;

import { assetUrl } from "./api/config";

export const LOGO_SRC = assetUrl("/images/tastepilot-logo-dark.png");
export const LOADING_RING_SRC = assetUrl("/images/loading-ring.svg");
export const EMPTY_ILLUSTRATION_SRC = assetUrl("/images/empty-illustration.svg");

export const FOOTER_AREAS = [
  "Koramangala",
  "Indiranagar",
  "HSR Layout",
  "Whitefield",
];

export const MOOD_FOOTER: Record<string, string> = {
  date_night: "Great match for date night",
  family_dinner: "Great match for family dining",
  quick_lunch: "Great match for a quick lunch",
  friends_hangout: "Great match for friends hangout",
  work_meeting: "Great match for work meetings",
  solo_dining: "Great match for solo dining",
  celebration_birthday: "Great match for celebrations",
  fine_dining: "Great match for fine dining",
  cafe_chill: "Great match for a relaxed cafe vibe",
};
