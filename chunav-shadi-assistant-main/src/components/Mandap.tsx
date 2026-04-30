import { motion } from "framer-motion";

/**
 * Animated Mandap / Lotus emblem — pure SVG, with rotating outer ring,
 * pulsing inner glow, and lotus petals.
 */
export function Mandap({ size = 320 }: { size?: number }) {
  return (
    <div className="relative" style={{ width: size, height: size }}>
      {/* Outer glow */}
      <div
        className="absolute inset-0 rounded-full blur-3xl opacity-70"
        style={{
          background:
            "radial-gradient(circle, oklch(0.85 0.16 88 / 70%), transparent 65%)",
        }}
      />

      {/* Soft breathing glow */}
      <motion.div
        className="absolute inset-0 rounded-full"
        animate={{ opacity: [0.55, 0.85, 0.55], scale: [1, 1.03, 1] }}
        transition={{ duration: 7, repeat: Infinity, ease: [0.4, 0, 0.6, 1] }}
        style={{
          background:
            "radial-gradient(circle, oklch(0.85 0.16 88 / 55%), transparent 70%)",
          filter: "blur(40px)",
        }}
      />

      {/* Rotating ring — slow, premium */}
      <motion.svg
        className="absolute inset-0"
        viewBox="0 0 200 200"
        animate={{ rotate: 360 }}
        transition={{ duration: 90, repeat: Infinity, ease: "linear" }}
      >
        <defs>
          <linearGradient id="ringGrad" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stopColor="oklch(0.85 0.16 88)" />
            <stop offset="50%" stopColor="oklch(0.72 0.18 45)" />
            <stop offset="100%" stopColor="oklch(0.78 0.11 35)" />
          </linearGradient>
        </defs>
        <circle
          cx="100"
          cy="100"
          r="92"
          fill="none"
          stroke="url(#ringGrad)"
          strokeWidth="0.6"
          strokeDasharray="2 4"
        />
        <circle
          cx="100"
          cy="100"
          r="84"
          fill="none"
          stroke="url(#ringGrad)"
          strokeWidth="1"
          opacity="0.6"
        />
        {/* Decorative dots */}
        {Array.from({ length: 24 }).map((_, i) => {
          const a = (i / 24) * Math.PI * 2;
          return (
            <circle
              key={i}
              cx={100 + Math.cos(a) * 88}
              cy={100 + Math.sin(a) * 88}
              r="1.6"
              fill="oklch(0.85 0.16 88)"
            />
          );
        })}
      </motion.svg>

      {/* Counter-rotating ring */}
      <motion.svg
        className="absolute inset-0"
        viewBox="0 0 200 200"
        animate={{ rotate: -360 }}
        transition={{ duration: 140, repeat: Infinity, ease: "linear" }}
      >
        <circle
          cx="100"
          cy="100"
          r="74"
          fill="none"
          stroke="oklch(0.85 0.16 88 / 40%)"
          strokeWidth="0.5"
          strokeDasharray="1 3"
        />
      </motion.svg>

      {/* Lotus — gentle breathing */}
      <motion.svg
        className="absolute inset-0"
        viewBox="0 0 200 200"
        animate={{ scale: [1, 1.025, 1], rotate: [0, 1.2, 0] }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: [0.4, 0, 0.6, 1],
        }}
      >
        <defs>
          <linearGradient id="petalGrad" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="oklch(0.95 0.1 88)" />
            <stop offset="100%" stopColor="oklch(0.72 0.18 45)" />
          </linearGradient>
          <radialGradient id="centerGrad">
            <stop offset="0%" stopColor="oklch(0.95 0.1 88)" />
            <stop offset="100%" stopColor="oklch(0.55 0.2 35)" />
          </radialGradient>
        </defs>

        {/* 8 lotus petals */}
        {Array.from({ length: 8 }).map((_, i) => (
          <g key={i} transform={`rotate(${(i * 360) / 8} 100 100)`}>
            <path
              d="M100 40 C 110 60, 110 80, 100 100 C 90 80, 90 60, 100 40 Z"
              fill="url(#petalGrad)"
              opacity="0.92"
              stroke="oklch(0.85 0.16 88)"
              strokeWidth="0.4"
            />
          </g>
        ))}

        {/* Inner petals */}
        {Array.from({ length: 8 }).map((_, i) => (
          <g key={`b-${i}`} transform={`rotate(${(i * 360) / 8 + 22.5} 100 100)`}>
            <path
              d="M100 60 C 106 75, 106 88, 100 100 C 94 88, 94 75, 100 60 Z"
              fill="oklch(0.85 0.16 88)"
              opacity="0.85"
            />
          </g>
        ))}

        {/* Center jewel */}
        <circle cx="100" cy="100" r="14" fill="url(#centerGrad)" />
        <circle cx="100" cy="100" r="6" fill="oklch(0.98 0.05 88)" />
      </motion.svg>

      {/* Sparkle — soft pulse */}
      <motion.div
        className="absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white"
        animate={{ scale: [0.7, 1.25, 0.7], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 4, repeat: Infinity, ease: [0.4, 0, 0.6, 1] }}
        style={{ boxShadow: "0 0 30px oklch(0.95 0.1 88)" }}
      />
    </div>
  );
}
