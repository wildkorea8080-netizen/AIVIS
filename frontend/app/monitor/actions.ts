"use server";

import { redirect } from "next/navigation";
import { createProject, addQuestion, runMonitor } from "@/lib/monitor-api";

export async function createProjectAction(formData: FormData) {
  const project = await createProject({
    name: formData.get("name") as string,
    target_url: formData.get("target_url") as string,
    mode: (formData.get("mode") as string) || "brand",
    brand_keyword: formData.get("brand_keyword") as string,
    owner_email: (formData.get("owner_email") as string) || undefined,
  });
  redirect(`/monitor/${project.id}`);
}

export async function addQuestionAction(projectId: number, formData: FormData) {
  const question = formData.get("question") as string;
  if (!question?.trim()) return;
  await addQuestion(projectId, question.trim());
  redirect(`/monitor/${projectId}`);
}

export async function runMonitorAction(projectId: number): Promise<void> {
  await runMonitor(projectId);
  redirect(`/monitor/${projectId}`);
}
