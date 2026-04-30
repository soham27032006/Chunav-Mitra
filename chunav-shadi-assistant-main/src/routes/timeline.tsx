import { createFileRoute } from "@tanstack/react-router";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { CalendarClock, Clock, AlertCircle, Check, RefreshCw } from "lucide-react";
import { Layout } from "@/components/Layout";
import { SectionHeader } from "@/components/SectionHeader";
import { api, type TimelineResponse } from "@/lib/api";
import { useLang, t } from "@/routes/__root";
import { toast } from "sonner";
import { SkeletonTimeline } from "@/components/SkeletonLoader";

export const Route = createFileRoute("/timeline")({
  component: Timeline,
});

function useCounter(target: number, duration = 1200) {
  const [v, setV] = useState(0);
  useEffect(() => {
    if (target === 0) return;
    let start = 0;
    const t0 = performance.now();
    let raf = 0;
    const step = (t: number) => {
      const p = Math.min(1, (t - t0) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setV(Math.round(start + (target - start) * eased));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);
  return v;
}

function Timeline() {
  const { lang } = useLang();
  const [data, setData] = useState<TimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchTimeline = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.timeline();
      setData(res);
    } catch {
      setError(lang === "hi" ? "Timeline load nahi ho payi. Server check karo." : "Could not load timeline. Check server.");
      toast.error(t("toast.apiError", lang), {
        icon: "⚠️",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, [lang]);

  const days = useCounter(data?.days_remaining ?? 0);

  const refreshTimeline = () => {
    fetchTimeline();
    toast.success(lang === "hi" ? "Timeline refresh ho gayi!" : "Timeline refreshed!", {
      icon: "🔄",
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <Layout hideFooter>
        <div className="mx-auto max-w-5xl px-4 py-10">
          <div className="flex items-center justify-between">
            <SectionHeader
              eyebrow={lang === "hi" ? "Shaadi Ka Schedule" : "Shaadi Ka Schedule"}
              title={t("timeline.title", lang)}
              subtitle={t("timeline.subtitle", lang)}
            />
            <button
              onClick={refreshTimeline}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-full border border-gold/30 bg-navy/40 px-4 py-2 text-sm text-gold transition hover:bg-gold/10 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              {lang === "hi" ? "Refresh" : "Refresh"}
            </button>
          </div>

          {error && (
            <div className="mb-6 rounded-2xl border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}

          {loading && !data && <SkeletonTimeline />}

          {data && !loading && (
            <>
              {/* Countdown */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="relative mb-10 overflow-hidden rounded-3xl glass-strong p-8 shadow-glow md:p-12"
              >
                <div
                  className="absolute inset-0 -z-0 opacity-30"
                  style={{ background: "var(--gradient-glow)" }}
                />
                <div className="relative grid items-center gap-6 md:grid-cols-3">
                  <div className="md:col-span-2">
                    <div className="text-[10px] uppercase tracking-widest text-gold/70">
                      {t("timeline.currentPhase", lang)}
                    </div>
                    <h3 className="mt-1 font-display text-3xl text-gradient-gold md:text-4xl">
                      {data.current_phase}
                    </h3>
                    <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-gold/30 bg-navy/40 px-3 py-1 text-xs text-cream/80">
                      <Clock className="h-3.5 w-3.5 text-gold" />
                      {t("timeline.next", lang)}: {data.next_deadline}
                    </div>
                  </div>
                  <div className="text-center md:text-right">
                    <div className="text-[10px] uppercase tracking-widest text-gold/70">
                      {t("timeline.daysRemaining", lang)}
                    </div>
                    <div className="font-display text-7xl font-bold text-gradient-gold animate-shimmer-text md:text-8xl">
                      {days}
                    </div>
                    <div className="text-xs text-cream/60">{lang === "hi" ? "din bache" : "days remaining"}</div>
                  </div>
                </div>
              </motion.div>

              {/* Phases */}
              <div className="relative">
                <div className="absolute left-6 top-0 h-full w-px bg-gradient-to-b from-gold/0 via-gold/50 to-gold/0 md:left-1/2" />
                <div className="space-y-8">
                  {data.phases.map((p, i) => {
                    const isCurrent = data.current_phase
                      .toLowerCase()
                      .includes(p.name.toLowerCase());
                    const isLeft = i % 2 === 0;
                    return (
                      <motion.div
                        key={p.phase}
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-50px" }}
                        transition={{ delay: i * 0.08, ease: [0.22, 1, 0.36, 1] }}
                        className={`relative grid items-center gap-4 md:grid-cols-2 ${
                          isLeft ? "" : "md:[&>*:first-child]:order-2"
                        }`}
                      >
                        <div className={isLeft ? "md:pr-12 md:text-right" : "md:pl-12"}>
                          <div className="ml-14 md:ml-0">
                            <div
                              className={`rounded-3xl border p-5 transition ${
                                isCurrent
                                  ? "border-gold bg-gold/10 shadow-glow"
                                  : "border-gold/20 bg-navy/40"
                              }`}
                            >
                              <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-gold/70">
                                {isCurrent ? (
                                  <AlertCircle className="h-3 w-3 text-gold" />
                                ) : (
                                  <Check className="h-3 w-3" />
                                )}
                                {lang === "hi" ? "Chharan" : "Phase"} {p.phase}
                              </div>
                              <h4 className="mt-1 font-display text-xl text-gold">
                                {p.name}
                              </h4>
                              <div className="mt-1 text-xs text-cream/60">{p.date}</div>
                              <p className="mt-2 text-sm text-cream/80">{p.description}</p>
                            </div>
                          </div>
                        </div>

                        {/* Dot */}
                        <div className="absolute left-6 -translate-x-1/2 md:left-1/2">
                          <motion.div
                            animate={
                              isCurrent
                                ? { scale: [1, 1.3, 1], boxShadow: ["0 0 20px #FFD700", "0 0 40px #FFD700", "0 0 20px #FFD700"] }
                                : {}
                            }
                            transition={{ duration: 2, repeat: Infinity }}
                            className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
                              isCurrent
                                ? "border-gold bg-mandap text-navy"
                                : "border-gold/40 bg-navy text-gold/70"
                            }`}
                          >
                            <CalendarClock className="h-4 w-4" />
                          </motion.div>
                        </div>

                        <div className={`hidden md:block ${isLeft ? "" : "md:order-1"}`} />
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      </Layout>
    </motion.div>
  );
}
