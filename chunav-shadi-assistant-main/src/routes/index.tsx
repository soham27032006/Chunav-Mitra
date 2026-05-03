import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  MessageCircle,
  UserCheck,
  MapPin,
  BookOpen,
  CalendarClock,
  ArrowRight,
  Sparkles,
  ScrollText,
  Landmark,
  Leaf,
  UtensilsCrossed,
  Gift,
  Gem,
  Crown,
  PartyPopper,
} from "lucide-react";
import { Layout } from "@/components/Layout";
import { Mandap } from "@/components/Mandap";
import { useLang, t } from "@/routes/__root";
import { useEffect, useState } from "react";
import { api, type StatsResponse } from "@/lib/api";
import { SkeletonStats } from "@/components/SkeletonLoader";
import { HowItWorks } from "@/components/HowItWorks";
import { TextScrollAnimation } from "@/components/ui/text-scroll-animation";

export const Route = createFileRoute("/")({
  component: Home,
});

function useCounter(target: number, duration = 1500) {
  const [value, setValue] = useState(0);
  
  useEffect(() => {
    if (target === 0) return;
    let startTime: number;
    let raf: number;
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      setValue(Math.round(target * eased));
      
      if (progress < 1) {
        raf = requestAnimationFrame(animate);
      }
    };
    
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);
  
  return value;
}

function AnimatedStat({ value, label, icon: Icon }: { value: number; label: string; icon: typeof MessageCircle }) {
  const animatedValue = useCounter(value);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-gold/20 bg-navy/40 p-4 text-center"
    >
      <div className="mb-2 flex justify-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-saffron to-gold">
          <Icon className="h-5 w-5 text-navy" />
        </div>
      </div>
      <div className="font-display text-3xl font-bold text-gradient-gold tabular-nums">
        {animatedValue.toLocaleString("en-IN")}
      </div>
      <div className="mt-1 text-xs text-cream/60">{label}</div>
    </motion.div>
  );
}

