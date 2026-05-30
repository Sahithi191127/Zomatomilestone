import { FOOTER_AREAS, LOGO_SRC } from "../constants";

export function Footer() {
  return (
    <footer className="tp-footer">
      <img className="tp-logo tp-logo-dark tp-logo-footer" src={LOGO_SRC} alt="TastePilot" width={120} />
      <p>Smarter restaurant discovery for Bangalore food lovers.</p>
      <div className="tp-footer-divider" />
      <div className="tp-footer-links">
        {FOOTER_AREAS.map((area) => (
          <a key={area} href={`#${area}`}>
            {area}
          </a>
        ))}
        <span className="tp-footer-sep">|</span>
        <a href="#terms">Terms</a>
        <a href="#privacy">Privacy</a>
      </div>
      <p className="tp-footer-copy">
        © 2026 TastePilot AI — Helping Bangalore discover better places to eat.
      </p>
    </footer>
  );
}
