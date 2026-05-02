import * as React from "react";
import { createFileRoute } from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { BookOpen, Lightbulb, Loader2, PartyPopper, Sparkles, Target } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Layout } from "@/components/Layout";
import { SectionHeader } from "@/components/SectionHeader";
import { SkeletonDictionary } from "@/components/SkeletonLoader";
import { api, type ExplainResponse, type Lang } from "@/lib/api";
import { t, useLang } from "@/routes/__root";

export const Route = createFileRoute("/dictionary")({
  component: Dictionary,
});

const TOPICS = [
  "EVM",
  "NOTA",
  "Manifesto",
  "Voter ID",
  "Booth",
  "Election Commission",
  "Model Code",
  "Vote Counting",
];

const TOPIC_DISPLAY_LABELS: Record<string, string> = {
  EVM: "EVM",
  NOTA: "NOTA",
  manifesto: "Manifesto",
  voter_id: "Voter ID",
  booth: "Booth",
  election_commission: "Election Commission",
  mcc: "Model Code",
  counting: "Vote Counting",
  ink: "Indelible Ink",
  candidate: "Candidate",
  constituency: "Constituency",
  voting_process: "Voting Process",
};

function getTopicDisplayLabel(topic: string) {
  return TOPIC_DISPLAY_LABELS[topic] || topic.replace(/_/g, " ");
}

