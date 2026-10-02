// Copy of tests/scenarios/scenarios.json (the frontend can't import outside its project).
// backend/tests/test_scenarios.py fails if the two drift apart.
import data from "./scenarios.json";
import type { AssessmentLevel, Channel, Language } from "./types";

export interface Scenario {
  id: string;
  label: string;
  language: Language;
  channel: Channel;
  story: string;
  follow_ups: string[];
  expected_level: AssessmentLevel;
}

export const SCENARIOS = data as Scenario[];
