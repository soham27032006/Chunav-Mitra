import { Link, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Sparkles, Activity, Languages } from "lucide-react";
import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { useLang, t } from "@/routes/__root";

const NAV = [
  { to: "/", labelKey: "nav.home" },
  { to: "/chat", labelKey: "nav.chat" },
  { to: "/voter-check", labelKey: "nav.voterCheck" },
  { to: "/booth", labelKey: "nav.mandap" },
  { to: "/dictionary", labelKey: "nav.dictionary" },
  { to: "/timeline", labelKey: "nav.timeline" },
] as const;

export function Header() {
  const { lang, toggleLang } = useLang();
  const navigate = useNavigate();
  const [today, setToday] = useState<number | null>(null);

  useEffect(() => {
    api
      .stats()
      .then((s) => setToday(s.queries_today))
      .catch(() => setToday(null));
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key.toLowerCase()) {
        case "/":
          e.preventDefault();
          navigate({ to: "/chat" });
          break;
        case "v":
          e.preventDefault();
          navigate({ to: "/voter-check" });
          break;
        case "b":
          e.preventDefault();
          navigate({ to: "/booth" });
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [navigate]);

  return (
    <motion.header
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="sticky top-0 z-40 border-b border-gold/10"
    >
      <div className="glass-strong">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 md:px-8">
          <Link to="/" className="group flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 rounded-full bg-gold/40 blur-md transition-all group-hover:bg-gold/70" />
              <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-mandap shadow-gold">
                <Sparkles className="h-5 w-5 text-navy" />
              </div>
            </div>
            <div className="leading-tight">
              <div className="font-display text-xl font-bold text-gradient-gold animate-shimmer-text">
                Chunav Mitra
              </div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-gold/70">
                {lang === "hi" ? "Desh ki Sabse Badi Shaadi" : "Desh ki Sabse Badi Shaadi"}
              </div>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex">
            {NAV.map((n) => (
              <Link
                key={n.to}
                to={n.to}
                className="group relative rounded-full px-4 py-2 text-sm font-medium text-cream/80 transition-colors hover:text-gold"
                activeProps={{ className: "text-gold" }}
              >
                {({ isActive }) => (
                  <>
                    {isActive && (
                      <motion.span
                        layoutId="navpill"
                        className="absolute inset-0 rounded-full bg-gold/15 ring-1 ring-gold/40"
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                      />
                    )}
                    <span className="relative">{t(n.labelKey, lang)}</span>
                  </>
                )}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            {/* Language Toggle */}
            <button
              onClick={toggleLang}
              className="inline-flex items-center gap-1.5 rounded-full border border-gold/30 bg-navy/40 px-3 py-1.5 text-xs font-medium text-gold transition hover:bg-gold/10"
              title={lang === "hi" ? "Switch to English" : "Hindi mein badlein"}
            >
              <Languages className="h-3.5 w-3.5" />
              <span className="font-semibold">{lang === "hi" ? "हिं" : "EN"}</span>
            </button>

            {today !== null && (
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="hidden items-center gap-2 rounded-full border border-gold/30 bg-navy/40 px-3 py-1.5 text-xs sm:flex"
              >
                <Activity className="h-3.5 w-3.5 text-deep-green" />
                <span className="text-cream/70">{lang === "hi" ? "Aaj:" : "Today:"}</span>
                <span className="font-bold text-gold tabular-nums">
                  {today.toLocaleString("en-IN")}
                </span>
              </motion.div>
            )}
          </div>
        </div>

        {/* Mobile nav */}
        <nav className="flex items-center gap-1 sm:gap-2 overflow-x-auto scrollbar-hide px-2 sm:px-0 lg:hidden pb-2">
          {NAV.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              className="px-3 py-1.5 sm:px-4 sm:py-2 rounded-full text-sm sm:text-base whitespace-nowrap border border-gold/30 hover:border-saffron transition-all duration-200 text-cream/80 min-h-[32px] min-w-auto"
              activeProps={{ className: "bg-gold/15 text-gold border-gold/50" }}
            >
              {t(n.labelKey, lang)}
            </Link>
          ))}
        </nav>
      </div>
    </motion.header>
  );
}
