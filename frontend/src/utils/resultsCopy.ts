/** Consumer-facing results headline + subtext (ignores API summary). */
export function buildResultsSummary(
  cuisineDisplay: string,
  location: string,
): { headline: string; subtext: string } {
  const cuisine = cuisineDisplay.trim() || "Restaurant";
  const area = location.trim() || "your area";

  return {
    headline: "Your personalized restaurant recommendations",
    subtext: `${cuisine} restaurants in ${area} matched to your budget, rating, and dining preferences.`,
  };
}
