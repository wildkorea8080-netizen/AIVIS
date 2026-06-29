"use server";

import { redirect } from "next/navigation";
import { submitAudit } from "@/lib/api";
import { encodeReport } from "@/lib/report-codec";

export async function runAudit(formData: FormData) {
  const url = formData.get("url") as string;
  const place_name = (formData.get("place_name") as string) || undefined;
  const region = (formData.get("region") as string) || undefined;
  const mode = formData.get("mode") === "local" ? "local" : "brand";

  if (!url) throw new Error("URL을 입력해주세요.");

  const report = await submitAudit({ url, place_name, region, mode });

  // DB에 저장된 경우 share_id로 짧은 URL 사용, 아니면 base64 fallback
  if (report.share_id) {
    redirect(`/report/${report.share_id}`);
  } else {
    const encoded = encodeReport(report);
    redirect(`/report?d=${encoded}`);
  }
}
