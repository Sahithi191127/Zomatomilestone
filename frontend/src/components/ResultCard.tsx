import { MOOD_FOOTER } from "../constants";
import { formatLabel } from "../api/client";
import type { Recommendation } from "../types";

interface ResultCardProps {
  rec: Recommendation;
  mood?: string | null;
}

export function ResultCard({ rec, mood }: ResultCardProps) {
  const r = rec.restaurant;
  const badge =
    rec.rank === 1 ? (
      <span className="tp-badge-best">#1 Best Match</span>
    ) : (
      <span className="tp-badge-rank">#{rec.rank} Match</span>
    );
  const footerLine =
    (mood && MOOD_FOOTER[mood]) || "Great match for your preferences";

  return (
    <article className="tp-result-card">
      <div className="tp-result-card-head">
        {badge}
        <span className="tp-rating-pill">★ {r.rating.toFixed(1)}</span>
      </div>
      <h3>{r.name}</h3>
      <p className="tp-result-loc">
        📍 {r.location} · ₹{Math.round(r.estimated_cost)} for two
      </p>
      <div className="tp-result-chips">
        {r.cuisines.slice(0, 5).map((c) => (
          <span key={c} className="tp-chip">
            {formatLabel(c)}
          </span>
        ))}
      </div>
      <div className="tp-why-box">
        <strong>Why TastePilot picked this:</strong>
        <p>{rec.explanation}</p>
      </div>
      <p className="tp-result-footer-line">✓ {footerLine}</p>
    </article>
  );
}
