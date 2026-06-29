import type { Finding } from "@/lib/types";
import { FINDINGS_META } from "@/lib/findings-meta";

const STATE_CONFIG = {
  yes: { icon: "✅", border: "border-green-800", bg: "bg-green-950/40", label: "통과" },
  partial: { icon: "⚠️", border: "border-amber-800", bg: "bg-amber-950/40", label: "부분" },
  no: { icon: "❌", border: "border-red-800", bg: "bg-red-950/40", label: "미흡" },
  unknown: { icon: "🔘", border: "border-slate-700", bg: "bg-slate-900/40", label: "확인불가" },
};

export default function FindingCard({ finding }: { finding: Finding }) {
  const cfg = STATE_CONFIG[finding.state];
  const meta = FINDINGS_META[finding.item_id];

  return (
    <div className={`rounded-2xl border ${cfg.border} ${cfg.bg} p-5 space-y-2`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{cfg.icon}</span>
          <span className="text-white font-semibold text-sm">
            {meta?.title ?? finding.label}
          </span>
        </div>
        <span className="text-xs text-slate-400 font-medium">{cfg.label}</span>
      </div>

      {finding.evidence && (
        <p className="text-slate-400 text-xs font-mono bg-slate-800/60 rounded-lg px-3 py-2 break-all">
          {finding.evidence}
        </p>
      )}

      {meta && (
        <p className="text-slate-300 text-xs">{meta.whyItMatters}</p>
      )}

      {meta && finding.state !== "yes" && finding.state !== "unknown" && (
        <div className="bg-indigo-950/60 border border-indigo-800 rounded-lg px-3 py-2">
          <p className="text-indigo-300 text-xs">
            <span className="font-semibold">개선 팁: </span>
            {meta.improveTip}
          </p>
        </div>
      )}
    </div>
  );
}
