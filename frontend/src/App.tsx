import { useCallback, useEffect, useState } from "react";
import {
  cuisineOptions,
  fetchCuisines,
  fetchLocations,
  postRecommendations,
} from "./api/client";
import { LOADING_MIN_MS } from "./constants";
import { Alert } from "./components/Alert";
import { EmptyState } from "./components/EmptyState";
import { Footer } from "./components/Footer";
import { Hero } from "./components/Hero";
import { LoadingOverlay } from "./components/LoadingOverlay";
import { Nav } from "./components/Nav";
import { PreferencesForm, type FormState } from "./components/PreferencesForm";
import { ResultsView } from "./components/ResultsView";
import type {
  AppPhase,
  PreferencesPayload,
  RecommendationResponse,
} from "./types";

const DEFAULT_FORM: FormState = {
  location: "",
  budget: "medium",
  cuisineLabel: "Italian",
  minRating: 2.9,
  topK: 5,
  mood: "",
  additional: "",
};

export default function App() {
  const [phase, setPhase] = useState<AppPhase>("home");
  const [cities, setCities] = useState<string[]>([]);
  const [cuisineLabels, setCuisineLabels] = useState<string[]>([]);
  const [cuisineLabelToRaw, setCuisineLabelToRaw] = useState<Record<string, string>>({});
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [payload, setPayload] = useState<PreferencesPayload | null>(null);
  const [cuisineDisplay, setCuisineDisplay] = useState("");
  const [response, setResponse] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState("");

  const loadMetadata = useCallback(async () => {
    try {
      const [loc, rawCuisines] = await Promise.all([fetchLocations(), fetchCuisines()]);
      setCities(loc);
      const { labels, labelToRaw } = cuisineOptions(rawCuisines);
      setCuisineLabels(labels);
      setCuisineLabelToRaw(labelToRaw);
      if (!loc.length && !rawCuisines.length) {
        setPhase("data_unavailable");
      }
    } catch {
      setPhase("data_unavailable");
    }
  }, []);

  useEffect(() => {
    loadMetadata();
  }, [loadMetadata]);

  const resetHome = () => {
    setPhase("home");
    setPayload(null);
    setResponse(null);
    setError("");
  };

  const runRecommendation = async (body: PreferencesPayload, display: string) => {
    setPayload(body);
    setCuisineDisplay(display);
    setPhase("loading");
    setError("");
    const started = Date.now();
    try {
      const [result] = await Promise.all([
        postRecommendations(body),
        new Promise((r) => setTimeout(r, LOADING_MIN_MS)),
      ]);
      const elapsed = Date.now() - started;
      if (elapsed < LOADING_MIN_MS) {
        await new Promise((r) => setTimeout(r, LOADING_MIN_MS - elapsed));
      }
      setResponse(result);
      setPhase(result.recommendations.length ? "results" : "empty");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
      setPhase("error");
    }
  };

  const handleEmptyChip = (chip: string) => {
    setForm((prev) => {
      const next = { ...prev };
      if (chip === "lower_rating") {
        next.minRating = Math.max(0, prev.minRating - 0.5);
      }
      if (chip === "expand_budget") {
        const order = ["low", "medium", "high"] as const;
        const idx = order.indexOf(prev.budget);
        next.budget = order[Math.min(2, idx + 1)];
      }
      return next;
    });
    resetHome();
  };

  if (phase === "loading") {
    return (
      <div className="tp-app">
        <LoadingOverlay />
      </div>
    );
  }

  return (
    <div className="tp-app">
      <div className="tp-page">
        <Nav />
        {(phase === "home" || phase === "error" || phase === "data_unavailable") && <Hero />}

        {phase === "data_unavailable" && (
          <Alert
            kind="error"
            title="Data unavailable"
            body="We could not load the restaurant catalog. Check your data path and try again."
            onRetry={() => {
              loadMetadata();
              setPhase("home");
            }}
          />
        )}

        {phase === "error" && (
          <>
            <Alert
              kind="error"
              title="Something went wrong"
              body={error}
              onRetry={() => payload && runRecommendation(payload, cuisineDisplay)}
            />
            <button type="button" className="tp-btn-secondary" style={{ display: "block", margin: "1rem auto" }} onClick={resetHome}>
              Adjust filters
            </button>
          </>
        )}

        {phase === "empty" && <EmptyState onChip={handleEmptyChip} />}

        {phase === "results" && response && payload && (
          <ResultsView
            response={response}
            payload={payload}
            cuisineDisplay={cuisineDisplay}
            onAdjust={resetHome}
            onAgain={resetHome}
          />
        )}

        {phase === "home" && cities.length > 0 && (
          <PreferencesForm
            cities={cities}
            cuisineLabels={cuisineLabels}
            cuisineLabelToRaw={cuisineLabelToRaw}
            initial={form}
            maxAdditionalChars={500}
            onSubmit={(p, display) => {
              setForm({
                location: p.location,
                budget: p.budget,
                cuisineLabel: display,
                minRating: p.min_rating,
                topK: p.top_k,
                mood: p.mood ?? "",
                additional: p.additional_preferences ?? "",
              });
              runRecommendation(p, display);
            }}
          />
        )}

        <Footer />
      </div>
    </div>
  );
}
