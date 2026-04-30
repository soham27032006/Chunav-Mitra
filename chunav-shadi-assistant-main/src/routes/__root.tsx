import { Outlet, createRootRoute, HeadContent, Scripts } from "@tanstack/react-router";
import { createContext, useContext, useState, useCallback, useEffect } from "react";

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
  toggleLang: () => {},
  setLang: () => {},
});

export function useLang() {
  return useContext(LangContext);
}

// Translation dictionary
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
    checkNow: { en: "Check Now", hi: "Check Karo" },
    find: { en: "Find", hi: "Dhoondho" },
    submit: { en: "Submit", hi: "Bhejo" },
    loading: { en: "Loading...", hi: "Loading..." },
    error: { en: "Error", hi: "Galti" },
    success: { en: "Success", hi: "Safalta" },
    cancel: { en: "Cancel", hi: "Cancel" },
    close: { en: "Close", hi: "Band Karein" },
    share: { en: "Share", hi: "Share Karein" },
    copy: { en: "Copy", hi: "Copy Karein" },
    copied: { en: "Copied!", hi: "Copy Ho Gaya!" },
  },
  chat: {
    placeholder: { en: "Type your question...", hi: "Apna sawaal yahaan likho..." },
    send: { en: "Send", hi: "Bhejo" },
    welcomeTitle: { en: "Welcome!", hi: "Namaste! Swagat hai aapka." },
    welcomeSubtitle: { en: "Ask anything — voter list, booth, EVM, timeline. Or choose a suggestion below.", hi: "Kuch bhi poocho — voter list, booth, EVM, timeline. Ya neeche se ek suggestion choose karo." },
  },
  voterCheck: {
    title: { en: "Are You On The Guest List?", hi: "Kya Aap Guest List Mein Hain?" },
    subtitle: { en: "Check your name in the voter list — without any hassle.", hi: "Apna naam check karo voter list mein — bina kisi jhanjhat ke." },
    nameLabel: { en: "Your Name (Full Name)", hi: "Aapka Naam (Full Name)" },
    namePlaceholder: { en: "Rajesh Kumar", hi: "Rajesh Kumar" },
    stateLabel: { en: "State", hi: "Rajya" },
    statePlaceholder: { en: "Choose your state", hi: "Apna rajya chunein" },
    dobLabel: { en: "Date of Birth", hi: "Janam Tithi" },
    checkButton: { en: "Check", hi: "Check Karein" },
    checking: { en: "Searching...", hi: "Dhoondh rahe hain..." },
    foundTitle: { en: "Congratulations!", hi: "Mubarak ho!" },
    notFoundTitle: { en: "Oh no! Name not found", hi: "Oho! Naam nahi mila" },
    voterIdLabel: { en: "Voter ID", hi: "Voter ID" },
    shareText: { en: "I'm ready to vote with Chunav Mitra! Voter ID: {voter_id} | Booth: {booth_name}", hi: "Main Chunav Mitra ke saath vote dene ke liye taiyaar hoon! Voter ID: {voter_id} | Booth: {booth_name}" },
    shareHashtags: { en: "#ChunavMitra #VoteKaro #PromptWars2026", hi: "#ChunavMitra #VoteKaro #PromptWars2026" },
  },
  booth: {
    title: { en: "Find Your Mandap", hi: "Apna Mandap Dhundho" },
    subtitle: { en: "Your polling booth — exact location, distance, and Maps link.", hi: "Aapka polling booth — exact location, distance, aur Maps link." },
    pincodePlaceholder: { en: "Pincode (e.g. 110001)", hi: "Pincode (jaise 110001)" },
    findButton: { en: "Find", hi: "Dhoondho" },
    useGps: { en: "Use GPS", hi: "GPS Use Karein" },
    yourMandap: { en: "Your Mandap", hi: "Aapka Mandap" },
  },
  dictionary: {
    title: { en: "Election Words, Shaadi Style", hi: "Election Words, Shaadi Style" },
    subtitle: { en: "Every election term — with a shaadi analogy. Choose and learn.", hi: "Har election term — ek shaadi analogy ke saath. Chuno aur seekho." },
    explainButton: { en: "Explain", hi: "Samjhao" },
    shaadiAnalogy: { en: "Shaadi Analogy", hi: "Shaadi Analogy" },
    simpleExplanation: { en: "Simple Explanation", hi: "Simple Explanation" },
    actionStep: { en: "Your Action Step", hi: "Aapka Action Step" },
    funFact: { en: "Fun Fact", hi: "Mazedaar Fact" },
  },
  timeline: {
    title: { en: "Election Timeline", hi: "Election Timeline" },
    subtitle: { en: "All ceremonies, all dates — in one place.", hi: "Saari rasmein, saari tareekhein — ek hi jagah." },
    currentPhase: { en: "Current Phase", hi: "Current Phase" },
    daysRemaining: { en: "Days Left", hi: "Din Bache" },
    next: { en: "Next", hi: "Next" },
  },
  toast: {
    voterFound: { en: "Congratulations! You're on the list!", hi: "Badhai ho! Aap list mein hain!" },
    voterNotFound: { en: "Name not found. Check on ECI website.", hi: "Naam nahi mila. ECI pe check karo." },
    boothFound: { en: "Your Mandap found!", hi: "Aapka Mandap mil gaya!" },
    apiError: { en: "Could not connect to server. Try again.", hi: "Server se baat nahi hui. Try again." },
    voterIdCopied: { en: "Voter ID copied!", hi: "Voter ID copy ho gaya!" },
    shareSuccess: { en: "Shared successfully!", hi: "Share ho gaya!" },
    shareFailed: { en: "Could not share. Copied to clipboard instead.", hi: "Share nahi ho paya. Clipboard pe copy kar diya." },
  },
  footer: {
    shortcuts: { en: "Shortcuts: / for Chat · V for Voter Check · B for Booth", hi: "Shortcuts: / Chat ke liye · V Voter Check · B Booth" },
  },
  hero: {
    title1: { en: "Desh ki sabse", hi: "Desh ki sabse" },
    title2: { en: "Badi Shaadi", hi: "Badi Shaadi" },
    title3: { en: "ke guest hain aap.", hi: "ke guest hain aap." },
    subtitle: { en: "India's elections — explained through the magic of a desi shaadi. Voter list ka guest list, booth ka mandap, vote ka shagun. Saare jawab, ek hi mandap mein.", hi: "India's elections — explained through the magic of a desi shaadi. Voter list ka guest list, booth ka mandap, vote ka shagun. Saare jawab, ek hi mandap mein." },
    chatButton: { en: "Talk to Pandit Ji", hi: "Pandit Ji se baat karo" },
    checkButton: { en: "Check Guest List", hi: "Guest List Check Karein" },
    stats1: { en: "28 States", hi: "28 States" },
    stats2: { en: "970M+ Voters", hi: "970M+ Voters" },
    stats3: { en: "22 Languages", hi: "22 Languages" },
    stats4: { en: "World's Biggest Democracy", hi: "World's Biggest Democracy" },
    featuresTitle: { en: "5 Mandap, Ek Manzil", hi: "5 Mandap, Ek Manzil" },
    featuresSubtitle: { en: "Shaadi Ke Rasme", hi: "Shaadi Ke Rasme" },
    analogyTitle: { en: "Election ≈ Indian Wedding", hi: "Election ≈ Indian Wedding" },
    analogySubtitle: { en: "The Analogy", hi: "The Analogy" },
  },
};

