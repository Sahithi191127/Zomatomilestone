import { LOGO_SRC } from "../constants";

export function Nav() {
  return (
    <>
      <div className="tp-glow" />
      <header className="tp-nav-bar">
        <div className="tp-nav-bar-inner">
          <a className="tp-nav-brand" href="/" aria-label="TastePilot home">
            <img
              className="tp-logo tp-logo-dark tp-logo-nav"
              src={LOGO_SRC}
              alt="TastePilot"
              width={160}
            />
          </a>
          <nav className="tp-nav-links tp-nav-links-beside-logo">
            <a href="/" className="active">
              Home
            </a>
            <a href="#about">About</a>
          </nav>
          <div className="tp-nav-icons">
            <span className="material-symbols-outlined tp-icon-red">notifications</span>
            <span className="material-symbols-outlined tp-icon-red">account_circle</span>
          </div>
        </div>
      </header>
    </>
  );
}
