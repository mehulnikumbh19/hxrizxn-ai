import { describe, expect, it } from "vitest";
import { fallbackPackage } from "../lib/api";

describe("fallback package", () => {
  it("contains the three required HORIZON-X scenarios", () => {
    expect(fallbackPackage.scenarios.map((scenario) => scenario.scenario_key)).toEqual([
      "optimistic",
      "base",
      "stress"
    ]);
    expect(fallbackPackage.memo.recommendation_summary).toContain("experiment");
  });
});