// Helper function to get translation
export function t(key: string, lang: Lang): string {
  const keys = key.split(".");
  let value: any = translations;
  for (const k of keys) {
    value = value?.[k];
  }
  return value?.[lang] || value?.en || key;
}

function NotFoundComponent() {
  const { lang } = useLang();
  return (
    <Layout>
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <div className="max-w-md text-center">
          <div className="font-display text-8xl text-gradient-gold">404</div>
          <h2 className="mt-4 text-xl font-semibold">
            {lang === "hi" ? "Yeh raasta toh shaadi mein hai hi nahi!" : "This path doesn't lead to the wedding!"}
          </h2>
          <p className="mt-2 text-sm text-cream/60">
            {lang === "hi" 
              ? "The page you're looking for is not on the guest list." 
              : "The page you're looking for is not on the guest list."}
          </p>
          <a
            href="/"
            className="mt-6 inline-flex rounded-full bg-mandap px-6 py-2.5 text-sm font-semibold text-navy shadow-gold"
          >
            {lang === "hi" ? "Wapas Mandap chalo" : "Back to Mandap"}
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
      { title: "Chunav Mitra — Desh ki Sabse Badi Shaadi" },
      {
        name: "description",
        content:
          "AI-powered Indian election assistant explaining elections through Desi wedding analogies. Voter check, booth finder, timeline, and live chat in Hindi & English.",
      },
      { name: "author", content: "Chunav Mitra" },
      { name: "theme-color", content: "#FF6B35" },
      { property: "og:title", content: "Chunav Mitra — Desh ki Sabse Badi Shaadi" },
      {
        property: "og:description",
        content:
          "Desh ki Sabse Badi Shaadi ke Guest Hain Aap! AI-powered Indian Election Assistant.",
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
      { rel: "manifest", href: "/manifest.json" },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
});

function RootShell({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    // Check localStorage for saved language preference
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("chunav-mitra-lang");
      if (saved === "hi" || saved === "en") return saved;
    }
    return "en";
  });

  const toggleLang = useCallback(() => {
    setLangState((prev) => {
      const newLang = prev === "en" ? "hi" : "en";
      if (typeof window !== "undefined") {
        localStorage.setItem("chunav-mitra-lang", newLang);
      }
      return newLang;
    });
  }, []);

  const setLang = useCallback((newLang: Lang) => {
    setLangState(newLang);
    if (typeof window !== "undefined") {
      localStorage.setItem("chunav-mitra-lang", newLang);
    }
  }, []);

  return (
    <html lang={lang}>
      <head>
        <HeadContent />
      </head>
      <body>
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
