import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { MapPin, Navigation, Loader2, ExternalLink, MapPinned } from "lucide-react";
import { Layout } from "@/components/Layout";
import { SectionHeader } from "@/components/SectionHeader";
import { api, type BoothResponse } from "@/lib/api";
import { useLang, t } from "@/routes/__root";
import { toast } from "sonner";
import { SkeletonBooth } from "@/components/SkeletonLoader";

export const Route = createFileRoute("/booth")({
  component: BoothFinder,
});

function BoothFinder() {
  const { lang } = useLang();
  const navigate = useNavigate();
  const [pincode, setPincode] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BoothResponse | null>(null);
  const [error, setError] = useState("");

  // Keyboard shortcut: "B" for booth finder, "Escape" to close result
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return;
      if (e.key === "Escape" && result) {
        setResult(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [result]);

  const find = async (data: { pincode?: string; lat?: number; lng?: number }) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await api.findBooth(data);
      setResult(res);
      toast.success(t("toast.boothFound", lang), {
        icon: "🏛️",
      });
    } catch {
      setError(lang === "hi" ? "Booth dhundhne mein dikkat. Try again later." : "Problem finding booth. Try again later.");
      toast.error(t("toast.apiError", lang), {
        icon: "⚠️",
      });
    } finally {
      setLoading(false);
    }
  };

  const useGps = () => {
    if (!navigator.geolocation) {
      setError(lang === "hi" ? "GPS aapke browser mein available nahi hai." : "GPS not available in your browser.");
      toast.error(lang === "hi" ? "GPS available nahi hai" : "GPS not available", {
        icon: "📍",
      });
      return;
    }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => find({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {
        setLoading(false);
        setError(lang === "hi" ? "Location access nahi mila. Pincode use karo." : "Location access denied. Use pincode instead.");
        toast.error(lang === "hi" ? "Location access nahi mila" : "Location access denied", {
          icon: "📍",
        });
      },
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <Layout hideFooter>
        <div className="mx-auto max-w-4xl px-4 py-10">
          <SectionHeader
            eyebrow={lang === "hi" ? "Mandap Locator" : "Mandap Locator"}
            title={t("booth.title", lang)}
            subtitle={t("booth.subtitle", lang)}
          />

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-3xl glass-strong p-6 shadow-card md:p-10"
          >
            <div className="flex flex-col gap-3 md:flex-row">
              <input
                value={pincode}
                onChange={(e) => setPincode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                placeholder={t("booth.pincodePlaceholder", lang)}
                className="flex-1 rounded-full border border-gold/30 bg-navy/50 px-5 py-3.5 text-cream outline-none transition focus:border-gold focus:bg-navy/70"
              />
              <button
                onClick={() => find({ pincode })}
                disabled={loading || pincode.length !== 6}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-mandap px-7 py-3.5 font-semibold text-navy shadow-gold gold-shimmer disabled:opacity-50"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <MapPin className="h-4 w-4" />}
                {t("booth.findButton", lang)}
              </button>
              <button
                onClick={useGps}
                disabled={loading}
                className="inline-flex items-center justify-center gap-2 rounded-full border border-gold/40 bg-navy/40 px-5 py-3.5 font-semibold text-gold transition hover:bg-gold/10 disabled:opacity-50"
              >
                <Navigation className="h-4 w-4" />
                {t("booth.useGps", lang)}
              </button>
            </div>

            {error && (
              <div className="mt-4 rounded-2xl border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <AnimatePresence>
              {loading && !result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mt-8"
                >
                  <SkeletonBooth />
                </motion.div>
              )}

              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 30, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ type: "spring", damping: 20 }}
                  className="mt-8 overflow-hidden rounded-3xl border border-gold/30 bg-navy/40"
                >
                  <div className="grid md:grid-cols-2">
                    <div className="p-6 md:p-8">
                      <div className="text-[10px] uppercase tracking-widest text-gold/70">
                        {t("booth.yourMandap", lang)}
                      </div>
                      <h3 className="mt-1 font-display text-3xl text-gradient-gold">
                        {result.booth_name}
                      </h3>
                      <p className="mt-3 text-sm text-cream/80">{result.address}</p>
                      <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-gold/30 bg-navy/40 px-3 py-1 text-xs text-gold">
                        <MapPin className="h-3.5 w-3.5" /> {result.distance}
                      </div>
                      <p className="mt-5 rounded-2xl border border-gold/20 bg-navy/40 p-4 text-sm italic text-cream/85">
                        💌 {result.message}
                      </p>
                      <a
                        href={result.maps_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-5 inline-flex items-center gap-2 rounded-full bg-mandap px-5 py-2.5 text-sm font-semibold text-navy shadow-gold gold-shimmer"
                      >
                        {lang === "hi" ? "Google Maps mein dekho" : "Open in Google Maps"}
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                    <div className="relative min-h-[300px] border-t border-gold/15 md:border-l md:border-t-0">
                      <iframe
                        title="Booth location"
                        className="h-full w-full"
                        src={`https://www.google.com/maps?q=${encodeURIComponent(
                          result.address || result.booth_name,
                        )}&output=embed`}
                        loading="lazy"
                        referrerPolicy="no-referrer-when-downgrade"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {!result && !loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-12 rounded-3xl border border-dashed border-gold/30 bg-navy/30 p-12 text-center text-cream/60"
              >
                <MapPinned className="mx-auto mb-4 h-16 w-16 text-gold/40" />
                <p className="text-lg font-display text-gold/80">
                  {lang === "hi" ? "Apna pincode daaliye ya GPS use kijiye" : "Enter your pincode or use GPS"}
                </p>
                <p className="mt-2 text-sm">
                  {lang === "hi" ? "Aapka mandap dhoondhne ke liye" : "to find your mandap"}
                </p>
              </motion.div>
            )}
          </motion.div>
        </div>
      </Layout>
    </motion.div>
  );
}
