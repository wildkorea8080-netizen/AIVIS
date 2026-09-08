from __future__ import annotations

import httpx
from xml.etree import ElementTree

from app.collectors.base import AuditContext, BaseCollector
from app.models.schemas import Finding, SignalResult


class SitemapCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        item_id = "l_sitemap" if ctx.mode == "local" else "b_sitemap"
        label = "사이트맵(sitemap.xml)"

        if not ctx.origin:
            return SignalResult(
                collector="sitemap",
                status="ok",
                findings=[Finding(item_id=item_id, label=label,
                                  state="unknown", evidence="URL 미입력")],
            )

        # robots.txt에서 sitemap 경로 우선 탐색
        sitemap_url = f"{ctx.origin}/sitemap.xml"
        try:
            robots_resp = await ctx.client.get(f"{ctx.origin}/robots.txt", follow_redirects=True)
            if robots_resp.status_code == 200:
                for line in robots_resp.text.splitlines():
                    if line.lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

        try:
            resp = await ctx.client.get(sitemap_url, follow_redirects=True)
        except httpx.TimeoutException as e:
            return SignalResult(collector="sitemap", status="error", findings=[], error=f"타임아웃: {e}")
        except Exception as e:
            return SignalResult(collector="sitemap", status="error", findings=[], error=str(e))

        if resp.status_code == 404:
            return SignalResult(
                collector="sitemap",
                status="ok",
                findings=[Finding(item_id=item_id, label=label,
                                  state="no", evidence="sitemap.xml 없음")],
            )
        if resp.status_code != 200:
            return SignalResult(
                collector="sitemap",
                status="ok",
                findings=[Finding(item_id=item_id, label=label,
                                  state="unknown", evidence=f"HTTP {resp.status_code}")],
            )

        # XML 파싱으로 URL 수 확인
        try:
            root = ElementTree.fromstring(resp.text)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = root.findall(".//sm:url", ns) or root.findall(".//url")
            url_count = len(urls)

            if url_count >= 5:
                state, evidence = "yes", f"{url_count}개 URL 등록됨"
            elif url_count >= 1:
                state, evidence = "partial", f"{url_count}개 URL (5개 이상 권장)"
            else:
                state, evidence = "partial", "sitemap 존재하나 URL 없음"
        except ElementTree.ParseError:
            state, evidence = "partial", "sitemap 존재하나 XML 파싱 실패"

        return SignalResult(
            collector="sitemap",
            status="ok",
            findings=[Finding(item_id=item_id, label=label, state=state, evidence=evidence)],
            raw={"sitemap_url": sitemap_url},
        )
