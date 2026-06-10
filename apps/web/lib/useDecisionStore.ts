import { create } from "zustand";
import type { AnalysisPackage } from "./types";

type Screen = "landing" | "intake" | "loading" | "comparison" | "ripple" | "experiment" | "memo";

type DecisionState = {
  screen: Screen;
  packageData: AnalysisPackage | null;
  setScreen: (screen: Screen) => void;
  setPackageData: (packageData: AnalysisPackage | null) => void;
};

export const useDecisionStore = create<DecisionState>((set) => ({
  screen: "landing",
  packageData: null,
  setScreen: (screen) => set({ screen }),
  setPackageData: (packageData) => set({ packageData })
}));

