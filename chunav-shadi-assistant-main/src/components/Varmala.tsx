import { motion } from "framer-motion";
import { useMemo } from "react";
import varmalaImg from "@/assets/varmala-scene.png";

interface VarmalaProps {
  size?: number;
}

export function Varmala({ size = 480 }: VarmalaProps) {
  const sparkles = useMemo(
    () =>
      Array.from({ length: 18 }, (_, i) => ({
        id: i,
        x: 30 + Math.random() * 40,
        y: 35 + Math.random() * 30,
        delay: Math.random() * 3,
        duration: 2 + Math.random() * 2,
        scale: 0.4 + Math.random() * 0.8,
      })),
    []
  );

  const petals = useMemo(
    () =>
      Array.from({ length: 14 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        delay: Math.random() * 6,
        duration: 7 + Math.random() * 5,
        rotate: Math.random() * 360,
        scale: 0.5 + Math.random() * 0.7,
      })),
    []
  );

  return (
    <div
      className="relative"
      style={{ width: size, height: size, perspective: 1200 }}
    >
      {/* Radial divine background */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "radial-gradient(circle at 50% 45%, rgba(255,170,60,0.45) 0%, rgba(217,119,6,0.25) 25%, rgba(76,29,149,0.35) 55%, rgba(15,23,42,0) 80%)",
          filter: "blur(8px)",
        }}
      />

      {/* Outer rotating glow ring */}
      <motion.div
        className="absolute inset-4 rounded-full"
        style={{
          background:
            "conic-gradient(from 0deg, rgba(251,191,36,0) 0%, rgba(251,191,36,0.5) 25%, rgba(244,63,94,0.4) 50%, rgba(251,191,36,0.5) 75%, rgba(251,191,36,0) 100%)",
          filter: "blur(20px)",
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 24, repeat: Infinity, ease: "linear" }}
      />

      {/* Halo behind figures */}
      <motion.div
        className="absolute left-1/2 top-[28%] -translate-x-1/2 rounded-full"
        style={{
          width: size * 0.55,
          height: size * 0.55,
          background:
            "radial-gradient(circle, rgba(255,215,100,0.55) 0%, rgba(255,180,60,0.25) 40%, transparent 70%)",
          filter: "blur(6px)",
        }}
        animate={{ scale: [1, 1.08, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Main scene with levitation */}
      <motion.div
        className="relative h-full w-full"
        animate={{
          y: [0, -14, 0],
          rotateY: [-3, 3, -3],
        }}
        transition={{
          y: { duration: 5, repeat: Infinity, ease: "easeInOut" },
          rotateY: { duration: 9, repeat: Infinity, ease: "easeInOut" },
        }}
        style={{ transformStyle: "preserve-3d" }}
      >
        <img
          src={varmalaImg}
          alt="Lord Ram and Sita Varmala ceremony"
          width={1024}
          height={1024}
          className="relative z-10 h-full w-full object-contain drop-shadow-[0_20px_40px_rgba(251,191,36,0.4)]"
          style={{
            filter:
              "drop-shadow(0 0 30px rgba(255,180,60,0.45)) drop-shadow(0 0 60px rgba(244,63,94,0.25))",
          }}
        />

        {/* Garland golden glow particles (centered between figures) */}
        {sparkles.map((s) => (
          <motion.div
            key={s.id}
            className="absolute z-20 rounded-full"
            style={{
              left: `${s.x}%`,
              top: `${s.y}%`,
              width: 6,
              height: 6,
              background:
                "radial-gradient(circle, rgba(255,236,170,1) 0%, rgba(251,191,36,0.8) 40%, transparent 70%)",
              boxShadow: "0 0 12px rgba(251,191,36,0.9)",
            }}
            animate={{
              scale: [0, s.scale, 0],
              opacity: [0, 1, 0],
              y: [0, -20, -40],
            }}
            transition={{
              duration: s.duration,
              repeat: Infinity,
              delay: s.delay,
              ease: "easeOut",
            }}
          />
        ))}
      </motion.div>

      {/* Diya flames bottom-left */}
      <Diya className="absolute bottom-2 left-4 z-30" />
      <Diya className="absolute bottom-2 right-4 z-30" delay={0.3} />

      {/* Falling marigold petals */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {petals.map((p) => (
          <motion.div
            key={p.id}
            className="absolute"
            style={{
              left: `${p.x}%`,
              top: -20,
              width: 12,
              height: 12,
            }}
            animate={{
              y: [0, size + 40],
              x: [0, Math.sin(p.id) * 30, Math.cos(p.id) * 20],
              rotate: [p.rotate, p.rotate + 360],
              opacity: [0, 1, 1, 0],
            }}
            transition={{
              duration: p.duration,
              repeat: Infinity,
              delay: p.delay,
              ease: "linear",
            }}
          >
            <div
              className="h-full w-full rounded-full"
              style={{
                background:
                  "radial-gradient(circle at 30% 30%, #fbbf24 0%, #f97316 60%, #b45309 100%)",
                transform: `scale(${p.scale})`,
                boxShadow: "0 0 6px rgba(251,146,60,0.6)",
              }}
            />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function Diya({ className, delay = 0 }: { className?: string; delay?: number }) {
  return (
    <div className={className}>
      <div className="relative flex flex-col items-center">
        {/* Flame */}
        <motion.div
          className="relative"
          animate={{
            scaleY: [1, 1.15, 0.95, 1.1, 1],
            scaleX: [1, 0.92, 1.05, 0.95, 1],
          }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            ease: "easeInOut",
            delay,
          }}
        >
          <div
            className="h-8 w-4 rounded-full"
            style={{
              background:
                "radial-gradient(ellipse at 50% 80%, #fff7d6 0%, #fbbf24 35%, #f97316 65%, #dc2626 100%)",
              filter: "blur(0.5px)",
              boxShadow:
                "0 0 20px rgba(251,191,36,0.9), 0 0 40px rgba(249,115,22,0.6)",
            }}
          />
        </motion.div>
        {/* Diya bowl */}
        <div
          className="-mt-1 h-3 w-10 rounded-b-full"
          style={{
            background: "linear-gradient(180deg, #b45309 0%, #78350f 100%)",
            boxShadow: "0 4px 12px rgba(0,0,0,0.4), inset 0 -2px 4px rgba(0,0,0,0.3)",
          }}
        />
      </div>
    </div>
  );
}
