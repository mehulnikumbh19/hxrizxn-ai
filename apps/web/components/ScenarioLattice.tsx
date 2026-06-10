"use client";

import dynamic from "next/dynamic";
import type { Edge, Node } from "@xyflow/react";
import type { ScenarioSpec } from "@/lib/types";

const ReactFlow = dynamic(() => import("@xyflow/react").then((mod) => mod.ReactFlow), {
  ssr: false
});
const Background = dynamic(() => import("@xyflow/react").then((mod) => mod.Background), {
  ssr: false
});

export function ScenarioLattice({ scenarios }: { scenarios: ScenarioSpec[] }) {
  const nodes: Node[] = [
    {
      id: "decision",
      position: { x: 20, y: 110 },
      data: { label: "Decision" },
      style: { width: 120, height: 48, borderColor: "#50e3c2" }
    },
    ...scenarios.map((scenario, index) => ({
      id: scenario.scenario_key,
      position: { x: 230, y: index * 92 + 28 },
      data: { label: `${scenario.scenario_name}\n${scenario.probability_band}` },
      style: {
        width: 230,
        height: 66,
        whiteSpace: "pre-line",
        borderColor:
          scenario.scenario_key === "stress"
            ? "#ff6b8a"
            : scenario.scenario_key === "base"
              ? "#50e3c2"
              : "#f4b95f"
      }
    }))
  ];
  const edges: Edge[] = scenarios.map((scenario) => ({
    id: `decision-${scenario.scenario_key}`,
    source: "decision",
    target: scenario.scenario_key,
    animated: scenario.scenario_key === "base",
    style: { stroke: scenario.scenario_key === "stress" ? "#ff6b8a" : "#50e3c2" }
  }));
  return (
    <div className="h-[330px] min-h-[330px] overflow-hidden rounded-lg border border-white/10 bg-black/20">
      <ReactFlow nodes={nodes} edges={edges} fitView nodesDraggable={false} zoomOnScroll={false}>
        <Background color="rgba(255,255,255,0.12)" gap={22} />
      </ReactFlow>
    </div>
  );
}

