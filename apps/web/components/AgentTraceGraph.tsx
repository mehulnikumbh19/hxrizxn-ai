"use client";

import dynamic from "next/dynamic";
import type { Edge, Node } from "@xyflow/react";
import type { AgentTraceView } from "@/lib/types";

const ReactFlow = dynamic(() => import("@xyflow/react").then((mod) => mod.ReactFlow), {
  ssr: false
});
const Background = dynamic(() => import("@xyflow/react").then((mod) => mod.Background), {
  ssr: false
});

export function AgentTraceGraph({ trace }: { trace: AgentTraceView[] }) {
  const nodes: Node[] = trace.map((item, index) => ({
    id: item.agent_name,
    position: { x: (index % 3) * 250, y: Math.floor(index / 3) * 108 },
    data: { label: `${item.agent_name}\n${item.status} · ${item.latency_ms} ms` },
    style: {
      width: 210,
      height: 62,
      whiteSpace: "pre-line",
      borderColor: item.status === "completed" ? "#50e3c2" : "#f4b95f"
    }
  }));
  const edges: Edge[] = trace.slice(1).map((item, index) => ({
    id: `${trace[index].agent_name}-${item.agent_name}`,
    source: trace[index].agent_name,
    target: item.agent_name,
    animated: true,
    style: { stroke: "#9b5cff" }
  }));
  return (
    <div className="h-[350px] min-h-[350px] overflow-hidden rounded-lg border border-white/10 bg-black/20">
      <ReactFlow nodes={nodes} edges={edges} fitView nodesDraggable={false} zoomOnScroll={false}>
        <Background color="rgba(255,255,255,0.12)" gap={24} />
      </ReactFlow>
    </div>
  );
}

