import { createFileRoute } from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { Bot, Languages, Sparkles, User } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { ChatInput } from "@/components/ChatInput";
import { Layout } from "@/components/Layout";
import { SectionHeader } from "@/components/SectionHeader";
import { SkeletonChat } from "@/components/SkeletonLoader";
import { api, type ChatMessage, type Lang } from "@/lib/api";
import { useLang } from "@/routes/__root";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
});

const SUGGESTIONS = [
  { en: "How do I check if I'm on the voter list?", hi: "मतदाता सूची में मेरा नाम कैसे जाँचूँ?" },
  { en: "Where is my polling booth?", hi: "मेरा मतदान केंद्र कहाँ है?" },
  { en: "What is an EVM?", hi: "ईवीएम क्या है?" },
  { en: "When are the next elections?", hi: "अगले चुनाव कब हैं?" },
] as const;

const CHAT_COPY = {
  en: {
    eyebrow: "AI Pandit Ji",
    title: "Ask Pandit Ji",
    subtitle: "Ask all your questions in Hindi or English.",
    online: "Online · Bilingual",
    toggle: "English",
    welcomeTitle: "Welcome!",
    welcomeSubtitle: "Ask anything about the voter list, polling booth, EVM, or election timeline.",
    aiUnavailable:
      "Sorry, the AI answer is temporarily unavailable. Please try the Dictionary or Timeline section instead.",
    serverUnavailable: "Sorry, server is not available. Please start the backend and try again.",
    switched: "Converted the chat to English.",
    translateFailed: "Could not translate the chat.",
    chatAreaLabel: "Chat conversation with Chunav Mitra",
    loadingAnnouncement: "Loading response from Chunav Mitra...",
  },
  hi: {
    eyebrow: "एआई पंडित जी",
    title: "पंडित जी से पूछो",
    subtitle: "अपने सभी सवाल हिंदी या अंग्रेज़ी में पूछिए।",
    online: "ऑनलाइन · द्विभाषी",
    toggle: "हिंदी",
    welcomeTitle: "स्वागत है!",
    welcomeSubtitle: "मतदाता सूची, मतदान केंद्र, ईवीएम और चुनाव की तारीखों के बारे में कुछ भी पूछिए।",
    aiUnavailable:
      "माफ़ कीजिए, एआई उत्तर अभी उपलब्ध नहीं है। कृपया Dictionary या Timeline सेक्शन आज़माइए।",
    serverUnavailable:
      "माफ़ कीजिए, सर्वर अभी उपलब्ध नहीं है। कृपया बैकएंड चालू करके फिर कोशिश करें।",
    switched: "पूरी चैट हिंदी में बदल दी गई।",
    translateFailed: "चैट का अनुवाद नहीं हो पाया।",
    chatAreaLabel: "चुनाव मित्र के साथ चैट बातचीत",
    loadingAnnouncement: "चुनाव मित्र से उत्तर लोड हो रहा है...",
  },
} as const;

const INTENT_LABELS: Record<string, { en: string; hi: string }> = {
  general: { en: "General", hi: "सामान्य" },
  explain: { en: "Explain", hi: "समझाइश" },
  timeline: { en: "Timeline", hi: "समय" },
  voter_check: { en: "Voter Check", hi: "मतदाता जाँच" },
  booth_finder: { en: "Booth Finder", hi: "मतदान केंद्र" },
};

function getIntentLabel(intent: string, lang: Lang): string {
  return INTENT_LABELS[intent]?.[lang] ?? intent.replace("_", " ");
}

function sanitizeAssistantText(text: string, lang: Lang): string {
  const lower = text.toLowerCase();
  if (
    lower.includes("quota exceeded") ||
    lower.includes("exceeded your current quota") ||
    lower.includes("rate-limit") ||
    lower.includes("generativelanguage.googleapis.com")
  ) {
    return CHAT_COPY[lang].aiUnavailable;
  }
  return text;
}

type ChatMessageWithTranslations = ChatMessage & {
  translations?: Partial<Record<Lang, string>>;
};

