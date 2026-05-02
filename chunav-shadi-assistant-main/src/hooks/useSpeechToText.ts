import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { api, type Lang } from "@/lib/api";

type SpeechRecognitionAlternativeLike = {
  transcript: string;
};

type SpeechRecognitionResultLike = {
  isFinal: boolean;
  0: SpeechRecognitionAlternativeLike;
  length: number;
};

type SpeechRecognitionEventLike = Event & {
  resultIndex: number;
  results: ArrayLike<SpeechRecognitionResultLike>;
};

type SpeechRecognitionErrorEventLike = Event & {
  error: string;
};

type SpeechRecognitionLike = EventTarget & {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onstart: ((event: Event) => void) | null;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null;
  onend: ((event: Event) => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
};

type SpeechRecognitionConstructorLike = new () => SpeechRecognitionLike;

type SpeechStatus = "idle" | "listening" | "processing";

type UseSpeechToTextOptions = {
  lang: Lang;
  onTranscript: (transcript: string) => void;
  onFocusInput: () => void;
};

type UseSpeechToTextResult = {
  status: SpeechStatus;
  interimTranscript: string;
  isSupported: boolean;
  tooltipText: string;
  toggleListening: () => Promise<void>;
};

type RecorderMode = "speech-recognition" | "media-recorder" | "unsupported";

function getSpeechRecognitionConstructor(): SpeechRecognitionConstructorLike | null {
  if (typeof window === "undefined") {
    return null;
  }

  const speechWindow = window as typeof window & {
    SpeechRecognition?: SpeechRecognitionConstructorLike;
    webkitSpeechRecognition?: SpeechRecognitionConstructorLike;
  };

  return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition ?? null;
}

function getRecognitionLanguage(lang: Lang): string {
  return lang === "hi" ? "hi-IN" : "en-IN";
}

function getUnsupportedMessage(lang: Lang): string {
  return lang === "hi"
    ? "Voice not supported in this browser."
    : "Voice not supported in this browser.";
}

function getPermissionDeniedMessage(lang: Lang): string {
  return lang === "hi"
    ? "Microphone access denied. Enable in browser settings."
    : "Microphone access denied. Enable in browser settings.";
}

function getNoSpeechMessage(lang: Lang): string {
  return lang === "hi"
    ? "No speech detected. Try again."
    : "No speech detected. Try again.";
}

function getNetworkMessage(lang: Lang): string {
  return lang === "hi"
    ? "Network issue while using voice. Try again."
    : "Network issue while using voice. Try again.";
}

function getCaptureMessage(lang: Lang): string {
  return lang === "hi"
    ? "Could not start voice input. Try again."
    : "Could not start voice input. Try again.";
}

function getMediaRecorderUnsupportedMessage(lang: Lang): string {
  return lang === "hi"
    ? "Voice not supported in this browser. Use Chrome."
    : "Voice not supported in this browser. Use Chrome.";
}

function getToastMessageForError(error: string, lang: Lang): string {
  if (error === "not-allowed" || error === "service-not-allowed") {
    return getPermissionDeniedMessage(lang);
  }
  if (error === "no-speech") {
    return getNoSpeechMessage(lang);
  }
  if (error === "network") {
    return getNetworkMessage(lang);
  }
  if (error === "audio-capture" || error === "aborted") {
    return getCaptureMessage(lang);
  }
  return getCaptureMessage(lang);
}

function showSpeechError(message: string) {
  toast.error(message, { duration: 3000 });
}

function clearRecognitionHandlers(recognition: SpeechRecognitionLike | null) {
  if (!recognition) {
    return;
  }

  recognition.onstart = null;
  recognition.onresult = null;
  recognition.onerror = null;
  recognition.onend = null;
}

export function useSpeechToText({
  lang,
  onTranscript,
  onFocusInput,
}: UseSpeechToTextOptions): UseSpeechToTextResult {
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const finalTranscriptRef = useRef("");
  const receivedResultRef = useRef(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const autoStopTimerRef = useRef<number | null>(null);
  const [status, setStatus] = useState<SpeechStatus>("idle");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [isSupported, setIsSupported] = useState(false);
  const [mode, setMode] = useState<RecorderMode>("unsupported");

  const resetRecognitionCycle = useCallback(() => {
    finalTranscriptRef.current = "";
    receivedResultRef.current = false;
    setInterimTranscript("");
  }, []);

  const abortRecognition = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      setStatus("idle");
      return;
    }

    clearRecognitionHandlers(recognition);
    recognition.abort();
    setStatus("idle");
    resetRecognitionCycle();
  }, [resetRecognitionCycle]);

  const cleanupMediaRecorder = useCallback(() => {
    if (autoStopTimerRef.current !== null) {
      window.clearTimeout(autoStopTimerRef.current);
      autoStopTimerRef.current = null;
    }
    mediaRecorderRef.current = null;
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    mediaStreamRef.current = null;
    audioChunksRef.current = [];
  }, []);

  const handleRecognitionError = useCallback(
    (error: string) => {
      setStatus("idle");
      setInterimTranscript("");
      showSpeechError(getToastMessageForError(error, lang));
    },
    [lang],
  );

  const bindRecognitionHandlers = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      return;
    }

    recognition.onstart = () => {
      resetRecognitionCycle();
      setStatus("listening");
    };

    recognition.onresult = (event: SpeechRecognitionEventLike) => {
      let nextInterimTranscript = "";
      let nextFinalTranscript = finalTranscriptRef.current;

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = result[0]?.transcript?.trim() ?? "";
        if (!transcript) {
          continue;
        }

        receivedResultRef.current = true;
        if (result.isFinal) {
          nextFinalTranscript = `${nextFinalTranscript} ${transcript}`.trim();
        } else {
          nextInterimTranscript = `${nextInterimTranscript} ${transcript}`.trim();
        }
      }

      finalTranscriptRef.current = nextFinalTranscript;
      setInterimTranscript(nextInterimTranscript);

      if (nextFinalTranscript) {
        setStatus("processing");
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEventLike) => {
      handleRecognitionError(event.error);
    };

    recognition.onend = () => {
      const finalTranscript = finalTranscriptRef.current.trim();
      const hadAnyResult = receivedResultRef.current;

      setStatus("idle");
      setInterimTranscript("");

      if (finalTranscript) {
        onTranscript(finalTranscript);
        onFocusInput();
      } else if (!hadAnyResult) {
        showSpeechError(getNoSpeechMessage(lang));
      }

      resetRecognitionCycle();
    };
  }, [handleRecognitionError, lang, onFocusInput, onTranscript, resetRecognitionCycle]);

  useEffect(() => {
    const recognitionCtor = getSpeechRecognitionConstructor();
    const hasMediaRecorder =
      typeof window !== "undefined" &&
      typeof window.MediaRecorder !== "undefined" &&
      Boolean(navigator.mediaDevices?.getUserMedia);

    if (recognitionCtor) {
      setMode("speech-recognition");
      setIsSupported(true);
    } else if (hasMediaRecorder) {
      setMode("media-recorder");
      setIsSupported(true);
    } else {
      setMode("unsupported");
      setIsSupported(false);
    }

    if (!recognitionCtor || recognitionRef.current) {
      return;
    }

    const recognition = new recognitionCtor();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = getRecognitionLanguage(lang);
    recognitionRef.current = recognition;
    bindRecognitionHandlers();

    return () => {
      clearRecognitionHandlers(recognitionRef.current);
      recognition.abort();
      recognitionRef.current = null;
    };
  }, [bindRecognitionHandlers, lang]);

  useEffect(() => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      return;
    }

    clearRecognitionHandlers(recognition);
    recognition.abort();
    recognition.lang = getRecognitionLanguage(lang);
    bindRecognitionHandlers();
    setStatus("idle");
    resetRecognitionCycle();

    return () => {
      clearRecognitionHandlers(recognition);
      recognition.abort();
    };
  }, [bindRecognitionHandlers, lang, resetRecognitionCycle]);

  useEffect(() => {
    return () => {
      abortRecognition();
      cleanupMediaRecorder();
    };
  }, [abortRecognition, cleanupMediaRecorder]);

  const requestMicrophonePermission = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("unsupported-media-devices");
    }

    return navigator.mediaDevices.getUserMedia({ audio: true });
  }, []);

  const startListening = useCallback(async () => {
    if (mode !== "speech-recognition" || !isSupported || !recognitionRef.current) {
      showSpeechError(getUnsupportedMessage(lang));
      return;
    }

    try {
      setStatus("processing");
      resetRecognitionCycle();
      recognitionRef.current.lang = getRecognitionLanguage(lang);
      recognitionRef.current.start();
    } catch {
      setStatus("idle");
      showSpeechError(getCaptureMessage(lang));
    }
  }, [isSupported, lang, mode, requestMicrophonePermission, resetRecognitionCycle]);

  const stopListening = useCallback(() => {
    if (mode === "speech-recognition") {
      if (!recognitionRef.current) {
        setStatus("idle");
        return;
      }

      setStatus("processing");
      recognitionRef.current.stop();
      return;
    }

    if (mode === "media-recorder") {
      if (!mediaRecorderRef.current) {
        setStatus("idle");
        return;
      }

      setStatus("processing");
      mediaRecorderRef.current.stop();
      return;
    }

    showSpeechError(getMediaRecorderUnsupportedMessage(lang));
  }, [lang, mode]);

  const startMediaRecorderFlow = useCallback(async () => {
    if (mode !== "media-recorder") {
      showSpeechError(getMediaRecorderUnsupportedMessage(lang));
      return;
    }

    let stream: MediaStream;
    try {
      stream = await requestMicrophonePermission();
    } catch (error) {
      setStatus("idle");
      const permissionError =
        error instanceof DOMException && (error.name === "NotAllowedError" || error.name === "SecurityError");
      showSpeechError(permissionError ? getPermissionDeniedMessage(lang) : getCaptureMessage(lang));
      return;
    }

    try {
      const preferredMimeTypes = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];
      const mimeType = preferredMimeTypes.find((candidate) => MediaRecorder.isTypeSupported(candidate));
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      mediaStreamRef.current = stream;
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onerror = () => {
        cleanupMediaRecorder();
        setStatus("idle");
        showSpeechError(getCaptureMessage(lang));
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        cleanupMediaRecorder();

        if (!audioBlob.size) {
          setStatus("idle");
          showSpeechError(getNoSpeechMessage(lang));
          return;
        }

        setStatus("processing");
        try {
          const result = await api.transcribe(audioBlob, lang);
          setStatus("idle");
          onTranscript(result.text);
          onFocusInput();
        } catch {
          setStatus("idle");
          showSpeechError(getNetworkMessage(lang));
        }
      };

      setStatus("listening");
      recorder.start();
      autoStopTimerRef.current = window.setTimeout(() => {
        if (mediaRecorderRef.current?.state === "recording") {
          setStatus("processing");
          mediaRecorderRef.current.stop();
        }
      }, 5000);
    } catch {
      cleanupMediaRecorder();
      setStatus("idle");
      showSpeechError(getCaptureMessage(lang));
    }
  }, [cleanupMediaRecorder, lang, mode, onFocusInput, onTranscript, requestMicrophonePermission]);

  const toggleListening = useCallback(async () => {
    if (status === "listening") {
      stopListening();
      return;
    }

    if (status === "processing") {
      return;
    }

    if (mode === "media-recorder") {
      await startMediaRecorderFlow();
      return;
    }

    await startListening();
  }, [mode, startListening, startMediaRecorderFlow, status, stopListening]);

  return {
    status,
    interimTranscript,
    isSupported,
    tooltipText: isSupported ? "" : getMediaRecorderUnsupportedMessage(lang),
    toggleListening,
  };
}