function Dictionary() {
  const { lang, setLang } = useLang();
  const [topic, setTopic] = useState("EVM");
  const [selectedLang, setSelectedLang] = useState<Lang>(lang);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ExplainResponse | null>(null);
  const [error, setError] = useState("");
  const explainCacheRef = useRef(new Map<string, ExplainResponse>());
  const requestIdRef = useRef(0);

  useEffect(() => {
    setSelectedLang(lang);
  }, [lang]);

  const fetchExplanation = async (topicKey: string, language: Lang) => {
    const cacheKey = `${topicKey}:${language}`;
    const cached = explainCacheRef.current.get(cacheKey);
    if (cached) {
      setError("");
      setData(cached);
      return;
    }

    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;
    setLoading(true);
    setError("");

    try {
      const response = await api.explain(topicKey, language);
      if (requestIdRef.current !== requestId) {
        return;
      }

      explainCacheRef.current.set(cacheKey, response);
      setData(response);
    } catch {
      if (requestIdRef.current !== requestId) {
        return;
      }

      setError(
        language === "hi"
          ? "Maaf kijiye, definition load nahi ho payi."
          : "Sorry, couldn't load definition.",
      );
      toast.error(t("toast.apiError", language), {
        icon: "⚠️",
      });
    } finally {
      if (requestIdRef.current === requestId) {
        setLoading(false);
      }
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
        <div className="mx-auto max-w-5xl px-4 py-10">
          <SectionHeader
            eyebrow={lang === "hi" ? "शादी वाली डिक्शनरी" : "Shaadi Wali Dictionary"}
            title={lang === "hi" ? "चुनावी शब्द, शादी स्टाइल में" : "Election Words, Shaadi Style"}
            subtitle={
              lang === "hi"
                ? "हर चुनावी शब्द को शादी वाली मिसाल के साथ समझिए। चुनिए और सीखिए।"
                : "Every election term with a shaadi analogy. Choose and learn."
            }
          />

          <div className="mb-6 flex flex-wrap items-center gap-3">
            <select
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              className="flex-1 rounded-full border border-gold/30 bg-navy/50 px-5 py-3.5 text-cream outline-none focus:border-gold"
            >
              {TOPICS.map((topicOption) => (
                <option key={topicOption} value={topicOption} className="bg-navy">
                  {topicOption}
                </option>
              ))}
            </select>

            <div className="flex gap-1 rounded-full border border-gold/30 bg-navy/50 p-1">
              {(["en", "hi"] as Lang[]).map((language) => (
                <button
                  key={language}
                  onClick={() => {
                    if (loading || selectedLang === language) {
                      return;
                    }

                    setSelectedLang(language);
                    setLang(language);
                    if (data) {
                      void fetchExplanation(topic, language);
                    }
                  }}
                  disabled={loading}
                  className={`rounded-full px-4 py-2 text-xs font-semibold transition ${
                    selectedLang === language
                      ? "bg-mandap text-navy"
                      : "text-cream/70 hover:text-gold"
                  } disabled:cursor-not-allowed disabled:opacity-60`}
                >
                  {language === "hi" ? "हिंदी" : "English"}
                </button>
              ))}
            </div>

            <button
              onClick={() => void fetchExplanation(topic, selectedLang)}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-full bg-mandap px-7 py-3.5 font-semibold text-navy shadow-gold gold-shimmer disabled:opacity-50"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <BookOpen className="h-4 w-4" />}
              {lang === "hi" ? "समझाओ" : "Explain"}
            </button>
          </div>

          {error && (
            <div className="mb-6 rounded-2xl border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <AnimatePresence mode="wait">
            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <SkeletonDictionary />
              </motion.div>
            )}

            {data && !loading && (
              <motion.div
                key={`${data.topic}-${data.lang}`}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.4 }}
                className="grid gap-5"
              >
                <div className="rounded-3xl glass-strong p-8 shadow-card">
                  <div className="text-[10px] uppercase tracking-widest text-gold/70">
                    {lang === "hi" ? "विषय" : "Topic"}
                  </div>
                  <h2 className="font-display text-5xl text-gradient-gold animate-shimmer-text">
                    {getTopicDisplayLabel(data.topic)}
                  </h2>
                </div>

                <Card
                  icon={Sparkles}
                  title={lang === "hi" ? "शादी वाली मिसाल" : "Shaadi Analogy"}
                  tone="from-saffron to-gold"
                >
                  {data.shaadi_analogy}
                </Card>
                <Card
                  icon={Lightbulb}
                  title={lang === "hi" ? "आसान समझाइश" : "Simple Explanation"}
                  tone="from-gold to-rose-gold"
                >
                  {data.simple_explanation}
                </Card>
                <Card
                  icon={Target}
                  title={lang === "hi" ? "अब आपको क्या करना चाहिए" : "Your Action Step"}
                  tone="from-deep-green to-gold"
                >
                  {data.action_step}
                </Card>
                <Card
                  icon={PartyPopper}
                  title={lang === "hi" ? "मज़ेदार तथ्य" : "Fun Fact"}
                  tone="from-royal-purple to-saffron"
                >
                  {data.fun_fact}
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {!data && !loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="rounded-3xl border border-dashed border-gold/30 bg-navy/30 p-12 text-center text-cream/60"
            >
              <BookOpen className="mx-auto mb-3 h-10 w-10 text-gold/60" />
              <p>{lang === "hi" ? "कोई विषय चुनिए और समझने के लिए बटन दबाइए" : "Choose a topic and click Explain to learn"}</p>
            </motion.div>
          )}
        </div>
      </Layout>
    </motion.div>
  );
}

function Card({
  icon: Icon,
  title,
  tone,
  children,
}: {
  icon: typeof Sparkles;
  title: string;
  tone: string;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="group relative overflow-hidden rounded-3xl glass p-6 shadow-card transition hover:-translate-y-1 hover:shadow-glow"
    >
      <div
        className={`absolute -right-10 -top-10 h-32 w-32 rounded-full bg-gradient-to-br ${tone} opacity-20 blur-2xl transition group-hover:opacity-40`}
      />
      <div className="relative flex gap-4">
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br ${tone} shadow-gold`}
        >
          <Icon className="h-6 w-6 text-navy" />
        </div>
        <div className="flex-1">
          <div className="font-display text-lg font-semibold text-gold">{title}</div>
          <p className="mt-1 leading-relaxed text-cream/85">{children}</p>
        </div>
      </div>
    </motion.div>
  );
}
