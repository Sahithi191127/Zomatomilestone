export type BudgetBand = "low" | "medium" | "high";

export type AppPhase =
  | "home"
  | "loading"
  | "results"
  | "empty"
  | "error"
  | "data_unavailable";

export interface Restaurant {
  id: string;
  name: string;
  location: string;
  cuisines: string[];
  rating: number;
  estimated_cost: number;
  budget_band: BudgetBand;
  metadata?: Record<string, unknown>;
}

export interface Recommendation {
  rank: number;
  restaurant: Restaurant;
  explanation: string;
}

export interface RecommendationMeta {
  candidates_considered: number;
  filters_applied: string[];
  fallback_used: boolean;
  llm_model?: string | null;
}

export interface RecommendationResponse {
  summary: string | null;
  recommendations: Recommendation[];
  meta: RecommendationMeta;
}

export interface PreferencesPayload {
  location: string;
  budget: BudgetBand;
  cuisine: string;
  min_rating: number;
  top_k: number;
  mood?: string | null;
  additional_preferences?: string | null;
}

export interface ApiErrorBody {
  message?: string;
  field?: string;
  suggestions?: string[];
}
