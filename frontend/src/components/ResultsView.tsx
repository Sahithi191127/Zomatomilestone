import type { PreferencesPayload, RecommendationResponse } from "../types";
import { buildResultsSummary } from "../utils/resultsCopy";
import { MatchExplainer } from "./MatchExplainer";
import { ResultCard } from "./ResultCard";

interface ResultsViewProps {
  response: RecommendationResponse;
  payload: PreferencesPayload;
  cuisineDisplay: string;
  onAdjust: () => void;
  onAgain: () => void;
}

export function ResultsView({
  response,
  payload,
  cuisineDisplay,
  onAdjust,
  onAgain,
}: ResultsViewProps) {
  const { headline, subtext } = buildResultsSummary(
    cuisineDisplay,
    payload.location,
  );

  return (
    <>
      {response.meta.fallback_used && (
        <div className="tp-alert tp-alert-warning" style={{ maxWidth: 720, margin: "0 auto 1rem" }}>
          <strong>AI ranking unavailable</strong>
          <p>Showing top-rated matches from your filters with mood-aware fallback.</p>
        </div>
      )}
      <div className="tp-results-hero">
        <h1>
          <span className="tp-sparkle">✨</span> {headline}
        </h1>
        <p>{subtext}</p>
      </div>
      <div className="tp-results-grid">
        {response.recommendations.map((rec) => (
          <ResultCard key={rec.restaurant.id} rec={rec} mood={payload.mood} />
        ))}
      </div>
      <MatchExplainer
        location={payload.location}
        cuisine={cuisineDisplay}
        budget={payload.budget}
        minRating={payload.min_rating}
      />
      <div className="tp-results-cta">
        <h3>Want better recommendations?</h3>
      </div>
      <div className="tp-results-actions">
        <button type="button" className="tp-btn-secondary" onClick={onAdjust}>
          Adjust filters
        </button>
        <button type="button" className="tp-btn-ghost" onClick={onAgain}>
          Try another search
        </button>
      </div>
    </>
  );
}
