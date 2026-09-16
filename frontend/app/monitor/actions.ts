"use server";

import { redirect } from "next/navigation";
import {
  createProject,
  addQuestion,
  runMonitor,
  deleteQuestion,
  deleteProject,
} from "@/lib/monitor-api";
import { rememberProjectToken } from "@/lib/project-cookie";

export async function createProjectAction(formData: FormData) {
  const project = await createProject({
    name: formData.get("name") as string,
    target_url: formData.get("target_url") as string,
    mode: (formData.get("mode") as string) || "brand",
    brand_keyword: formData.get("brand_keyword") as string,
    owner_email: (formData.get("owner_email") as string) || undefined,
  });

  // 계정이 없으므로 이 쿠키가 프로젝트로 돌아올 유일한 길이다.
  // redirect()보다 먼저 기록해야 응답에 Set-Cookie가 실린다.
  rememberProjectToken(project.owner_token);

  redirect(`/monitor/${project.owner_token}`);
}

export async function addQuestionAction(token: string, formData: FormData) {
  const question = formData.get("question") as string;
  if (!question?.trim()) return;
  await addQuestion(token, question.trim());
  redirect(`/monitor/${token}`);
}

export async function runMonitorAction(token: string): Promise<void> {
  await runMonitor(token);
  redirect(`/monitor/${token}`);
}

export async function deleteQuestionAction(token: string, questionId: number): Promise<void> {
  await deleteQuestion(token, questionId);
  redirect(`/monitor/${token}`);
}

export async function deleteProjectAction(token: string): Promise<void> {
  await deleteProject(token);
  redirect("/monitor");
}
