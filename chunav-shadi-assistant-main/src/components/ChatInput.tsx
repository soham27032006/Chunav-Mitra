import { memo } from "react";
import { Send } from "lucide-react";
import type { KeyboardEvent, RefObject } from "react";
import type { Lang } from "@/lib/api";

type ChatInputProps = {
  value: string;
  onValueChange: (value: string) => void;
  onSubmit: () => void;
  streaming: boolean;
  lang: Lang;
  inputRef: RefObject<HTMLInputElement | null>;
};

function ChatInputComponent({
  value,
  onValueChange,
  onSubmit,
  streaming,
  lang,
  inputRef,
}: ChatInputProps) {
  const inputPlaceholder =
    lang === "hi" ? "अपना चुनाव सवाल यहाँ लिखिए..." : "Type your election question...";
  const chatHint =
    lang === "hi"
      ? "Enter दबाकर संदेश भेजें।"
      : "Press Enter to send your message.";
  const inputLabel =
    lang === "hi"
      ? "हिंदी या अंग्रेज़ी में अपना चुनाव प्रश्न लिखें"
      : "Type your election question in Hindi or English";
  const sendLabel = lang === "hi" ? "संदेश भेजें" : "Send message";

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      onSubmit();
    }
  };

  return (
    <div className="border-t border-gold/15 p-3 md:p-4">
      <div className="flex items-center gap-2">
        <input
          ref={inputRef}
          value={value}
          onChange={(event) => onValueChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={inputPlaceholder}
          aria-label={inputLabel}
          aria-describedby="chat-hint"
          aria-required="true"
          className="flex-1 rounded-full border border-gold/30 bg-navy/40 px-5 py-3 text-sm text-cream outline-none transition placeholder:text-cream/55 focus:border-gold/70 focus:bg-navy/60"
        />
        <span id="chat-hint" className="sr-only">
          {chatHint}
        </span>
        <button
          type="button"
          onClick={onSubmit}
          disabled={!value.trim() || streaming}
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-mandap text-navy shadow-gold transition-transform hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label={sendLabel}
        >
          <Send className="h-5 w-5" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}

export const ChatInput = memo(ChatInputComponent);
