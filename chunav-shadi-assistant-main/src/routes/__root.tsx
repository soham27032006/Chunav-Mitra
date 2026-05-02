import * as React from "react";
import { Outlet, createRootRoute, HeadContent, Scripts } from "@tanstack/react-router";
import { createContext, useCallback, useContext, useEffect, useState } from "react";

import appCss from "../styles.css?url";
import { Layout } from "@/components/Layout";
import { Toaster } from "@/components/ui/sonner";

export type Lang = "hi" | "en";

interface LangContextType {
  lang: Lang;
  toggleLang: () => void;
  setLang: (lang: Lang) => void;
}

export const LangContext = createContext<LangContextType>({
  lang: "en",
  toggleLang: () => undefined,
  setLang: () => undefined,
});

export function useLang() {
  return useContext(LangContext);
}

export const translations = {
  nav: {
    home: { en: "Home", hi: "घर" },
    chat: { en: "Chat", hi: "बात" },
    voterCheck: { en: "Guest List", hi: "मेहमान" },
    mandap: { en: "Mandap", hi: "मंडप" },
    dictionary: { en: "Dictionary", hi: "शब्दकोश" },
    timeline: { en: "Timeline", hi: "समय" },
  },
  common: {
    checkNow: { en: "Check Now", hi: "अभी जाँचें" },
    find: { en: "Find", hi: "ढूँढें" },
    submit: { en: "Submit", hi: "भेजें" },
    loading: { en: "Loading...", hi: "लोड हो रहा है..." },
    error: { en: "Error", hi: "गलती" },
    success: { en: "Success", hi: "सफलता" },
    cancel: { en: "Cancel", hi: "रद्द करें" },
    close: { en: "Close", hi: "बंद करें" },
    share: { en: "Share", hi: "साझा करें" },
    copy: { en: "Copy", hi: "कॉपी करें" },
    copied: { en: "Copied!", hi: "कॉपी हो गया!" },
  },
  chat: {
    placeholder: { en: "Type your question...", hi: "अपना सवाल यहाँ लिखिए..." },
    send: { en: "Send", hi: "भेजें" },
    welcomeTitle: { en: "Welcome!", hi: "स्वागत है!" },
    welcomeSubtitle: {
      en: "Ask anything - voter list, booth, EVM, timeline. Or choose a suggestion below.",
      hi: "कुछ भी पूछिए - मतदाता सूची, बूथ, ईवीएम, टाइमलाइन। या नीचे से एक सुझाव चुनिए।",
    },
  },
  voterCheck: {
    title: { en: "Are You On The Guest List?", hi: "क्या आप गेस्ट लिस्ट में हैं?" },
    subtitle: {
      en: "Check your name in the voter list without any hassle.",
      hi: "मतदाता सूची में अपना नाम आसानी से जाँचिए।",
    },
    nameLabel: { en: "Your Name (Full Name)", hi: "आपका नाम (पूरा नाम)" },
    namePlaceholder: { en: "Rajesh Kumar", hi: "राजेश कुमार" },
    stateLabel: { en: "State", hi: "राज्य" },
    statePlaceholder: { en: "Choose your state", hi: "अपना राज्य चुनें" },
    dobLabel: { en: "Date of Birth", hi: "जन्म तिथि" },
    checkButton: { en: "Check", hi: "जाँचें" },
    checking: { en: "Searching...", hi: "खोज रहे हैं..." },
    foundTitle: { en: "Congratulations!", hi: "बधाई हो!" },
    notFoundTitle: { en: "Oh no! Name not found", hi: "अरे! नाम नहीं मिला" },
    voterIdLabel: { en: "Voter ID", hi: "मतदाता पहचान पत्र" },
    shareText: {
      en: "I'm ready to vote with Chunav Mitra! Voter ID: {voter_id} | Booth: {booth_name}",
      hi: "मैं Chunav Mitra के साथ वोट देने के लिए तैयार हूँ! वोटर आईडी: {voter_id} | बूथ: {booth_name}",
    },
    shareHashtags: {
      en: "#ChunavMitra #VoteKaro #PromptWars2026",
      hi: "#ChunavMitra #VoteKaro #PromptWars2026",
    },
  },
  booth: {
    title: { en: "Find Your Mandap", hi: "अपना मंडप ढूँढें" },
    subtitle: {
      en: "Your polling booth - exact location, distance, and map link.",
      hi: "आपका पोलिंग बूथ - सही लोकेशन, दूरी और मैप लिंक के साथ।",
    },
    pincodePlaceholder: { en: "Pincode (e.g. 110001)", hi: "पिनकोड (जैसे 110001)" },
    findButton: { en: "Find", hi: "ढूँढें" },
    useGps: { en: "Use GPS", hi: "GPS का उपयोग करें" },
    yourMandap: { en: "Your Mandap", hi: "आपका मंडप" },
  },
  dictionary: {
    title: { en: "Election Words, Shaadi Style", hi: "चुनावी शब्द, शादी की शैली में" },
    subtitle: {
      en: "Every election term with a shaadi analogy. Choose and learn.",
      hi: "हर चुनावी शब्द शादी की मिसाल के साथ। चुनिए और सीखिए।",
    },
    explainButton: { en: "Explain", hi: "समझाओ" },
    shaadiAnalogy: { en: "Shaadi Analogy", hi: "शादी वाली मिसाल" },
    simpleExplanation: { en: "Simple Explanation", hi: "आसान समझाइश" },
    actionStep: { en: "Your Action Step", hi: "अब आपको क्या करना चाहिए" },
    funFact: { en: "Fun Fact", hi: "मज़ेदार तथ्य" },
  },
  timeline: {
    title: { en: "Election Timeline", hi: "चुनाव टाइमलाइन" },
    subtitle: {
      en: "All ceremonies, all dates in one place.",
      hi: "सारी रस्में और सारी तारीखें एक ही जगह।",
    },
    currentPhase: { en: "Current Phase", hi: "वर्तमान चरण" },
    daysRemaining: { en: "Days Left", hi: "बचे हुए दिन" },
    next: { en: "Next", hi: "अगला" },
  },
  toast: {
    voterFound: { en: "Congratulations! You're on the list!", hi: "बधाई हो! आपका नाम सूची में है!" },
    voterNotFound: { en: "Name not found. Check on ECI website.", hi: "नाम नहीं मिला। ECI वेबसाइट पर जाँचें।" },
    boothFound: { en: "Your Mandap found!", hi: "आपका मंडप मिल गया!" },
    apiError: { en: "Could not connect to server. Try again.", hi: "सर्वर से कनेक्ट नहीं हो पाया। फिर कोशिश करें।" },
    voterIdCopied: { en: "Voter ID copied!", hi: "वोटर आईडी कॉपी हो गया!" },
    shareSuccess: { en: "Shared successfully!", hi: "सफलतापूर्वक साझा किया गया!" },
    shareFailed: { en: "Could not share. Copied to clipboard instead.", hi: "साझा नहीं हो पाया। क्लिपबोर्ड पर कॉपी कर दिया गया।" },
  },
  footer: {
    shortcuts: {
      en: "Shortcuts: / for Chat · V for Voter Check · B for Booth",
      hi: "शॉर्टकट: / चैट के लिए · V मतदाता जाँच · B बूथ के लिए",
    },
  },
  hero: {
    title: { en: "Chunav Mitra", hi: "चुनाव मित्र" },
    subtitle: {
      en: "India's elections explained through the magic of a desi shaadi. Voter list ka guest list, booth ka mandap, vote ka shagun.",
      hi: "भारत के चुनाव एक देसी शादी की मिसाल से समझिए। मतदाता सूची यानी गेस्ट लिस्ट, बूथ यानी मंडप, और वोट यानी शगुन।",
    },
    chatButton: { en: "Talk to Pandit Ji", hi: "पंडित जी से बात करें" },
    checkButton: { en: "Check Guest List", hi: "गेस्ट लिस्ट जाँचें" },
    stats1: { en: "28 States", hi: "28 राज्य" },
    stats2: { en: "970M+ Voters", hi: "970M+ मतदाता" },
    stats3: { en: "22 Languages", hi: "22 भाषाएँ" },
    stats4: { en: "World's Biggest Democracy", hi: "दुनिया का सबसे बड़ा लोकतंत्र" },
    featuresTitle: { en: "5 Mandap, One Destination", hi: "5 मंडप, एक मंज़िल" },
    featuresSubtitle: { en: "Wedding Rituals", hi: "शादी की रस्में" },
    analogyTitle: { en: "Election ≈ Indian Wedding", hi: "चुनाव ≈ भारतीय शादी" },
    analogySubtitle: { en: "The Analogy", hi: "मिसाल" },
  },
};

