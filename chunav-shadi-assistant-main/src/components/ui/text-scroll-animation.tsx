"use client";

import { motion } from "framer-motion";
import {
  BadgeCheck,
  BookOpen,
  Bot,
  HeartHandshake,
  Landmark,
  Languages,
  MapPinned,
  Sparkles,
  Vote,
} from "lucide-react";

const ICONS = [
  { Icon: Bot, label: "AI Samjhao", accent: "border-sky-400/45 bg-sky-400/10 text-sky-300" },
  { Icon: Vote, label: "Vote Ready", accent: "border-amber-400/45 bg-amber-400/10 text-amber-200" },
  { Icon: MapPinned, label: "Booth Finder", accent: "border-rose-400/45 bg-rose-400/10 text-rose-300" },
  { Icon: Languages, label: "2 Languages", accent: "border-emerald-400/45 bg-emerald-400/10 text-emerald-300" },
  { Icon: Landmark, label: "Election Guide", accent: "border-fuchsia-400/45 bg-fuchsia-400/10 text-fuchsia-300" },
  { Icon: BadgeCheck, label: "Trusted Flow", accent: "border-cyan-400/45 bg-cyan-400/10 text-cyan-300" },
  { Icon: BookOpen, label: "Shaadi Dictionary", accent: "border-violet-400/45 bg-violet-400/10 text-violet-300" },
  { Icon: HeartHandshake, label: "For Democracy", accent: "border-orange-400/45 bg-orange-400/10 text-orange-200" },
];

const TextScrollAnimation = () => {
  return (
    <section className="relative px-4 py-12 md:py-16">
      <div className="mx-auto max-w-6xl overflow-hidden rounded-[2rem] border border-gold/15 bg-[radial-gradient(circle_at_top,rgba(39,61,116,0.75),rgba(11,6,29,0.95)_70%)] shadow-card">
        <div className="border-b border-gold/10 px-6 py-4 text-center text-[11px] uppercase tracking-[0.42em] text-gold/60">
          Built for real voters
        </div>

        <div className="relative px-6 py-14 md:px-10 md:py-16">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,168,77,0.14),transparent_45%)]" />
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="relative text-center"
          >
            <div className="mb-5 text-[11px] uppercase tracking-[0.45em] text-gold/60">
              Chunav Mitra
            </div>
            <div className="font-display text-4xl font-bold leading-tight text-gradient-gold md:text-6xl lg:text-7xl">
              Fast actions, friendly guidance, zero confusion.
            </div>
            <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-cream/70 md:text-lg">
              Chunav Mitra homepage ko light aur fast rakha gaya hai, taaki voter help, booth
              guidance, dictionary aur timeline bina lag ke quickly accessible rahein.
            </p>
          </motion.div>

          <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {ICONS.map(({ Icon, label, accent }, index) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.35, delay: index * 0.04 }}
                className={`flex items-center gap-3 rounded-2xl border px-4 py-4 shadow-[0_0_30px_rgba(200,169,106,0.06)] ${accent}`}
              >
                <Icon className="h-5 w-5 shrink-0" />
                <span className="text-sm font-semibold md:text-base">{label}</span>
              </motion.div>
            ))}
          </div>

          <div className="mt-10 border-t border-gold/10 pt-8 text-center">
            <div className="font-display text-2xl text-[#efbfad] md:text-4xl">Chunav Mitra</div>
            <p className="mt-3 text-sm uppercase tracking-[0.32em] text-gold/65">
              Made with love by Soham Sahu
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export { TextScrollAnimation };
