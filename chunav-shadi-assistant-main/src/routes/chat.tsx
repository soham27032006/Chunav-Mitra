import { createFileRoute } from "@tanstack/react-router";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState, useCallback } from "react";
import { Mic, MicOff, Send, Sparkles, Languages, Bot, User } from "lucide-react";
import { Layout } from "@/components/Layout";
import { SectionHeader } from "@/components/SectionHeader";
import { api, type ChatMessage, type Lang } from "@/lib/api";
import { useLang, t } from "@/routes/__root";
import { toast } from "sonner";
import { SkeletonChat } from "@/components/SkeletonLoader";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
});

const SUGGESTIONS = [
  { en: "How do I check if I'm on the voter list?", hi: "Kya mera naam voter list mein hai?" },
  { en: "Where is my polling booth?", hi: "Mera matdan kendra kahan hai?" },
  { en: "What is an EVM?", hi: "EVM kya hai?" },
  { en: "When are the next elections?", hi: "Agla chunav kab hai?" },
];

// Minimal SpeechRecognition typings
type SR = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: (e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void;
  onend: () => void;
  onerror: () => void;
  start: () => void;
  stop: () => void;
};

function getSR(): SR | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?: new () => SR;
    webkitSpeechRecognition?: new () => SR;
  };
  const Ctor = w.SpeechRecognition || w.webkitSpeechRecognition;
  return Ctor ? new Ctor() : null;
}

