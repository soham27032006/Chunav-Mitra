import * as React from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import confetti from "canvas-confetti";
import { CheckCircle2, XCircle, Loader2, UserCheck, Share2, Copy, ExternalLink } from "lucide-react";
import { Layout } from "@/components/Layout";
import { SectionHeader } from "@/components/SectionHeader";
import { api, type VoterCheckResponse } from "@/lib/api";
import { useLang, t } from "@/routes/__root";
import { toast } from "sonner";
import { SkeletonVoterResult } from "@/components/SkeletonLoader";

export const Route = createFileRoute("/voter-check")({
  component: VoterCheck,
});

const STATES = [
  "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Odisha",
  "Punjab", "Rajasthan", "Tamil Nadu", "Telangana", "Uttar Pradesh",
  "Uttarakhand", "West Bengal",
];

function fireConfetti() {
  const colors = ["#FF6B35", "#FFD700", "#2D6A4F", "#FFF8F0", "#C8A96A"];
  const burst = (origin: { x: number; y: number }) =>
    confetti({
      particleCount: 80,
      spread: 75,
      origin,
      colors,
      scalar: 1.1,
      ticks: 220,
    });
  burst({ x: 0.2, y: 0.4 });
  burst({ x: 0.5, y: 0.3 });
  burst({ x: 0.8, y: 0.4 });
  setTimeout(() => burst({ x: 0.5, y: 0.5 }), 250);
}

