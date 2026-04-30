import { motion } from "framer-motion";
import { MessageCircle, Lightbulb, Vote, ArrowRight, Sparkles } from "lucide-react";
import { useLang, t } from "@/routes/__root";
import { Link } from "@tanstack/react-router";

const STEPS = [
  {
    icon: MessageCircle,
    emoji: "🗣️",
    title: { en: "Poocho", hi: "पूछो" },
    subtitle: { en: "Ask", hi: "पूछिए" },
    description: {
      en: "Ask anything in Hindi or English. Voice input bhi chalega!",
      hi: "Kuch bhi poochiye Hindi ya English mein. Voice input bhi chalega!",
    },
    action: { en: "Chat with Pandit Ji", hi: "Pandit Ji se baat karo" },
    link: "/chat",
    color: "from-saffron to-gold",
    delay: 0,
  },
  {
    icon: Lightbulb,
    emoji: "🎊",
    title: { en: "Samjho", hi: "समझो" },
    subtitle: { en: "Understand", hi: "समझिए" },
    description: {
      en: "Get answers with shaadi analogies that actually make sense.",
      hi: "Shaadi analogy ke saath jawab jo actually samajh mein aaye.",
    },
    action: { en: "Try Dictionary", hi: "Dictionary try karo" },
    link: "/dictionary",
    color: "from-gold to-rose-gold",
    delay: 0.15,
  },
  {
    icon: Vote,
    emoji: "🗳️",
    title: { en: "Karo", hi: "करो" },
    subtitle: { en: "Act", hi: "कीजिए" },
    description: {
      en: "Check your voter status, find your booth, and be election-ready.",
      hi: "Apna voter status check karo, booth dhoondho, aur taiyaar raho.",
    },
    action: { en: "Check Guest List", hi: "Guest List check karo" },
    link: "/voter-check",
    color: "from-deep-green to-gold",
    delay: 0.3,
  },
];

export function HowItWorks() {
  const { lang } = useLang();

  return (
    <section className="relative px-4 py-20">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-16 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-block rounded-full border border-gold/30 bg-navy/40 px-4 py-1 text-[10px] uppercase tracking-[0.3em] text-gold"
          >
            {lang === "hi" ? "3 Aasan Kadam" : "3 Easy Steps"}
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="mt-4 font-display text-4xl text-gradient-gold md:text-5xl"
          >
            {lang === "hi" ? "Kaam Kaise Karega" : "How It Works"}
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mx-auto mt-4 max-w-2xl text-cream/70"
          >
            {lang === "hi"
              ? "Itna aasan ki daadi wale bhi samajh jaayein. No jargon, only shaadi style."
              : "So easy even your grandparents will get it. No jargon, only shaadi style."}
          </motion.p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connecting Line (Desktop) */}
          <div className="absolute left-1/2 top-24 hidden h-[calc(100%-8rem)] w-px -translate-x-1/2 bg-gradient-to-b from-gold/0 via-gold/50 to-gold/0 lg:block" />

          <div className="space-y-8 lg:space-y-16">
            {STEPS.map((step, index) => (
              <motion.div
                key={step.title.en}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ delay: step.delay, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="relative"
              >
                <div
                  className={`grid items-center gap-8 lg:grid-cols-2 ${
                    index % 2 === 1 ? "lg:[&>*:first-child]:order-2" : ""
                  }`}
                >
                  {/* Content */}
                  <div className={index % 2 === 1 ? "lg:pl-12" : "lg:pr-12"}>
                    <div
                      className={`rounded-3xl border border-gold/20 bg-navy/40 p-8 transition-all duration-500 hover:border-gold/40 hover:shadow-glow ${
                        index % 2 === 1 ? "lg:text-left" : "lg:text-right"
                      }`}
                    >
                      {/* Step Number */}
                      <div
                        className={`mb-4 inline-flex items-center gap-2 rounded-full border border-gold/30 bg-navy/60 px-3 py-1 text-xs font-semibold text-gold ${
                          index % 2 === 1 ? "lg:justify-start" : "lg:justify-end lg:flex-row-reverse"
                        }`}
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-gold" />
                        Step {index + 1}/3
                      </div>

                      {/* Title */}
                      <div
                        className={`flex items-center gap-3 ${
                          index % 2 === 1 ? "lg:justify-start" : "lg:justify-end lg:flex-row-reverse"
                        }`}
                      >
                        <span className="text-4xl">{step.emoji}</span>
                        <div>
                          <h3 className="font-display text-3xl font-bold text-gradient-gold">
                            {step.title[lang]}
                          </h3>
                          <p className="text-sm text-cream/60">{step.subtitle[lang]}</p>
                        </div>
                      </div>

                      {/* Description */}
                      <p className={`mt-4 text-cream/80 ${index % 2 === 1 ? "" : "lg:text-right"}`}>
                        {step.description[lang]}
                      </p>

                      {/* Action Link */}
                      <Link
                        to={step.link}
                        className={`mt-6 inline-flex items-center gap-2 rounded-full bg-gradient-to-r ${step.color} px-5 py-2.5 font-semibold text-navy shadow-gold transition-transform hover:scale-105 ${
                          index % 2 === 1 ? "" : "lg:flex-row-reverse"
                        }`}
                      >
                        <step.icon className="h-4 w-4" />
                        {step.action[lang]}
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </div>
                  </div>

                  {/* Icon Circle (Desktop) */}
                  <div className="hidden lg:flex lg:justify-center">
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className={`relative flex h-20 w-20 items-center justify-center rounded-full border-4 border-navy bg-gradient-to-br ${step.color} shadow-glow`}
                    >
                      <step.icon className="h-8 w-8 text-navy" />
                      <motion.div
                        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="absolute inset-0 rounded-full border border-gold/30"
                      />
                    </motion.div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="mt-16 text-center"
        >
        <div className="inline-flex items-center gap-2 rounded-full border border-gold/30 bg-navy/40 px-6 py-3">
          <Sparkles className="h-5 w-5 text-gold" />
          <span className="text-cream/80">
            {lang === "hi"
              ? "Taiyaar hain? Shuru karo!"
              : "Ready? Let's begin!"}
          </span>
        </div>
        </motion.div>
      </div>
    </section>
  );
}