function ChatPage() {
  const { lang, setLang } = useLang();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [streaming, setStreaming] = useState(false);
  const [listening, setListening] = useState(false);
  const [initialLoading, setInitialLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const srRef = useRef<SR | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, streaming]);

  // Keyboard shortcut: "/" to focus chat input
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape") {
        // Clear any active states
        setListening(false);
        srRef.current?.stop();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const send = async (textRaw?: string) => {
    const text = (textRaw ?? input).trim();
    if (!text || streaming) return;
    setInput("");
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    const assistantId = crypto.randomUUID();
    setMessages((m) => [
      ...m,
      userMsg,
      { id: assistantId, role: "assistant", content: "", timestamp: new Date() },
    ]);
    setStreaming(true);

    // Try SSE streaming first
    const url = api.streamAskUrl(text, sessionId);
    let streamed = false;
    try {
      const es = new EventSource(url);
      let acc = "";
      const cleanup = () => {
        es.close();
        setStreaming(false);
      };
      es.onmessage = (ev) => {
        streamed = true;
        try {
          const data = JSON.parse(ev.data) as {
            chunk?: string;
            session_id?: string;
            done?: boolean;
            intent?: ChatMessage["intent"];
          };
          if (data.session_id) setSessionId(data.session_id);
          if (data.chunk) {
            acc += data.chunk;
            setMessages((m) =>
              m.map((msg) =>
                msg.id === assistantId ? { ...msg, content: acc, intent: data.intent } : msg,
              ),
            );
          }
          if (data.done) cleanup();
        } catch {
          /* plain text */
          acc += ev.data;
          setMessages((m) =>
            m.map((msg) => (msg.id === assistantId ? { ...msg, content: acc } : msg)),
          );
        }
      };
      es.onerror = () => {
        if (streamed) {
          cleanup();
          return;
        }
        es.close();
        // Fallback to POST /api/ask
        api
          .ask(text, sessionId, lang)
          .then((res) => {
            setSessionId(res.session_id);
            setMessages((m) =>
              m.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, content: res.response, intent: res.intent }
                  : msg,
              ),
            );
          })
          .catch(() => {
            toast.error(t("toast.apiError", lang));
            setMessages((m) =>
              m.map((msg) =>
                msg.id === assistantId
                  ? {
                      ...msg,
                      content: lang === "hi"
                        ? "🙏 Maaf kijiye, server abhi available nahi hai. Backend chalu karke try kare."
                        : "🙏 Sorry, server is not available. Please start the backend and try again.",
                    }
                  : msg,
              ),
            );
          })
          .finally(() => setStreaming(false));
      };
    } catch {
      setStreaming(false);
    }
  };

  const toggleMic = () => {
    if (listening) {
      srRef.current?.stop();
      setListening(false);
      return;
    }
    const sr = getSR();
    if (!sr) {
      toast.error(lang === "hi" ? "Voice input is supported nahi hai." : "Voice input is not supported in this browser.");
      return;
    }
    sr.lang = lang === "hi" ? "hi-IN" : "en-IN";
    sr.interimResults = false;
    sr.continuous = false;
    sr.onresult = (e) => {
      const t = e.results[0][0].transcript;
      setInput(t);
      setListening(false);
      setTimeout(() => send(t), 200);
    };
    sr.onend = () => setListening(false);
    sr.onerror = () => {
      setListening(false);
      toast.error(lang === "hi" ? "Voice sunne mein dikkat hui." : "Could not understand voice input.");
    };
    sr.start();
    srRef.current = sr;
    setListening(true);
  };

  const toggleLanguage = useCallback(() => {
    const newLang = lang === "hi" ? "en" : "hi";
    setLang(newLang);
    toast.success(newLang === "hi" ? "Hindi mein badal diya!" : "Switched to English!");
  }, [lang, setLang]);

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
            eyebrow="AI Pandit Ji"
            title={lang === "hi" ? "Pandit Ji Se Poocho" : "Ask Pandit Ji"}
            subtitle={lang === "hi" 
              ? "Apne sabhi sawaal poochiye — Hindi ya English mein. Voice bhi chalega."
              : "Ask all your questions — in Hindi or English. Voice also works."}
          />

          {/* Chat panel */}
          <div className="overflow-hidden rounded-3xl glass-strong shadow-card">
            {/* Bar */}
            <div className="flex items-center justify-between border-b border-gold/15 px-5 py-3">
              <div className="flex items-center gap-2 text-sm text-cream/80">
                <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-mandap">
                  <Sparkles className="h-4 w-4 text-navy" />
                  <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-deep-green ring-2 ring-navy" />
                </div>
                <div>
                  <div className="font-semibold text-gold">Chunav Mitra</div>
                  <div className="text-[10px] uppercase tracking-widest text-cream/50">
                    {lang === "hi" ? "Online · Bilingual" : "Online · Bilingual"}
                  </div>
                </div>
              </div>
              <button
                onClick={toggleLanguage}
                className="inline-flex items-center gap-2 rounded-full border border-gold/30 bg-navy/40 px-3 py-1.5 text-xs text-gold transition hover:bg-gold/10"
              >
                <Languages className="h-3.5 w-3.5" />
                {lang === "hi" ? "हिंदी" : "English"}
              </button>
            </div>

            {/* Messages */}
            <div
              ref={scrollRef}
              className="scrollbar-gold h-[55vh] overflow-y-auto px-4 py-6 md:px-6"
            >
              {messages.length === 0 && !initialLoading && (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <motion.div
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 3, repeat: Infinity }}
                    className="mb-3 text-5xl"
                  >
                    🪔
                  </motion.div>
                  <div className="font-display text-xl text-gradient-gold">
                    {t("chat.welcomeTitle", lang)}
                  </div>
                  <p className="mt-1 max-w-md text-sm text-cream/60">
                    {t("chat.welcomeSubtitle", lang)}
                  </p>
                  <div className="mt-6 grid w-full max-w-2xl grid-cols-1 gap-2 sm:grid-cols-2">
                    {SUGGESTIONS.map((s, i) => {
                      const text = lang === "hi" ? s.hi : s.en;
                      return (
                        <motion.button
                          key={i}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.1 + i * 0.05 }}
                          onClick={() => send(text)}
                          className="rounded-2xl border border-gold/25 bg-navy/40 px-4 py-3 text-left text-sm text-cream/85 transition hover:-translate-y-0.5 hover:border-gold/60 hover:bg-gold/10"
                        >
                          ✨ {text}
                        </motion.button>
                      );
                    })}
                  </div>
                </div>
              )}

              {initialLoading && <SkeletonChat />}

              <AnimatePresence initial={false}>
                {messages.map((m) => (
                  <motion.div
                    key={m.id}
                    initial={{ opacity: 0, y: 16, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ type: "spring", stiffness: 260, damping: 22 }}
                    className={`mb-4 flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}
                  >
                    <div
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
                        m.role === "user"
                          ? "bg-royal text-cream"
                          : "bg-mandap text-navy shadow-gold"
                      }`}
                    >
                      {m.role === "user" ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                    </div>
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-card ${
                        m.role === "user"
                          ? "bg-gradient-to-br from-saffron to-rose-gold text-navy"
                          : "border border-gold/20 bg-navy/60 text-cream/90"
                      }`}
                    >
                      {m.content || (
                        <span className="inline-flex gap-1">
                          <span className="h-2 w-2 animate-bounce rounded-full bg-gold [animation-delay:0ms]" />
                          <span className="h-2 w-2 animate-bounce rounded-full bg-gold [animation-delay:120ms]" />
                          <span className="h-2 w-2 animate-bounce rounded-full bg-gold [animation-delay:240ms]" />
                        </span>
                      )}
                      {m.intent && m.role === "assistant" && (
                        <div className="mt-2 inline-block rounded-full border border-gold/30 bg-navy/40 px-2 py-0.5 text-[9px] uppercase tracking-widest text-gold/80">
                          {m.intent.replace("_", " ")}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* Input */}
            <div className="border-t border-gold/15 p-3 md:p-4">
              <div className="flex items-center gap-2">
                <button
                  onClick={toggleMic}
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full transition-all ${
                    listening
                      ? "bg-destructive text-cream animate-glow-pulse"
                      : "border border-gold/40 bg-navy/40 text-gold hover:bg-gold/10"
                  }`}
                  aria-label="Voice input"
                >
                  {listening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                </button>
                <input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && send()}
                  placeholder={t("chat.placeholder", lang)}
                  className="flex-1 rounded-full border border-gold/30 bg-navy/40 px-5 py-3 text-sm text-cream placeholder:text-cream/40 outline-none transition focus:border-gold/70 focus:bg-navy/60"
                />
                <button
                  onClick={() => send()}
                  disabled={!input.trim() || streaming}
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-mandap text-navy shadow-gold transition-transform hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="Send"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </motion.div>
  );
}