function VoterCheck() {
  const { lang } = useLang();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [state, setState] = useState("");
  const [dob, setDob] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VoterCheckResponse | null>(null);
  const [error, setError] = useState("");

  // Keyboard shortcut: "V" to focus this page, "Escape" to close result
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLSelectElement) {
        return;
      }
      if (e.key === "Escape" && result) {
        setResult(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [result]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !state || !dob) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await api.checkVoter({ name, state, dob });
      setResult(res);
      if (res.found) {
        setTimeout(fireConfetti, 100);
        toast.success(t("toast.voterFound", lang), {
          icon: "🎊",
        });
      } else {
        toast.error(t("toast.voterNotFound", lang), {
          icon: "😢",
        });
      }
    } catch {
      setError(lang === "hi" ? "Server se baat nahi ho payi. Thodi der baad try kijiye." : "Could not connect to server. Please try again later.");
      toast.error(t("toast.apiError", lang), {
        icon: "⚠️",
      });
    } finally {
      setLoading(false);
    }
  };

  const shareResult = async () => {
    if (!result?.found || !result.voter_id) return;

    const shareText = lang === "hi"
      ? `🗳️ Main Chunav Mitra ke saath apna vote dene ke liye taiyaar hoon! Voter ID: ${result.voter_id}\nDesh ki sabse badi shaadi mein aap bhi shamil ho! #ChunavMitra #VoteKaro #PromptWars2026`
      : `🗳️ I'm ready to vote with Chunav Mitra! Voter ID: ${result.voter_id}\nJoin the world's biggest wedding! #ChunavMitra #VoteKaro #PromptWars2026`;

    try {
      if (navigator.share) {
        await navigator.share({
          title: "Chunav Mitra - Voter Ready!",
          text: shareText,
        });
        toast.success(t("toast.shareSuccess", lang));
      } else {
        await navigator.clipboard.writeText(shareText);
        toast.success(t("toast.voterIdCopied", lang), {
          icon: "📋",
        });
      }
    } catch {
      // User cancelled or share failed
      try {
        await navigator.clipboard.writeText(shareText);
        toast.success(t("toast.voterIdCopied", lang), {
          icon: "📋",
        });
      } catch {
        toast.error(t("toast.shareFailed", lang));
      }
    }
  };

  const copyVoterId = async () => {
    if (!result?.voter_id) return;
    try {
      await navigator.clipboard.writeText(result.voter_id);
      toast.success(t("toast.voterIdCopied", lang), {
        icon: "📋",
      });
    } catch {
      toast.error(t("toast.shareFailed", lang));
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <Layout hideFooter>
        <div className="mx-auto max-w-3xl px-4 py-10">
          <SectionHeader
            eyebrow={lang === "hi" ? "Guest List Check" : "Guest List Check"}
            title={t("voterCheck.title", lang)}
            subtitle={t("voterCheck.subtitle", lang)}
          />

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="overflow-hidden rounded-3xl glass-strong p-6 shadow-card md:p-10"
          >
            <form onSubmit={submit} className="grid gap-5">
              <div>
                <label className="mb-2 block text-xs uppercase tracking-widest text-gold/80">
                  {t("voterCheck.nameLabel", lang)}
                </label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t("voterCheck.namePlaceholder", lang)}
                  className="w-full rounded-2xl border border-gold/30 bg-navy/50 px-4 py-3.5 text-cream outline-none transition focus:border-gold focus:bg-navy/70"
                  required
                />
              </div>

              <div className="grid gap-5 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-xs uppercase tracking-widest text-gold/80">
                    {t("voterCheck.stateLabel", lang)}
                  </label>
                  <select
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="w-full rounded-2xl border border-gold/30 bg-navy/50 px-4 py-3.5 text-cream outline-none transition focus:border-gold"
                    required
                  >
                    <option value="">{t("voterCheck.statePlaceholder", lang)}</option>
                    {STATES.map((s) => (
                      <option key={s} value={s} className="bg-navy">
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-2 block text-xs uppercase tracking-widest text-gold/80">
                    {t("voterCheck.dobLabel", lang)}
                  </label>
                  <input
                    type="date"
                    value={dob}
                    onChange={(e) => setDob(e.target.value)}
                    className="w-full rounded-2xl border border-gold/30 bg-navy/50 px-4 py-3.5 text-cream outline-none transition focus:border-gold"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="group relative mt-2 inline-flex items-center justify-center gap-2 overflow-hidden rounded-full bg-mandap py-4 font-semibold text-navy shadow-gold gold-shimmer disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <UserCheck className="h-5 w-5" />
                )}
                {loading ? t("voterCheck.checking", lang) : t("voterCheck.checkButton", lang)}
              </button>

              {error && (
                <div className="rounded-2xl border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  {error}
                </div>
              )}
            </form>

            <AnimatePresence>
              {loading && !result && <SkeletonVoterResult />}
              
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ type: "spring", damping: 18 }}
                  className={`mt-8 overflow-hidden rounded-3xl border p-6 ${
                    result.found
                      ? "border-deep-green/50 bg-deep-green/15"
                      : "border-destructive/40 bg-destructive/10"
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div
                      className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl ${
                        result.found ? "bg-deep-green text-cream" : "bg-destructive text-cream"
                      }`}
                    >
                      {result.found ? (
                        <CheckCircle2 className="h-7 w-7" />
                      ) : (
                        <XCircle className="h-7 w-7" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="font-display text-2xl">
                        {result.found
                          ? lang === "hi" ? "Mubarak ho! 🎉" : "Congratulations! 🎉"
                          : lang === "hi" ? "Oho! Naam nahi mila" : "Oh no! Name not found"}
                      </div>
                      <p className="mt-1 text-sm text-cream/80">{result.message}</p>
                      {result.voter_id && (
                        <div className="mt-4 inline-block rounded-xl border border-gold/30 bg-navy/40 px-4 py-2">
                          <div className="text-[10px] uppercase tracking-widest text-gold/70">
                            {t("voterCheck.voterIdLabel", lang)}
                          </div>
                          <div className="font-mono text-lg font-bold text-gold">
                            {result.voter_id}
                          </div>
                        </div>
                      )}
                      
                      {/* Share buttons */}
                      {result.found && (
                        <div className="mt-4 flex flex-wrap gap-2">
                          <button
                            onClick={shareResult}
                            className="inline-flex items-center gap-2 rounded-full bg-mandap px-4 py-2 text-sm font-semibold text-navy shadow-gold gold-shimmer"
                          >
                            <Share2 className="h-4 w-4" />
                            {t("common.share", lang)}
                          </button>
                          {result.voter_id && (
                            <button
                              onClick={copyVoterId}
                              className="inline-flex items-center gap-2 rounded-full border border-gold/40 bg-navy/40 px-4 py-2 text-sm font-semibold text-gold transition hover:bg-gold/10"
                            >
                              <Copy className="h-4 w-4" />
                              {t("common.copy", lang)}
                            </button>
                          )}
                          <a
                            href="https://electoralsearch.eci.gov.in/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 rounded-full border border-gold/40 bg-navy/40 px-4 py-2 text-sm font-semibold text-gold transition hover:bg-gold/10"
                          >
                            <ExternalLink className="h-4 w-4" />
                            ECI
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </Layout>
    </motion.div>
  );
}