function ChatPage() {
  const { lang, setLang } = useLang();
  const [messages, setMessages] = useState<ChatMessageWithTranslations[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [streaming, setStreaming] = useState(false);
  const [initialLoading] = useState(false);
  const [translatingChat, setTranslatingChat] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const inputTranslationsRef = useRef<Partial<Record<Lang, string>>>({});
  const copy = CHAT_COPY[lang];
  const isBusy = streaming || translatingChat;

  const localizedSuggestions = useMemo(
    () => SUGGESTIONS.map((suggestion) => (lang === "hi" ? suggestion.hi : suggestion.en)),
    [lang],
  );

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isBusy]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (
        event.key === "/" &&
        document.activeElement?.tagName !== "INPUT" &&
        document.activeElement?.tagName !== "TEXTAREA"
      ) {
        event.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleInputChange = useCallback(
    (nextValue: string) => {
      setInput(nextValue);
      inputTranslationsRef.current[lang] = nextValue;
      inputTranslationsRef.current[lang === "hi" ? "en" : "hi"] = undefined;
    },
    [lang],
  );

  const updateAssistantMessage = useCallback(
    (assistantId: string, nextContent: string, intent?: ChatMessage["intent"]) => {
      const sanitizedContent = sanitizeAssistantText(nextContent, lang);
      setMessages((currentMessages) =>
        currentMessages.map((message) =>
          message.id === assistantId
            ? {
                ...message,
                content: sanitizedContent,
                intent,
                translations: {
                  ...message.translations,
                  [lang]: sanitizedContent,
                },
              }
            : message,
        ),
      );
    },
    [lang],
  );

  const send = useCallback(
    async (textRaw?: string) => {
      const text = (textRaw ?? input).trim();
      if (!text || isBusy) {
        return;
      }

      setInput("");
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      const assistantId = crypto.randomUUID();
      inputTranslationsRef.current[lang] = "";
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          ...userMsg,
          translations: { [lang]: text },
        },
        { id: assistantId, role: "assistant", content: "", timestamp: new Date(), translations: {} },
      ]);
      setStreaming(true);

      const url = api.streamAskUrl(text, sessionId, lang);
      let streamed = false;

      try {
        const eventSource = new EventSource(url);
        let accumulatedResponse = "";
        const cleanup = () => {
          eventSource.close();
          setStreaming(false);
        };

        eventSource.onmessage = (event) => {
          streamed = true;
          try {
            const data = JSON.parse(event.data) as {
              chunk?: string;
              session_id?: string;
              done?: boolean;
              intent?: ChatMessage["intent"];
            };
            if (data.session_id) {
              setSessionId(data.session_id);
            }
            if (data.chunk) {
              accumulatedResponse += data.chunk;
              updateAssistantMessage(assistantId, accumulatedResponse, data.intent);
            }
            if (data.done) {
              cleanup();
            }
          } catch {
            accumulatedResponse += event.data;
            updateAssistantMessage(assistantId, accumulatedResponse);
          }
        };

        eventSource.onerror = () => {
          if (streamed) {
            cleanup();
            return;
          }

          eventSource.close();
          api
            .ask(text, sessionId, lang)
            .then((response) => {
              setSessionId(response.session_id);
              updateAssistantMessage(assistantId, response.response, response.intent);
            })
            .catch(() => {
              toast.error(copy.serverUnavailable);
              updateAssistantMessage(assistantId, copy.serverUnavailable);
            })
            .finally(() => setStreaming(false));
        };
      } catch {
        setStreaming(false);
      }
    },
    [copy.serverUnavailable, input, isBusy, lang, sessionId, updateAssistantMessage],
  );

  const toggleLanguage = useCallback(async () => {
    const nextLang: Lang = lang === "hi" ? "en" : "hi";
    if (translatingChat) {
      return;
    }
    setTranslatingChat(true);

    try {
      if (messages.length > 0) {
        const uncachedEntries = messages
          .map((message, index) => ({
            index,
            text: message.content,
            cached: message.translations?.[nextLang],
          }))
          .filter((entry) => !entry.cached && entry.text.trim().length > 0);

        const result =
          uncachedEntries.length > 0
            ? await api.translateBatch(
                uncachedEntries.map((entry) => entry.text),
                nextLang,
              )
            : { texts: [], target_lang: nextLang };

        const translatedByIndex = new Map<number, string>();
        uncachedEntries.forEach((entry, translatedIndex) => {
          const translated = result.texts[translatedIndex];
          if (translated) {
            translatedByIndex.set(entry.index, translated);
          }
        });

        setMessages((currentMessages) =>
          currentMessages.map((message, index) => ({
            ...message,
            content:
              message.translations?.[nextLang] ?? translatedByIndex.get(index) ?? message.content,
            translations: {
              ...message.translations,
              [nextLang]:
                message.translations?.[nextLang] ?? translatedByIndex.get(index) ?? message.content,
            },
          })),
        );
      }

      if (input.trim()) {
        if (!inputTranslationsRef.current[nextLang]) {
          const result = await api.translateBatch([input], nextLang);
          inputTranslationsRef.current[nextLang] = result.texts[0] ?? input;
        }
        setInput(inputTranslationsRef.current[nextLang] ?? input);
      }

      setLang(nextLang);
      toast.success(CHAT_COPY[nextLang].switched);
    } catch {
      toast.error(CHAT_COPY[nextLang].translateFailed);
    } finally {
      setTranslatingChat(false);
    }
  }, [input, lang, messages, setLang]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <Layout hideFooter>
        <div className="mx-auto max-w-4xl px-4 py-10">
          <SectionHeader eyebrow={copy.eyebrow} title={copy.title} subtitle={copy.subtitle} />

          <div className="overflow-hidden rounded-3xl glass-strong shadow-card">
            <div className="flex items-center justify-between border-b border-gold/15 px-5 py-3">
              <div className="flex items-center gap-2 text-sm text-cream/85">
                <div
                  className="relative flex h-8 w-8 items-center justify-center rounded-full bg-mandap"
                  aria-hidden="true"
                >
                  <Sparkles className="h-4 w-4 text-navy" />
                  <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-deep-green ring-2 ring-navy" />
                </div>
                <div>
                  <div className="font-semibold text-gold">Chunav Mitra</div>
                  <div className="text-[10px] uppercase tracking-widest text-cream/65">
                    {copy.online}
                  </div>
                </div>
              </div>
              <button
                onClick={() => void toggleLanguage()}
                disabled={translatingChat}
                aria-label={lang === "hi" ? "Switch chat language to English" : "Switch chat language to Hindi"}
                className="inline-flex items-center gap-2 rounded-full border border-gold/30 bg-navy/40 px-3 py-1.5 text-xs text-gold transition hover:bg-gold/10 disabled:opacity-60"
              >
                <Languages className="h-3.5 w-3.5" aria-hidden="true" />
                {copy.toggle}
              </button>
            </div>

            <div className="sr-only" aria-live="polite" aria-atomic="true">
              {isBusy ? copy.loadingAnnouncement : ""}
            </div>

            <div
              ref={scrollRef}
              className="scrollbar-gold h-[55vh] overflow-y-auto px-4 py-6 md:px-6"
              aria-label={copy.chatAreaLabel}
              aria-live="polite"
              aria-busy={isBusy}
            >
              {messages.length === 0 && !initialLoading && (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <motion.div
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 3, repeat: Infinity }}
                    className="mb-3 text-5xl"
                    aria-hidden="true"
                  >
                    🪔
                  </motion.div>
                  <div className="font-display text-xl text-gradient-gold">{copy.welcomeTitle}</div>
                  <p className="mt-1 max-w-md text-sm text-cream/75">{copy.welcomeSubtitle}</p>
                  <div className="mt-6 grid w-full max-w-2xl grid-cols-1 gap-2 sm:grid-cols-2">
                    {localizedSuggestions.map((suggestionText, index) => (
                      <motion.button
                        key={suggestionText}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 + index * 0.05 }}
                        onClick={() => void send(suggestionText)}
                        aria-label={suggestionText}
                        className="rounded-2xl border border-gold/25 bg-navy/40 px-4 py-3 text-left text-sm text-cream/90 transition hover:-translate-y-0.5 hover:border-gold/60 hover:bg-gold/10"
                      >
                        ✨ {suggestionText}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}

              {initialLoading && <SkeletonChat />}

              <AnimatePresence initial={false}>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 16, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ type: "spring", stiffness: 260, damping: 22 }}
                    className={`mb-4 flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
                  >
                    <div
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
                        message.role === "user"
                          ? "bg-royal text-cream"
                          : "bg-mandap text-navy shadow-gold"
                      }`}
                      aria-hidden="true"
                    >
                      {message.role === "user" ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                    </div>
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-card ${
                        message.role === "user"
                          ? "bg-gradient-to-br from-saffron to-rose-gold text-navy"
                          : "border border-gold/20 bg-navy/60 text-cream/95"
                      }`}
                    >
                      {message.content || (
                        <span className="inline-flex gap-1" aria-label={copy.loadingAnnouncement}>
                          <span className="h-2 w-2 animate-bounce rounded-full bg-gold [animation-delay:0ms]" />
                          <span className="h-2 w-2 animate-bounce rounded-full bg-gold [animation-delay:120ms]" />
                          <span className="h-2 w-2 animate-bounce rounded-full bg-gold [animation-delay:240ms]" />
                        </span>
                      )}
                      {message.intent && message.role === "assistant" && (
                        <div className="mt-2 inline-block rounded-full border border-gold/30 bg-navy/40 px-2 py-0.5 text-[9px] uppercase tracking-widest text-gold/90">
                          {getIntentLabel(message.intent, lang)}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            <ChatInput
              value={input}
              onValueChange={handleInputChange}
              onSubmit={() => void send()}
              streaming={isBusy}
              lang={lang}
              inputRef={inputRef}
            />
          </div>
        </div>
      </Layout>
    </motion.div>
  );
}
