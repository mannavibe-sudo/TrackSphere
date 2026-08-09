import ReactECharts from "echarts-for-react";
import { revenueTrend, formatINR } from "../lib/mockData";

export default function RevenueChart() {
  const option = {
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
    tooltip: {
      trigger: "axis",
      valueFormatter: (v) => formatINR(v),
      textStyle: { fontFamily: "JetBrains Mono, monospace", fontSize: 12 },
    },
    legend: {
      data: ["Revenue", "Transport Cost"],
      top: 0,
      textStyle: { fontFamily: "Inter, sans-serif", fontSize: 12, color: "#5B6472" },
    },
    xAxis: {
      type: "category",
      data: revenueTrend.map((d) => d.month),
      axisLine: { lineStyle: { color: "#12203B1a" } },
      axisLabel: { fontFamily: "Inter, sans-serif", color: "#5B6472" },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        formatter: (v) => `${(v / 100000).toFixed(0)}L`,
        fontFamily: "JetBrains Mono, monospace",
        color: "#5B6472",
      },
      splitLine: { lineStyle: { color: "#12203B0d" } },
    },
    series: [
      {
        name: "Revenue",
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { color: "#F5A623", width: 2.5 },
        itemStyle: { color: "#F5A623" },
        areaStyle: { color: "#F5A62314" },
        data: revenueTrend.map((d) => d.revenue),
      },
      {
        name: "Transport Cost",
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { color: "#0E7C7B", width: 2.5 },
        itemStyle: { color: "#0E7C7B" },
        data: revenueTrend.map((d) => d.cost),
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: 280 }} />;
}
