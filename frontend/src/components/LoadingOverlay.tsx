import { LOADING_RING_SRC, LOGO_SRC } from "../constants";

export function LoadingOverlay() {
  return (
    <div className="tp-loading-overlay">
      <div className="tp-loading-card">
        <div className="tp-loading-logo-wrap">
          <img className="tp-loading-ring" src={LOADING_RING_SRC} alt="" />
          <img
            className="tp-logo tp-logo-dark tp-logo-loading tp-logo-pulse"
            src={LOGO_SRC}
            alt="TastePilot"
            height={62}
          />
        </div>
        <h2 className="tp-loading-title">Finding your perfect matches…</h2>
        <p className="tp-loading-sub">
          TastePilot is ranking restaurants from real data using your preferences.
        </p>
        <ul className="tp-loading-steps">
          <li className="tp-step tp-step-1">
            <span className="tp-step-icon">
              <span className="tp-step-mark tp-step-mark-pending" />
              <span className="tp-step-mark tp-step-mark-active material-symbols-outlined">
                sync
              </span>
              <span className="tp-step-mark tp-step-mark-done material-symbols-outlined">
                check
              </span>
            </span>
            <span className="tp-step-label-em">Filtering restaurants</span>
          </li>
          <li className="tp-step tp-step-2">
            <span className="tp-step-icon">
              <span className="tp-step-mark tp-step-mark-pending" />
              <span className="tp-step-mark tp-step-mark-active material-symbols-outlined">
                psychology
              </span>
              <span className="tp-step-mark tp-step-mark-done material-symbols-outlined">
                check
              </span>
            </span>
            <span>AI ranking & explanations</span>
          </li>
          <li className="tp-step tp-step-3">
            <span className="tp-step-icon">
              <span className="tp-step-mark tp-step-mark-pending" />
              <span className="tp-step-mark tp-step-mark-active material-symbols-outlined">
                auto_awesome
              </span>
              <span className="tp-step-mark tp-step-mark-done material-symbols-outlined">
                check
              </span>
            </span>
            <span>Preparing your picks</span>
          </li>
        </ul>
        <div className="tp-loading-progress-pill">
          <span className="tp-loading-pill-sparkle">✨</span>
          This usually takes a few seconds
        </div>
      </div>
    </div>
  );
}
