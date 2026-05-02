import { Heart, Keyboard } from "lucide-react";
import { useLang, t } from "@/routes/__root";

export function Footer() {
  const { lang } = useLang();

  return (
    <footer className="relative z-10 mt-20 border-t border-gold/15">
      <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="font-display text-2xl text-gradient-gold">
            Chunav Mitra
          </div>
          <p className="max-w-xl text-sm text-cream/60">
            Made with <Heart className="inline h-3.5 w-3.5 fill-saffron text-saffron" /> by Soham Sahu
          </p>
          
          {/* Keyboard Shortcuts */}
          <div className="flex items-center gap-2 rounded-full border border-gold/20 bg-navy/30 px-4 py-2 text-[10px] text-cream/50">
            <Keyboard className="h-3 w-3" />
            <span>{t("footer.shortcuts", lang)}</span>
          </div>

          <div className="text-[10px] uppercase tracking-[0.3em] text-gold/50">
            Vote · Celebrate · Repeat
          </div>
        </div>
      </div>
    </footer>
  );
}
