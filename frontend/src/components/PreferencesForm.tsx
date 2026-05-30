import { FormEvent, useMemo } from "react";
import {
  BUDGET_OPTIONS,
  MOOD_OPTIONS,
  RESULT_COUNTS,
} from "../constants";
import type { PreferencesPayload } from "../types";
import { SelectField } from "./SelectField";

interface PreferencesFormProps {
  cities: string[];
  cuisineLabels: string[];
  cuisineLabelToRaw: Record<string, string>;
  initial: FormState;
  maxAdditionalChars: number;
  onSubmit: (payload: PreferencesPayload, cuisineDisplay: string) => void;
}

export interface FormState {
  location: string;
  budget: "low" | "medium" | "high";
  cuisineLabel: string;
  minRating: number;
  topK: number;
  mood: string;
  additional: string;
}

export function PreferencesForm({
  cities,
  cuisineLabels,
  cuisineLabelToRaw,
  initial,
  maxAdditionalChars,
  onSubmit,
}: PreferencesFormProps) {
  const defaultCity = useMemo(() => {
    if (initial.location && cities.includes(initial.location)) return initial.location;
    if (cities.includes("Bellandur")) return "Bellandur";
    return cities[0] ?? "";
  }, [cities, initial.location]);

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const location = String(fd.get("location") ?? defaultCity);
    const budget = String(fd.get("budget") ?? "medium") as "low" | "medium" | "high";
    const cuisineLabel = String(fd.get("cuisine") ?? "");
    const cuisine = cuisineLabelToRaw[cuisineLabel] ?? cuisineLabel.toLowerCase();
    const minRating = Number(fd.get("min_rating") ?? 2.9);
    const topK = Number(fd.get("top_k") ?? 5);
    const mood = String(fd.get("mood") ?? "");
    const additional = String(fd.get("additional") ?? "").trim();

    const payload: PreferencesPayload = {
      location,
      budget,
      cuisine,
      min_rating: minRating,
      top_k: topK,
      mood: mood || null,
      additional_preferences: additional || null,
    };
    onSubmit(payload, cuisineLabel);
  }

  return (
    <form className="tp-form-card" onSubmit={handleSubmit}>
      <div className="tp-form-row">
        <div className="tp-field">
          <label className="tp-field-label" htmlFor="location">
            Area
          </label>
          <SelectField
            id="location"
            name="location"
            required
            defaultValue={defaultCity}
            options={cities.map((c) => ({ value: c, label: c }))}
          />
        </div>
        <div className="tp-field">
          <label className="tp-field-label" htmlFor="min_rating">
            Minimum rating
          </label>
          <input
            id="min_rating"
            name="min_rating"
            type="range"
            className="tp-rating-slider"
            min={0}
            max={5}
            step={0.1}
            defaultValue={initial.minRating}
            onInput={(e) => {
              const el = e.currentTarget.parentElement?.querySelector(".tp-rating-value");
              if (el) {
                el.innerHTML = `${Number(e.currentTarget.value).toFixed(1)} <span class="tp-rating-star">★</span>`;
              }
            }}
          />
          <div
            className="tp-rating-value"
            dangerouslySetInnerHTML={{
              __html: `${initial.minRating.toFixed(1)} <span class="tp-rating-star">★</span>`,
            }}
          />
        </div>
      </div>

      <div className="tp-form-gap" />

      <div className="tp-form-row tp-form-row-budget">
        <div className="tp-field">
          <span className="tp-field-label">Budget range</span>
          <div className="tp-budget-tray">
            {BUDGET_OPTIONS.map((opt) => (
              <label key={opt.value} className="tp-budget-option">
                <input
                  type="radio"
                  name="budget"
                  value={opt.value}
                  defaultChecked={initial.budget === opt.value}
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>
        <div className="tp-field">
          <label className="tp-field-label" htmlFor="top_k">
            Number of results
          </label>
          <SelectField
            id="top_k"
            name="top_k"
            defaultValue={String(initial.topK)}
            options={RESULT_COUNTS.map((n) => ({ value: String(n), label: String(n) }))}
          />
        </div>
      </div>

      <div className="tp-form-gap" />

      <div className="tp-field">
        <label className="tp-field-label" htmlFor="cuisine">
          Preferred cuisines
        </label>
        <SelectField
          id="cuisine"
          name="cuisine"
          required
          defaultValue={initial.cuisineLabel}
          options={cuisineLabels.map((label) => ({ value: label, label }))}
        />
      </div>

      <div className="tp-form-gap" />

      <div className="tp-field">
        <label className="tp-field-label" htmlFor="additional">
          Additional preferences
        </label>
        <textarea
          id="additional"
          name="additional"
          className="tp-textarea"
          placeholder="Describe your perfect dining experience..."
          maxLength={maxAdditionalChars}
          defaultValue={initial.additional}
        />
      </div>

      <div className="tp-form-gap" />

      <div className="tp-field">
        <label className="tp-field-label" htmlFor="mood">
          Mood / occasion
        </label>
        <SelectField
          id="mood"
          name="mood"
          defaultValue={initial.mood}
          options={MOOD_OPTIONS.map((m) => ({ value: m.value, label: m.label }))}
        />
      </div>

      <div className="tp-form-gap tp-form-gap-lg" />

      <button type="submit" className="tp-btn-primary">
        ✨ Get AI Recommendations
      </button>
    </form>
  );
}
