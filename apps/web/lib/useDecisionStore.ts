import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { AnalysisPackage } from "./types";

type Screen = "landing" | "intake" | "loading" | "comparison" | "ripple" | "experiment" | "memo";

type DecisionState = {
  screen: Screen;
  packageData: AnalysisPackage | null;
  setScreen: (screen: Screen) => void;
  setPackageData: (packageData: AnalysisPackage | null) => void;
};

export const useDecisionStore = create<DecisionState>()(
  persist(
    (set) => ({
      screen: "landing",
      packageData: null,
      setScreen: (screen) => set({ screen }),
      setPackageData: (packageData) => set({ packageData })
    }),
    {
      name: "hxrizxn-decision",
      // Persist within the tab/session only; clears when the tab closes.
      storage: createJSONStorage(() => sessionStorage),
      // Avoid Next.js SSR hydration mismatch: do not read storage on the
      // server render. The client calls rehydrate() from a mount effect.
      skipHydration: true,
      // A refresh during analysis would otherwise restore a "loading" screen
      // with no in-flight request behind it. Send the user back to intake.
      onRehydrateStorage: () => (state) => {
        if (state && state.screen === "loading") {
          state.screen = "intake";
        }
      }
    }
  )
);
