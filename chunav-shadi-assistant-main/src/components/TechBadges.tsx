import { motion } from "framer-motion";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface TechBadge {
  name: string;
  shortName: string;
  color: string;
  bgColor: string;
  description: string;
  icon?: string;
}

const TECH_BADGES: TechBadge[] = [
  {
    name: "Google Gemini 1.5 Flash",
    shortName: "Gemini",
    color: "#4285F4",
    bgColor: "rgba(66, 133, 244, 0.15)",
    description: "Powers the AI chat with shaadi analogy system prompt. Supports SSE streaming for real-time responses in Hindi & English.",
    icon: "🧠",
  },
  {
    name: "Google Maps API",
    shortName: "Maps",
    color: "#EA4335",
    bgColor: "rgba(234, 67, 53, 0.15)",
    description: "Embeds interactive maps for booth finder. Shows exact distance and provides direct navigation links.",
    icon: "🗺️",
  },
  {
    name: "Google Translate API",
    shortName: "Translate",
    color: "#34A853",
    bgColor: "rgba(52, 168, 83, 0.15)",
    description: "Automatically detects language and translates between Hindi & English for seamless bilingual experience.",
    icon: "🌐",
  },
  {
    name: "Firebase + Firestore",
    shortName: "Firebase",
    color: "#FFCA28",
    bgColor: "rgba(255, 202, 40, 0.15)",
    description: "Stores chat history and session data. Tracks usage stats in real-time with live counters.",
    icon: "🔥",
  },
  {
    name: "React 19",
    shortName: "React",
    color: "#61DAFB",
    bgColor: "rgba(97, 218, 251, 0.15)",
    description: "Latest React with hooks, TanStack Router for navigation, and concurrent features for smooth UI.",
    icon: "⚛️",
  },
  {
    name: "FastAPI",
    shortName: "FastAPI",
    color: "#009688",
    bgColor: "rgba(0, 150, 136, 0.15)",
    description: "High-performance Python backend with async endpoints, SSE streaming, and auto-generated OpenAPI docs.",
    icon: "⚡",
  },
  {
    name: "Framer Motion",
    shortName: "Motion",
    color: "#FF6B9D",
    bgColor: "rgba(255, 107, 157, 0.15)",
    description: "Smooth page transitions, confetti animations, floating petals, and interactive UI animations.",
    icon: "✨",
  },
];

function Badge({ badge, index }: { badge: TechBadge; index: number }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: index * 0.08, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          whileHover={{ scale: 1.05, y: -2 }}
          className="group relative cursor-pointer"
        >
          <div
            className="flex items-center gap-2 rounded-full border px-4 py-2 transition-all duration-300 hover:shadow-lg"
            style={{
              borderColor: badge.color,
              backgroundColor: badge.bgColor,
              boxShadow: `0 0 20px ${badge.bgColor}`,
            }}
          >
            <span className="text-lg">{badge.icon}</span>
            <span
              className="font-semibold text-sm"
              style={{ color: badge.color }}
            >
              {badge.name}
            </span>
          </div>
        </motion.div>
      </TooltipTrigger>
      <TooltipContent
        side="top"
        className="max-w-xs border-gold/30 bg-navy/95 p-3 text-sm"
        sideOffset={8}
      >
        <p className="text-cream/90">{badge.description}</p>
      </TooltipContent>
    </Tooltip>
  );
}

export function TechBadges() {
  return (
    <TooltipProvider delayDuration={100}>
      <section className="relative px-4 py-12">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8 text-center">
            <div className="text-[10px] uppercase tracking-[0.3em] text-gold/70">
              Built With
            </div>
            <h2 className="mt-2 font-display text-3xl text-gradient-gold md:text-4xl">
              Google Tech Stack
            </h2>
            <p className="mx-auto mt-2 max-w-xl text-sm text-cream/60">
              Hover over badges to see how each technology powers Chunav Mitra
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3">
            {TECH_BADGES.map((badge, i) => (
              <Badge key={badge.name} badge={badge} index={i} />
            ))}
          </div>

          {/* Stats Row */}
          <div className="mt-10 grid grid-cols-2 gap-4 border-t border-gold/10 pt-8 sm:grid-cols-4">
            {[
              { value: "3", label: "Google APIs", icon: "🔌" },
              { value: "60s", label: "Demo Mode", icon: "⏱️" },
              { value: "22", label: "Languages Supported", icon: "🗣️" },
              { value: "970M+", label: "Potential Users", icon: "👥" },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="text-2xl font-bold text-gradient-gold md:text-3xl">
                  {stat.value}
                </div>
                <div className="mt-1 flex items-center justify-center gap-1 text-xs text-cream/60">
                  <span>{stat.icon}</span>
                  <span>{stat.label}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </TooltipProvider>
  );
}

export function TechBadgeInline({ name }: { name: string }) {
  const badge = TECH_BADGES.find((b) => b.name.includes(name) || b.shortName === name);
  if (!badge) return null;

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
          style={{
            borderColor: badge.color,
            backgroundColor: badge.bgColor,
            color: badge.color,
          }}
        >
          {badge.icon} {badge.shortName}
        </span>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-xs border-gold/30 bg-navy/95 p-2 text-xs">
        <p className="text-cream/90">{badge.description}</p>
      </TooltipContent>
    </Tooltip>
  );
}
