import { EMPTY_ILLUSTRATION_SRC, LOGO_SRC } from "../constants";

interface EmptyStateProps {
  onChip: (chip: string) => void;
}

const CHIPS = [
  ["Lower minimum rating", "lower_rating"],
  ["Expand budget", "expand_budget"],
  ["Try nearby areas", "nearby_areas"],
  ["Broaden cuisine", "broaden_cuisine"],
] as const;

export function EmptyState({ onChip }: EmptyStateProps) {
  return (
    <div className="tp-empty-page">
      <div className="tp-empty-visual">
        <img className="tp-empty-plate-bg" src={EMPTY_ILLUSTRATION_SRC} alt="" />
        <div className="tp-empty-logo-badge">
          <img className="tp-logo tp-logo-dark" src={LOGO_SRC} alt="" height={28} />
        </div>
      </div>
      <h2>No matches found</h2>
      <p className="tp-empty-body">
        We couldn&apos;t find restaurants that fit all your filters. Try adjusting your
        preferences — TastePilot will help you discover more places worth trying.
      </p>
      <p className="tp-empty-chips-label">Quick adjustments</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "0.5rem", maxWidth: 640, margin: "0 auto" }}>
        {CHIPS.map(([label, key]) => (
          <button
            key={key}
            type="button"
            className="tp-btn-secondary"
            style={{ borderRadius: 999, fontSize: 12 }}
            onClick={() => onChip(key)}
          >
            {label}
          </button>
        ))}
      </div>
      <p className="tp-empty-disclaimer">
        <em>We search real restaurants and rank recommendations based on your preferences.</em>
      </p>
    </div>
  );
}
