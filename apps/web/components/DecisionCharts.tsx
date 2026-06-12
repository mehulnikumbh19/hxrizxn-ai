"use client";

import dynamic from "next/dynamic";
import type { AnalysisPackage } from "@/lib/types";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

const scoreNames = ["Upside", "Downside", "Regret", "Reverse", "Options"];

/* Fluent 2 light chart palette */
const textMuted = "#616161";
const textStrong = "#242424";
const gridLine = "rgba(0, 0, 0, 0.08)";
const brandBlue = "#0f6cbd";
const accentPurple = "#5b5fc7";
const successGreen = "#107c10";
const dangerRed = "#d13438";

export function RadarChart({ data }: { data: AnalysisPackage }) {
  const seriesColors = [successGreen, brandBlue, dangerRed];
  const option = {
    backgroundColor: "transparent",
    tooltip: {},
    legend: { textStyle: { color: textMuted }, top: 0 },
    color: seriesColors,
    radar: {
      indicator: scoreNames.map((name) => ({ name, max: 100 })),
      radius: "55%",
      center: ["53%", "58%"],
      axisName: { color: textMuted },
      splitLine: { lineStyle: { color: gridLine } },
      splitArea: { areaStyle: { color: ["rgba(15,108,189,0.03)", "rgba(91,95,199,0.05)"] } }
    },
    series: [
      {
        type: "radar",
        data: data.scenarios.map((scenario, index) => ({
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
          ],
          areaStyle: { opacity: 0.14 },
          lineStyle: { width: 2, color: seriesColors[index] },
          itemStyle: { color: seriesColors[index] }
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
    grid: { top: 16, right: 20, bottom: 76, left: 168 },
    xAxis: { type: "category", data: scenarios, axisLabel: { color: textMuted } },
    yAxis: { type: "category", data: risks, axisLabel: { color: textMuted } },
    visualMap: {
      min: 0,
      max: 4,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      text: ["severe", "none"],
      textStyle: { color: textMuted },
      inRange: { color: ["#f3f2f1", "#a9d3f2", "#f8c886", "#dc626d"] }
    },
    series: [
      {
        type: "heatmap",
        data: values,
        label: { show: true, color: textStrong },
        itemStyle: { borderColor: "#ffffff", borderWidth: 2, borderRadius: 4 }
      }
    ]
  };
  return <ReactECharts option={option} style={{ height: 360 }} />;
}

export function ImpactStack({ data }: { data: AnalysisPackage }) {
  const domains = [...new Set(data.impacts.map((impact) => impact.domain))];
  const barColors = [brandBlue, accentPurple, "#9ea2f0"];
  const option = {
    tooltip: { trigger: "axis" },
    legend: { data: ["1st order", "2nd order", "3rd order"], textStyle: { color: textMuted }, top: 0 },
    color: barColors,
    grid: { top: 42, right: 20, bottom: 78, left: 40 },
    xAxis: {
      type: "category",
      data: domains,
      axisLabel: { color: textMuted, rotate: 24, fontSize: 11 },
      axisLine: { lineStyle: { color: gridLine } }
    },
    yAxis: {
      type: "value",
      axisLabel: { color: textMuted },
      splitLine: { lineStyle: { color: gridLine } }
    },
    series: [1, 2, 3].map((order, index) => ({
      name: `${order}${order === 1 ? "st" : order === 2 ? "nd" : "rd"} order`,
      type: "bar",
      stack: "impact",
      barMaxWidth: 34,
      itemStyle: { color: barColors[index], borderRadius: order === 3 ? [4, 4, 0, 0] : 0 },
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
    grid: { top: 24, right: 36, bottom: 52, left: 56 },
    xAxis: {
      min: 0, max: 100, name: "Reversibility",
      axisLabel: { color: textMuted },
      nameTextStyle: { color: textMuted },
      axisLine: { lineStyle: { color: gridLine } },
      splitLine: { lineStyle: { color: "rgba(0,0,0,0.05)" } }
    },
    yAxis: {
      min: 0, max: 100, name: "Optionality",
      axisLabel: { color: textMuted },
      nameTextStyle: { color: textMuted },
      axisLine: { lineStyle: { color: gridLine } },
      splitLine: { lineStyle: { color: "rgba(0,0,0,0.05)" } }
    },
    series: [
      {
        type: "scatter",
        symbolSize: 22,
        itemStyle: {
          color: accentPurple,
          shadowBlur: 10,
          shadowColor: "rgba(91,95,199,0.35)"
        },
        data: data.scenarios.map((scenario) => [
          scenario.reversibility_score,
          scenario.optionality_score,
          scenario.scenario_name
        ]),
        label: {
          show: true,
          formatter: (params: { data: [number, number, string] }) => params.data[2],
          color: textStrong,
          fontSize: 11,
          position: "right"
        }
      }
    ]
  };
  return <ReactECharts option={option} style={{ height: 320 }} />;
}
