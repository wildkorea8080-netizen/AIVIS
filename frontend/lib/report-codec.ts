import type { ReadinessReport } from "./types";

export function encodeReport(report: ReadinessReport): string {
  return Buffer.from(encodeURIComponent(JSON.stringify(report))).toString("base64");
}

export function decodeReport(encoded: string): ReadinessReport {
  return JSON.parse(decodeURIComponent(Buffer.from(encoded, "base64").toString("utf-8")));
}
