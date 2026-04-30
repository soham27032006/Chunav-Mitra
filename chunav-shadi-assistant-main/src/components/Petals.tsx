import { motion } from "framer-motion";
import { useMemo } from "react";

interface Petal {
  id: number;
  left: number;
  delay: number;
  duration: number;
  size: number;
  rotate: number;
  hue: number;
}

export function Petals({ count = 18 }: { count?: number }) {
  const petals = useMemo<Petal[]>(
    () =>
      Array.from({ length: count }).map((_, i) => ({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 10,
        duration: 12 + Math.random() * 14,
        size: 10 + Math.random() * 18,
        rotate: Math.random() * 360,
        hue: 30 + Math.random() * 30,
      })),
    [count],
  );

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {petals.map((p) => (
        <motion.div
          key={p.id}
          className="absolute -top-10"
          style={{ left: `${p.left}%` }}
          initial={{ y: -50, rotate: p.rotate, opacity: 0 }}
          animate={{
            y: typeof window !== "undefined" ? window.innerHeight + 100 : 1200,
            rotate: p.rotate + 540,
            opacity: [0, 1, 1, 0],
            x: [0, 30, -30, 20, 0],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: "linear",
          }}
        >
          <svg width={p.size} height={p.size} viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2C9 6 6 9 6 13a6 6 0 0012 0c0-4-3-7-6-11z"
              fill={`oklch(0.78 0.18 ${p.hue})`}
              opacity="0.85"
            />
            <circle cx="12" cy="14" r="2" fill="oklch(0.95 0.1 88)" />
          </svg>
        </motion.div>
      ))}
    </div>
  );
}
