import * as React from "react";
import { cn } from "../lib/cn";
import { Badge } from "./Badge";
import { ConfidenceBadge } from "./ConfidenceBadge";
import type { EvidenceBundle } from "../types";

export interface EvidenceDrawerProps {
  open: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  evidence: EvidenceBundle | null;
  confidence?: number;
  summaryBody?: string;
  className?: string;
}

const TIER_LABELS = [
  "Tier 1 - Git evidence",
  "Tier 2 - Structural inference",
  "Tier 3 - Runtime / app signals",
  "Tier 4 - Model inference",
] as const;

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  open,
  onClose,
  title,
  subtitle,
  evidence,
  confidence,
  summaryBody,
  className,
}) => {
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <div
      className={cn(
        "fixed inset-0 z-40 pointer-events-none transition-opacity",
        open ? "opacity-100 pointer-events-auto" : "opacity-0",
      )}
      aria-hidden={!open}
    >
      <button
        aria-label="Close evidence panel"
        onClick={onClose}
        className={cn(
          "absolute inset-0 bg-black/50 backdrop-blur-[1px] transition-opacity",
          open ? "opacity-100" : "opacity-0",
        )}
      />
      <aside
        role="dialog"
        aria-modal="true"
        className={cn(
          "absolute right-0 top-0 h-full w-full max-w-[520px] bg-bg-base border-l border-white/10 shadow-2xl overflow-y-auto transition-transform",
          open ? "translate-x-0" : "translate-x-full",
          className,
        )}
      >
        <div className="sticky top-0 z-10 bg-bg-base/95 backdrop-blur border-b border-white/8 px-5 py-4 flex items-start justify-between gap-3">
          <div className="min-w-0">
            {subtitle ? (
              <p className="text-[11px] uppercase tracking-wider text-fg-tertiary mb-1">{subtitle}</p>
            ) : null}
            <h2 className="text-base font-semibold text-fg-primary truncate">
              {title ?? "Evidence"}
            </h2>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {typeof confidence === "number" ? (
              <ConfidenceBadge value={confidence} />
            ) : null}
            <button
              onClick={onClose}
              className="h-8 w-8 inline-flex items-center justify-center rounded-md text-fg-tertiary hover:bg-white/5 hover:text-fg-primary"
              aria-label="Close"
            >
              x
            </button>
          </div>
        </div>

        <div className="px-5 py-5 space-y-6">
          {summaryBody ? (
            <section>
              <h3 className="text-xs font-medium uppercase tracking-wider text-fg-tertiary mb-2">
                Why we think this
              </h3>
              <p className="text-sm text-fg-secondary leading-relaxed whitespace-pre-line">
                {summaryBody}
              </p>
            </section>
          ) : null}

          {evidence ? (
            <>
              <EvidenceTierSection
                label={TIER_LABELS[0]}
                present={evidence.tier1.commit_shas.length > 0 || evidence.tier1.files_touched.length > 0}
                items={[
                  ["Commits", evidence.tier1.commit_shas.map((s) => s.slice(0, 8))],
                  ["Files", evidence.tier1.files_touched],
                  ["Authors", evidence.tier1.authors],
                  ["Branches", evidence.tier1.branches],
                ]}
              />
              <EvidenceTierSection
                label={TIER_LABELS[1]}
                present={
                  evidence.tier2.manifest_features.length > 0 ||
                  evidence.tier2.module_matches.length > 0
                }
                items={[
                  ["Manifest features", evidence.tier2.manifest_features],
                  ["Module matches", evidence.tier2.module_matches],
                  ["Tests touched", evidence.tier2.tests_touched],
                  ["Ownership hints", evidence.tier2.ownership_hints],
                ]}
              />
              <EvidenceTierSection
                label={TIER_LABELS[2]}
                present={
                  evidence.tier3.hook_events.length > 0 ||
                  evidence.tier3.domain_events.length > 0
                }
                items={[
                  ["Hook events", evidence.tier3.hook_events],
                  ["Domain events", evidence.tier3.domain_events],
                  ["Finding refs", evidence.tier3.scan_finding_ids],
                ]}
              />
              <EvidenceTierSection
                label={TIER_LABELS[3]}
                present={evidence.tier4.inferred_capabilities.length > 0}
                items={[
                  ["Model", evidence.tier4.model ? [evidence.tier4.model] : []],
                  ["Inferred capabilities", evidence.tier4.inferred_capabilities],
                ]}
              />
            </>
          ) : (
            <p className="text-sm text-fg-tertiary">No evidence available.</p>
          )}
        </div>
      </aside>
    </div>
  );
};

const EvidenceTierSection: React.FC<{
  label: string;
  present: boolean;
  items: Array<[string, string[]]>;
}> = ({ label, present, items }) => (
  <section>
    <div className="flex items-center justify-between mb-2">
      <h3 className="text-xs font-medium uppercase tracking-wider text-fg-tertiary">{label}</h3>
      {present ? (
        <Badge className="text-state-success border-state-success/30 bg-state-success/10">
          present
        </Badge>
      ) : (
        <Badge className="text-fg-tertiary">absent</Badge>
      )}
    </div>
    {present ? (
      <dl className="space-y-2">
        {items
          .filter(([, vs]) => vs.length > 0)
          .map(([label, vs]) => (
            <div key={label} className="text-sm">
              <dt className="text-fg-tertiary text-xs mb-1">{label}</dt>
              <dd className="flex flex-wrap gap-1">
                {vs.slice(0, 40).map((v) => (
                  <Badge key={v} className="font-mono text-[11px]">
                    {v}
                  </Badge>
                ))}
                {vs.length > 40 ? (
                  <span className="text-fg-tertiary text-xs">and {vs.length - 40} more</span>
                ) : null}
              </dd>
            </div>
          ))}
      </dl>
    ) : (
      <p className="text-sm text-fg-tertiary">No signal in this tier.</p>
    )}
  </section>
);
