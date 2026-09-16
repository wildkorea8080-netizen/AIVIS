import { cookies } from "next/headers";

const COOKIE_NAME = "aivis_projects";
const MAX_TOKENS = 10;
const ONE_YEAR = 60 * 60 * 24 * 365;

/**
 * 이 브라우저가 만든 프로젝트의 소유 토큰 목록.
 *
 * 계정이 없으므로 "내 프로젝트"를 알아내는 유일한 단서다. 토큰만 담고
 * 이름은 넣지 않는다 — 금방 낡고, 쿠키 용량만 잡아먹는다.
 */
export function readProjectTokens(): string[] {
  const raw = cookies().get(COOKIE_NAME)?.value;
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((t): t is string => typeof t === "string").slice(0, MAX_TOKENS);
  } catch {
    return [];
  }
}

/**
 * 토큰을 목록 맨 앞에 기록한다.
 *
 * 서버 액션이나 라우트 핸들러에서만 호출할 수 있다 —
 * 서버 컴포넌트 렌더 중 쿠키 쓰기는 Next가 막는다.
 */
export function rememberProjectToken(token: string): void {
  const next = [token, ...readProjectTokens().filter((t) => t !== token)].slice(0, MAX_TOKENS);
  cookies().set(COOKIE_NAME, JSON.stringify(next), {
    httpOnly: true,                                  // 조회는 전부 서버에서 하므로 JS 접근이 필요 없다
    secure: process.env.NODE_ENV === "production",   // 로컬 http에서도 저장되도록
    sameSite: "lax",
    path: "/",
    maxAge: ONE_YEAR,
  });
}
