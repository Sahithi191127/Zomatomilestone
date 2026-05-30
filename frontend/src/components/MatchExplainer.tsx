import { formatLabel } from "../api/client";

interface MatchExplainerProps {
  location: string;
  cuisine: string;
  budget: string;
  minRating: number;
}

function budgetLabel(budget: string): string {
  const map: Record<string, string> = {
    low: "Budget",
    medium: "Medium",
    high: "Premium",
  };
  return map[budget] ?? formatLabel(budget);
}

function ratingLabel(value: number): string {
  const text = value.toFixed(1).replace(/\.0$/, "");
  return `${text}+`;
}

export function MatchExplainer({
  location,
  cuisine,
  budget,
  minRating,
}: MatchExplainerProps) {
  return (
    <details className="tp-expander">
      <summary>How TastePilot matched your restaurants</summary>
      <div className="tp-expander-body">
        <div className="tp-match-explainer">
          <p className="tp-match-explainer-subtitle">
            We matched restaurants based on what matters to you.
          </p>
          <div className="tp-match-explainer-rows">
            <div className="tp-match-explainer-row">
              <span className="tp-match-explainer-icon" aria-hidden>
                📍
              </span>
              <div className="tp-match-explainer-copy">
                <span className="tp-match-explainer-label">Location</span>
                <p className="tp-match-explainer-text">
                  Showing restaurants in <strong>{location || "your area"}</strong>
                </p>
              </div>
            </div>
            <div className="tp-match-explainer-row">
              <span className="tp-match-explainer-icon" aria-hidden>
                🍽️
              </span>
              <div className="tp-match-explainer-copy">
                <span className="tp-match-explainer-label">Cuisine preference</span>
                <p className="tp-match-explainer-text">
                  Prioritized <strong>{cuisine || "your preferred cuisine"}</strong> restaurants
                </p>
              </div>
            </div>
            <div className="tp-match-explainer-row">
              <span className="tp-match-explainer-icon" aria-hidden>
                💰
              </span>
              <div className="tp-match-explainer-copy">
                <span className="tp-match-explainer-label">Budget</span>
                <p className="tp-match-explainer-text">
                  Focused on <strong>{budgetLabel(budget)}</strong> dining options
                </p>
              </div>
            </div>
            <div className="tp-match-explainer-row">
              <span className="tp-match-explainer-icon" aria-hidden>
                ⭐
              </span>
              <div className="tp-match-explainer-copy">
                <span className="tp-match-explainer-label">Minimum rating</span>
                <p className="tp-match-explainer-text">
                  Recommended places rated <strong>{ratingLabel(minRating)}</strong>
                </p>
              </div>
            </div>
            <div className="tp-match-explainer-row">
              <span className="tp-match-explainer-icon" aria-hidden>
                ✨
              </span>
              <div className="tp-match-explainer-copy">
                <span className="tp-match-explainer-label">Personalized ranking</span>
                <p className="tp-match-explainer-text">
                  Ranked using ratings, reviews, cuisine match, dining preferences, and overall
                  fit for your search
                </p>
              </div>
            </div>
          </div>
          <p className="tp-match-explainer-trust">
            We evaluated multiple restaurant options to find your best matches.
          </p>
        </div>
      </div>
    </details>
  );
}