function Home() {
  const { lang } = useLang();
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    api
      .stats()
      .then((s) => {
        setStats(s);
        setLoadingStats(false);
      })
      .catch(() => setLoadingStats(false));
    
    // Refresh stats every 60 seconds
    const interval = setInterval(() => {
      api.stats().then(setStats).catch(() => {});
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const FEATURES = [
    {
      to: "/chat" as const,
      icon: MessageCircle,
      title: lang === "hi" ? "Pandit Ji Se Poocho" : "Pandit Ji Se Poocho",
      desc: lang === "hi" ? "AI chat in Hindi & English. Voice supported." : "AI chat in Hindi & English. Voice supported.",
      accent: "from-saffron to-gold",
    },
    {
      to: "/voter-check" as const,
      icon: UserCheck,
      title: lang === "hi" ? "Guest List Check" : "Guest List Check",
      desc: lang === "hi" ? "Kya aapka naam voter list mein hai?" : "Is your name on the voter list?",
      accent: "from-gold to-rose-gold",
    },
    {
      to: "/booth" as const,
      icon: MapPin,
      title: lang === "hi" ? "Apna Mandap Dhundho" : "Find Your Mandap",
      desc: lang === "hi" ? "Find your nearest polling booth." : "Find your nearest polling booth.",
      accent: "from-deep-green to-gold",
    },
    {
      to: "/dictionary" as const,
      icon: BookOpen,
      title: lang === "hi" ? "Shaadi Wali Dictionary" : "Shaadi Dictionary",
      desc: lang === "hi" ? "EVM, NOTA, Manifesto — shaadi style." : "EVM, NOTA, Manifesto — shaadi style.",
      accent: "from-royal-purple to-saffron",
    },
    {
      to: "/timeline" as const,
      icon: CalendarClock,
      title: lang === "hi" ? "Shaadi Ka Schedule" : "Shaadi Schedule",
      desc: lang === "hi" ? "Election timeline & countdown." : "Election timeline & countdown.",
      accent: "from-burgundy to-gold",
    },
  ];

  const ANALOGIES = [
    ["Voter List", lang === "hi" ? "Guest List" : "Guest List", ScrollText, "from-saffron to-gold"],
    ["Polling Booth", "Mandap", Landmark, "from-gold to-rose-gold"],
    ["Indelible Ink", "Mehndi", Leaf, "from-deep-green to-gold"],
    ["Manifesto", lang === "hi" ? "Shagun Menu" : "Shagun Menu", UtensilsCrossed, "from-royal-purple to-saffron"],
    ["Voting", lang === "hi" ? "Shagun Dena" : "Shagun Dena", Gift, "from-burgundy to-gold"],
    ["EVM", lang === "hi" ? "Mangalsutra" : "Mangalsutra", Gem, "from-rose-gold to-gold"],
    ["Candidate", lang === "hi" ? "Dulha/Dulhan" : "Dulha/Dulhan", Crown, "from-gold to-saffron"],
    ["Polling Day", lang === "hi" ? "Shaadi Day" : "Shaadi Day", PartyPopper, "from-saffron to-burgundy"],
  ] as const;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <Layout>
        {/* HERO */}
        <section className="relative overflow-hidden px-4 pb-20 pt-10 md:pt-16 hero-section">
          <div className="mx-auto flex flex-col md:grid max-w-7xl items-center gap-4 sm:gap-6 md:gap-8 md:grid-cols-2">
            
            {/* Mandap visual - Moved to top on mobile */}
            <motion.div
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="order-first md:order-last relative flex items-center justify-center w-[240px] h-[240px] sm:w-[320px] sm:h-[320px] md:w-[420px] md:h-[420px] max-w-[80vw] max-h-[80vw] mx-auto mt-4 sm:mt-6 md:mt-0"
            >
              <div className="scale-[0.5] sm:scale-[0.66] md:scale-100 origin-center">
                <Mandap size={480} />
              </div>
            </motion.div>

            <div className="relative z-10 mt-0 sm:mt-2 text-center md:text-left flex flex-col items-center md:items-start w-full">
              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1, duration: 0.8 }}
                className={`${lang === "hi" ? "overflow-visible font-hindi pt-4 leading-[1.32] md:pt-5 md:leading-[1.22]" : "font-display leading-[1.05]"} text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold`}
              >
                <span className={`${lang === "hi" ? "inline-block overflow-visible px-1 pt-2" : "block"} text-gradient-gold animate-shimmer-text`}>
                  {t("hero.title", lang)}
                </span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                className="mt-6 text-sm sm:text-base md:text-lg px-4 sm:px-0 max-w-full sm:max-w-2xl break-words [word-break:break-word] overflow-hidden leading-relaxed text-cream/75"
              >
                {t("hero.subtitle", lang)}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="mt-8 flex flex-col xs:flex-row gap-3 w-full px-4 sm:px-0 sm:w-auto"
              >
                <Link
                  to="/chat"
                  className="group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-full bg-mandap w-full sm:w-auto min-h-[48px] px-6 py-3 font-semibold text-navy shadow-gold gold-shimmer touch-manipulation"
                >
                  <MessageCircle className="h-5 w-5" />
                  {t("hero.chatButton", lang)}
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link
                  to="/voter-check"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-gold/40 bg-navy/40 w-full sm:w-auto min-h-[48px] px-6 py-3 font-semibold text-gold backdrop-blur-md transition-all hover:bg-gold/10 touch-manipulation"
                >
                  <UserCheck className="h-5 w-5" />
                  {t("hero.checkButton", lang)}
                </Link>
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-6 flex flex-wrap items-center gap-2 sm:gap-4 justify-center md:justify-start text-xs sm:text-sm text-cream/60"
              >
                <span className="whitespace-nowrap">🪔 {t("hero.stats1", lang)}</span>
                <span className="whitespace-nowrap">💍 {t("hero.stats2", lang)}</span>
                <span className="whitespace-nowrap">🌸 {t("hero.stats3", lang)}</span>
                <span className="whitespace-nowrap">🎊 {t("hero.stats4", lang)}</span>
              </motion.div>

              {/* Live Stats */}
              {!loadingStats && stats && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                  className="mt-8 hidden sm:grid grid-cols-3 gap-3 w-full"
                >
                  <AnimatedStat
                    value={stats.total_queries}
                    label={lang === "hi" ? "Questions Asked" : "Questions Asked"}
                    icon={MessageCircle}
                  />
                  <AnimatedStat
                    value={(stats.languages_used.hi || 0) + (stats.languages_used.en || 0)}
                    label={lang === "hi" ? "Languages" : "Languages"}
                    icon={BookOpen}
                  />
                  <AnimatedStat
                    value={stats.top_intents.booth_finder || 0}
                    label={lang === "hi" ? "Mandaps Found" : "Mandaps Found"}
                    icon={MapPin}
                  />
                </motion.div>
              )}
              {loadingStats && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-8 hidden sm:block w-full"
                >
                  <SkeletonStats />
                </motion.div>
              )}
            </div>
          </div>
        </section>

        {/* FEATURES */}
        <section className="relative px-4 py-16">
          <div className="mx-auto max-w-7xl">
            <div className="mb-12 text-center">
              <div className="inline-block rounded-full border border-gold/30 bg-navy/40 px-4 py-1 text-[10px] uppercase tracking-[0.3em] text-gold">
                {t("hero.featuresSubtitle", lang)}
              </div>
              <h2 className="mt-3 font-display text-4xl text-gradient-gold md:text-5xl">
                {t("hero.featuresTitle", lang)}
              </h2>
            </div>

            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              {FEATURES.map((f, i) => (
                <motion.div
                  key={f.to}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ delay: i * 0.07, ease: [0.22, 1, 0.36, 1] }}
                >
                  <Link to={f.to} className="group block h-full">
                    <div className="relative h-full overflow-hidden rounded-3xl glass p-6 shadow-card transition-all duration-500 hover:-translate-y-2 hover:shadow-glow gold-shimmer">
                      <div
                        className={`absolute -right-12 -top-12 h-40 w-40 rounded-full bg-gradient-to-br ${f.accent} opacity-20 blur-2xl transition-opacity duration-500 group-hover:opacity-50`}
                      />
                      <div className="relative">
                        <div
                          className={`mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${f.accent} shadow-gold`}
                        >
                          <f.icon className="h-7 w-7 text-navy" />
                        </div>
                        <h3 className="font-display text-2xl font-semibold text-gold">
                          {f.title}
                        </h3>
                        <p className="mt-2 text-sm text-cream/70">{f.desc}</p>
                        <div className="mt-5 inline-flex items-center gap-1 text-xs font-semibold text-gold/80 transition-all group-hover:gap-3">
                          {lang === "hi" ? "Andar aaiye" : "Enter"} <ArrowRight className="h-3.5 w-3.5" />
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

      {/* ANALOGY STRIP */}
      <section className="relative px-4 py-16">
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-gold/20 glass-strong p-8 shadow-card md:p-14">
          <div className="text-center">
            <div className="text-[10px] uppercase tracking-[0.3em] text-gold/70">
              {t("hero.analogySubtitle", lang)}
            </div>
            <h2 className="mt-2 font-display text-3xl text-cream md:text-4xl">
              Election ≈{" "}
              <span className="text-gradient-gold">Indian Wedding</span>
            </h2>
          </div>
          <div className="mt-10 grid grid-cols-2 gap-5 md:grid-cols-4">
            {ANALOGIES.map(([a, b, Icon, accent], i) => (
              <motion.div
                key={a}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                whileHover={{ y: -4 }}
                className="group relative overflow-hidden rounded-2xl border border-gold/20 bg-navy/40 p-5 text-center transition-all duration-500 hover:border-gold/50 hover:shadow-glow"
              >
                <div
                  className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${accent} opacity-0 blur-2xl transition-opacity duration-500 group-hover:opacity-20`}
                />
                <div className="relative">
                  <div
                    className={`mx-auto mb-3 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${accent} shadow-gold ring-1 ring-gold/30`}
                  >
                    <Icon className="h-6 w-6 text-navy" strokeWidth={1.75} />
                  </div>
                  <div className="text-xs uppercase tracking-wider text-cream/60">{a}</div>
                  <div className="mt-1 font-display text-base font-semibold text-gradient-gold">
                    ≈ {b}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <HowItWorks />

      <TextScrollAnimation />
    </Layout>
  </motion.div>
);
}
