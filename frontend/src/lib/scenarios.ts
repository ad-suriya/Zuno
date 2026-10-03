// Demo scenarios (F03). Source of truth: tests/scenarios/scenarios.json; scenarios.json here is a copy
// (backend/tests/test_scenarios.py fails if the two drift apart).

import data from "./scenarios.json";
import type { AssessmentLevel, Channel, Language } from "./types";

export interface Scenario {
  id: string;
  title: Record<Language, string>;
  language: Language;
  channel: Channel;
  story: string;
  follow_ups: string[];
  expected_level: AssessmentLevel;
}

export const SCENARIOS = data as Scenario[];
