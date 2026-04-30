import { motion } from "framer-motion";

interface SkeletonCardProps {
  className?: string;
}

export function SkeletonCard({ className = "" }: SkeletonCardProps) {
  return (
    <div className={`rounded-3xl border border-gold/10 bg-navy/30 p-6 ${className}`}>
      <div className="animate-pulse space-y-4">
        <div className="h-4 w-1/3 rounded bg-gold/20" />
        <div className="h-8 w-2/3 rounded bg-gold/20" />
        <div className="h-20 rounded bg-gold/10" />
      </div>
    </div>
  );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 rounded bg-gold/20"
          style={{ width: `${100 - (i * 15)}%` }}
        />
      ))}
    </div>
  );
}

export function SkeletonTimeline() {
  return (
    <div className="space-y-8">
      {Array.from({ length: 5 }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="relative grid items-center gap-4 md:grid-cols-2"
        >
          <div className="ml-14 md:ml-0 md:pr-12 md:text-right">
            <div className="rounded-3xl border border-gold/10 bg-navy/30 p-5">
              <div className="animate-pulse space-y-2">
                <div className="h-3 w-20 rounded bg-gold/20" />
                <div className="h-6 w-32 rounded bg-gold/20" />
                <div className="h-4 w-full rounded bg-gold/10" />
              </div>
            </div>
          </div>
          <div className="absolute left-6 -translate-x-1/2 md:left-1/2">
            <div className="h-10 w-10 rounded-full border-2 border-gold/20 bg-navy animate-pulse" />
          </div>
          <div className="hidden md:block" />
        </motion.div>
      ))}
    </div>
  );
}

export function SkeletonStats() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div
          key={i}
          className="rounded-2xl border border-gold/10 bg-navy/30 p-6"
        >
          <div className="animate-pulse space-y-2">
            <div className="h-3 w-24 rounded bg-gold/20" />
            <div className="h-10 w-20 rounded bg-gold/20" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonChat() {
  return (
    <div className="space-y-4 p-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className={`flex gap-3 ${i % 2 === 0 ? "flex-row-reverse" : ""}`}
        >
          <div className="h-9 w-9 shrink-0 rounded-full bg-gold/20 animate-pulse" />
          <div
            className={`max-w-[80%] rounded-2xl p-4 ${
              i % 2 === 0
                ? "bg-saffron/20"
                : "border border-gold/10 bg-navy/30"
            }`}
          >
            <div className="animate-pulse space-y-2">
              <div className="h-3 w-full rounded bg-gold/20" />
              <div className="h-3 w-3/4 rounded bg-gold/20" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonBooth() {
  return (
    <div className="rounded-3xl border border-gold/10 bg-navy/30 overflow-hidden">
      <div className="grid md:grid-cols-2">
        <div className="p-6 md:p-8 space-y-4">
          <div className="animate-pulse space-y-3">
            <div className="h-3 w-24 rounded bg-gold/20" />
            <div className="h-8 w-48 rounded bg-gold/20" />
            <div className="h-4 w-full rounded bg-gold/10" />
            <div className="h-4 w-32 rounded bg-gold/20" />
            <div className="h-20 rounded bg-gold/10" />
          </div>
        </div>
        <div className="min-h-[300px] bg-navy/50 animate-pulse" />
      </div>
    </div>
  );
}

export function SkeletonVoterResult() {
  return (
    <div className="rounded-3xl border border-gold/10 bg-navy/30 p-6">
      <div className="animate-pulse flex items-start gap-4">
        <div className="h-14 w-14 shrink-0 rounded-2xl bg-gold/20" />
        <div className="flex-1 space-y-3">
          <div className="h-6 w-48 rounded bg-gold/20" />
          <div className="h-4 w-full rounded bg-gold/10" />
          <div className="h-10 w-32 rounded bg-gold/20" />
        </div>
      </div>
    </div>
  );
}

export function SkeletonDictionary() {
  return (
    <div className="space-y-5">
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="rounded-3xl border border-gold/10 bg-navy/30 p-6"
        >
          <div className="animate-pulse flex gap-4">
            <div className="h-12 w-12 shrink-0 rounded-2xl bg-gold/20" />
            <div className="flex-1 space-y-2">
              <div className="h-5 w-32 rounded bg-gold/20" />
              <div className="h-4 w-full rounded bg-gold/10" />
              <div className="h-4 w-3/4 rounded bg-gold/10" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
