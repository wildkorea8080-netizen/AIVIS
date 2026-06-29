"use server";

import { redirect } from "next/navigation";
import { submitAudit } from "@/lib/api";
import { encodeReport } from "@/lib/report-codec";

export async function runAudit(formData: FormData) {
  const url = (formData.get("url") as string) || undefined;
  const place_name = (formData.get("place_name") as string) || undefined;
  const region = (formData.get("region") as string) || undefined;
  const mode = formData.get("mode") === "local" ? "local" : "brand";

  if (mode === "brand" && !url) throw new Error("온라인 브랜드 진단은 URL이 필요합니다.");
  if (mode === "local" && !place_name) throw new Error("오프라인 매장 진단은 매장명이 필요합니다.");

  const report = await submitAudit({ url, place_name, region, mode });

  if (report.share_id) {
    redirect(`/report/${report.share_id}`);
  } else {
    const encoded = encodeReport(report);
    redirect(`/report?d=${encoded}`);
  }
}
