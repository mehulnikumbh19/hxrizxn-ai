"use client";

import dynamic from "next/dynamic";
import type { AnalysisPackage } from "@/lib/types";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

const scoreNames = ["Upside", "Downside", "Regret", "Reverse", "Options"];

export function RadarChart({ data }: { data: AnalysisPackage }) {
  const option = {
    backgroundColor: "transparent",
    tooltip: {},
    legend: { textStyle: { color: "#cbd5e1" }, top: 0 },
    radar: {
      indicator: scoreNames.map((name) => ({ name, max: 100 })),
      radius: "55%",
      center: ["53%", "58%"],
      axisName: { color: "#cbd5e1" },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.12)" } },
      splitArea: { areaStyle: { color: ["rgba(255,255,255,0.02)", "rgba(255,255,255,0.05)"] } }
    },
    series: [
      {
        type: "radar",
        data: data.scenarios.map((scenario) => ({
          name:
            scenario.scenario_key === "optimistic"
              ? "Upside branch"
              : scenario.scenario_key === "base"
                ? "Base branch"
                : "Stress branch",
          value: [
            scenario.upside_score,
            scenario.downside_score,
            scenario.regret_score,
            scenario.reversibility_score,
            scenario.optionality_score
          ]
        }))
      }
    ]
  };
  return <ReactECharts option={option} style={{ height: 340 }} />;
}

export function RiskHeatmap({ data }: { data: AnalysisPackage }) {
  const scenarios = data.scenarios.map((scenario) => scenario.scenario_key);
  const risks = [...new Set(data.risks.map((risk) => risk.risk_name))].slice(0, 8);
  const severity = { low: 1, medium: 2, high: 3, very_high: 4 };
  const values = risks.flatMap((riskName, y) =>
    scenarios.map((scenario, x) => {
      const risk = data.risks.find((item) => item.risk_name === riskName && item.scenario_key === scenario);
      return [x, y, risk ? severity[risk.severity_band] : 0];
    })
  );
  const option = {
    tooltip: {},
    grid: { top: 20, right: 20, bottom: 70, left: 160 },
    xAxis: { type: "category", data: scenarios, axisLabel: { color: "#cbd5e1" } },
    yAxis: { type: "category", data: risks, axisLabel: { color: "#cbd5e1" } },
    visualMap: {
      min: 0,
      max: 4,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      textStyle: { color: "#cbd5e1" },
      inRange: { color: ["#172033", "#50e3c2", "#f4b95f", "#ff6b8a"] }
    },
    series: [{ type: "heatmap", data: values, label: { show: true, color: "#fff" } }]
  };
  return <ReactECharts option={option} style={{ height: 360 }} />;
}

export function ImpactStack({ data }: { data: AnalysisPackage }) {
  const domains = [...new Set(data.impacts.map((impact) => impact.domain))];
  const option = {
    tooltip: { trigger: "axis" },
    legend: { data: ["1st order", "2nd order", "3rd order"], textStyle: { color: "#cbd5e1" } },
    grid: { top: 48, right: 20, bottom: 50, left: 40 },
    xAxis: { type: "category", data: domains, axisLabel: { color: "#cbd5e1", rotate: 20 } },
    yAxis: { type: "value", axisLabel: { color: "#cbd5e1" } },
    series: [1, 2, 3].map((order) => ({
      name: `${order}${order === 1 ? "st" : order === 2 ? "nd" : "rd"} order`,
      type: "bar",
      stack: "impact",
      data: domains.map((domain) =>
        data.impacts
          .filter((impact) => impact.domain === domain && impact.order_level === order)
          .reduce((sum, impact) => sum + impact.severity, 0)
      )
    }))
  };
  return <ReactECharts option={option} style={{ height: 340 }} />;
}

export function OptionalityQuadrant({ data }: { data: AnalysisPackage }) {
  const option = {
    tooltip: {},
    grid: { top: 20, right: 30, bottom: 50, left: 55 },
    xAxis: { min: 0, max: 100, name: "Reversibility", axisLabel: { color: "#cbd5e1" }, nameTextStyle: { color: "#cbd5e1" } },
    yAxis: { min: 0, max: 100, name: "Optionality", axisLabel: { color: "#cbd5e1" }, nameTextStyle: { color: "#cbd5e1" } },
    series: [
      {
        type: "scatter",
        symbolSize: 24,
        data: data.scenarios.map((scenario) => [
          scenario.reversibility_score,
          scenario.optionality_score,
          scenario.scenario_name
        ]),
        label: {
          show: true,
          formatter: (params: { data: [number, number, string] }) => params.data[2],
          color: "#fff",
          position: "right"
        }
      }
    ]
  };
  return <ReactECharts option={option} style={{ height: 320 }} />;
}