export function t(key: string, lang: Lang): string {
  const keys = key.split(".");
  let value: unknown = translations;

  for (const keyPart of keys) {
    if (typeof value === "object" && value !== null && keyPart in value) {
      value = (value as Record<string, unknown>)[keyPart];
    } else {
      return key;
    }
  }

  if (typeof value === "object" && value !== null && lang in value) {
    return String((value as Record<string, unknown>)[lang]);
  }

  if (typeof value === "object" && value !== null && "en" in value) {
    return String((value as Record<string, unknown>).en);
  }

  return key;
}

function NotFoundComponent() {
  const { lang } = useLang();

  return (
    <Layout disableAmbientEffects>
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <div className="max-w-md text-center">
          <div className="font-display text-8xl text-gradient-gold">404</div>
          <h2 className="mt-4 text-xl font-semibold">
            {lang === "hi"
              ? "यह रास्ता शादी तक नहीं जाता!"
              : "This path doesn't lead to the wedding!"}
          </h2>
          <p className="mt-2 text-sm text-cream/70">
            {lang === "hi"
              ? "जिस पेज की आप तलाश कर रहे हैं, वह गेस्ट लिस्ट में नहीं है।"
              : "The page you're looking for is not on the guest list."}
          </p>
          <a
            href="/"
            className="mt-6 inline-flex rounded-full bg-mandap px-6 py-2.5 text-sm font-semibold text-navy shadow-gold"
          >
            {lang === "hi" ? "वापस मंडप चलें" : "Back to Mandap"}
          </a>
        </div>
      </div>
    </Layout>
  );
}

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Chunav Mitra - Desh ki Sabse Badi Shaadi" },
      {
        name: "description",
        content:
          "AI-powered Indian election assistant explaining elections through Desi wedding analogies. Voter check, booth finder, timeline, and live chat in Hindi and English.",
      },
      { name: "author", content: "Chunav Mitra" },
      { name: "theme-color", content: "#FF6B35" },
      { property: "og:title", content: "Chunav Mitra - Desh ki Sabse Badi Shaadi" },
      {
        property: "og:description",
        content: "Desh ki sabse badi shaadi ke guest hain aap! AI-powered Indian election assistant.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&family=Tiro+Devanagari+Hindi&display=swap",
      },
      { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
      { rel: "alternate icon", href: "/favicon.svg" },
      { rel: "apple-touch-icon", href: "/icon-192.png" },
      { rel: "manifest", href: "/manifest.json" },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
});

function RootShell({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    const saved = window.localStorage.getItem("chunav-mitra-lang");
    if (saved === "hi" || saved === "en") {
      setLangState(saved);
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang === "hi" ? "hi" : "en";
    document.documentElement.dir = "ltr";
    window.localStorage.setItem("chunav-mitra-lang", lang);
  }, [lang]);

  const toggleLang = useCallback(() => {
    setLangState((previous) => (previous === "en" ? "hi" : "en"));
  }, []);

  const setLang = useCallback((newLang: Lang) => {
    setLangState(newLang);
  }, []);

  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <head>
        <HeadContent />
      </head>
      <body>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded focus:bg-saffron focus:px-4 focus:py-2 focus:text-white"
        >
          Skip to main content
        </a>
        <LangContext.Provider value={{ lang, toggleLang, setLang }}>
          {children}
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: "rgba(10, 10, 26, 0.95)",
                border: "1px solid rgba(200, 169, 106, 0.3)",
                color: "#FFF8F0",
              },
            }}
          />
        </LangContext.Provider>
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  return <Outlet />;
}
