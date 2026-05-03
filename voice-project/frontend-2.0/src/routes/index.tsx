import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "Voxa — Voice Transcription, Reimagined" },
      { name: "description", content: "Real-time voice transcription with a beautiful, focused interface. Speak. Watch words bloom." },
    ],
    links: [
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" },
    ],
  }),
});

type Line = { id: number; text: string; ts: string };

function Index() {
  const [recording, setRecording] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [lines, setLines] = useState<Line[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [level, setLevel] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const rafRef = useRef<number | null>(null);
  const startedAtRef = useRef<number>(0);
  const tickRef = useRef<number | null>(null);
  const idRef = useRef(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [lines]);

  useEffect(() => () => cleanup(), []);

  function cleanup() {
    try { mediaRecorderRef.current?.state !== "inactive" && mediaRecorderRef.current?.stop(); } catch {}
    try { socketRef.current?.close(); } catch {}
    streamRef.current?.getTracks().forEach((t) => t.stop());
    audioCtxRef.current?.close().catch(() => {});
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    if (tickRef.current) window.clearInterval(tickRef.current);
  }

  async function startRecording() {
    setError(null);
    setLines([]);
    setConnecting(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Audio level meter
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const ctx = new AudioCtx();
      audioCtxRef.current = ctx;
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteTimeDomainData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
          const v = (data[i] - 128) / 128;
          sum += v * v;
        }
        setLevel(Math.min(1, Math.sqrt(sum / data.length) * 2.4));
        rafRef.current = requestAnimationFrame(tick);
      };
      tick();

      const socket = new WebSocket("ws://localhost:8001/ws");
      socketRef.current = socket;

      socket.onopen = () => {
        setConnecting(false);
        setRecording(true);
        startedAtRef.current = Date.now();
        tickRef.current = window.setInterval(() => {
          setElapsed(Math.floor((Date.now() - startedAtRef.current) / 1000));
        }, 250);

        const mr = new MediaRecorder(stream);
        mediaRecorderRef.current = mr;
        mr.ondataavailable = (event) => {
          if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
            socket.send(event.data);
          }
        };
        mr.start(4000);
      };

      socket.onmessage = (event) => {
        const text = typeof event.data === "string" ? event.data : "";
        if (!text) return;
        const ts = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
        setLines((prev) => [...prev, { id: ++idRef.current, text, ts }]);
      };

      socket.onerror = () => {
        setError("Connection error. Make sure your transcription server is running on ws://localhost:8001/ws");
        setConnecting(false);
      };

      socket.onclose = () => {
        setRecording(false);
        setConnecting(false);
      };
    } catch (e) {
      setError(e instanceof Error ? e.message : "Microphone access denied.");
      setConnecting(false);
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send("STOP");
    }
    streamRef.current?.getTracks().forEach((t) => t.stop());
    audioCtxRef.current?.close().catch(() => {});
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    if (tickRef.current) window.clearInterval(tickRef.current);
    setRecording(false);
    setLevel(0);
  }

  const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const ss = String(elapsed % 60).padStart(2, "0");

  return (
    <main className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="px-8 py-6 flex items-center justify-between max-w-6xl mx-auto w-full">
        <div className="flex items-center gap-2.5">
          <div className="h-7 w-7 rounded-full bg-gradient-to-br from-primary to-accent shadow-[0_0_20px_var(--color-glow)]" />
          <span className="font-display text-2xl tracking-tight">Voxa</span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
          <span className={`h-1.5 w-1.5 rounded-full ${recording ? "bg-primary animate-pulse" : connecting ? "bg-accent animate-pulse" : "bg-muted-foreground/40"}`} />
          {recording ? "LIVE" : connecting ? "CONNECTING" : "IDLE"}
        </div>
      </header>

      {/* Hero / Recorder */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 pt-4 pb-16 max-w-3xl mx-auto w-full">
        <div className="text-center mb-12 animate-[fade-in_0.6s_ease-out]">
          <h1 className="font-display text-6xl md:text-7xl leading-[0.95] tracking-tight">
            Speak it.
            <br />
            <em className="text-primary">See it bloom.</em>
          </h1>
          <p className="mt-5 text-muted-foreground max-w-md mx-auto text-[15px] leading-relaxed">
            A quiet, focused space for your voice. Real-time transcription, beautifully rendered.
          </p>
        </div>

        {/* Mic Orb */}
        <div className="relative flex items-center justify-center mb-10">
          {recording && (
            <>
              <span className="absolute inset-0 rounded-full bg-primary/30 animate-pulse-ring" />
              <span className="absolute inset-0 rounded-full bg-accent/20 animate-pulse-ring" style={{ animationDelay: "0.8s" }} />
            </>
          )}
          <button
            onClick={recording ? stopRecording : startRecording}
            disabled={connecting}
            aria-label={recording ? "Stop recording" : "Start recording"}
            className="relative h-32 w-32 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center transition-all duration-300 hover:scale-105 active:scale-95 disabled:opacity-60 disabled:cursor-wait shadow-[0_0_60px_-10px_var(--color-glow),0_20px_50px_-15px_rgba(0,0,0,0.6)]"
            style={{
              transform: recording ? `scale(${1 + level * 0.12})` : undefined,
            }}
          >
            <svg viewBox="0 0 24 24" fill="none" className="h-12 w-12 text-primary-foreground" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {recording ? (
                <rect x="7" y="7" width="10" height="10" rx="1.5" fill="currentColor" />
              ) : (
                <>
                  <rect x="9" y="3" width="6" height="12" rx="3" fill="currentColor" />
                  <path d="M5 11a7 7 0 0 0 14 0" />
                  <path d="M12 18v3" />
                </>
              )}
            </svg>
          </button>
        </div>

        {/* Level meter + timer */}
        <div className="flex items-center gap-6 font-mono text-xs text-muted-foreground tabular-nums">
          <span className={recording ? "text-primary" : ""}>{mm}:{ss}</span>
          <div className="flex items-end gap-[3px] h-5">
            {Array.from({ length: 18 }).map((_, i) => {
              const peak = recording ? Math.max(0.15, Math.min(1, level * (1 + Math.sin(i * 0.7 + Date.now() / 200) * 0.4))) : 0.12;
              return (
                <span
                  key={i}
                  className="w-[3px] rounded-full bg-gradient-to-t from-accent to-primary transition-all duration-100"
                  style={{ height: `${peak * 100}%`, opacity: recording ? 0.6 + peak * 0.4 : 0.25 }}
                />
              );
            })}
          </div>
          <span>{recording ? "LISTENING" : "READY"}</span>
        </div>

        {error && (
          <div className="mt-8 max-w-md text-center text-sm text-destructive bg-destructive/10 border border-destructive/30 rounded-xl px-4 py-3 animate-[fade-in_0.3s_ease-out]">
            {error}
          </div>
        )}
      </section>

      {/* Transcript */}
      <section className="px-6 pb-16 max-w-3xl mx-auto w-full">
        <div className="flex items-baseline justify-between mb-3 px-1">
          <h2 className="font-display text-2xl">Transcript</h2>
          <span className="font-mono text-[11px] text-muted-foreground uppercase tracking-wider">
            {lines.length} {lines.length === 1 ? "entry" : "entries"}
          </span>
        </div>
        <div
          ref={scrollRef}
          className="relative bg-card/60 backdrop-blur-xl border border-border rounded-2xl p-6 md:p-8 min-h-[280px] max-h-[420px] overflow-y-auto shadow-[0_30px_80px_-30px_rgba(0,0,0,0.5)]"
        >
          {lines.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-muted-foreground/70 text-sm font-mono">
                {recording ? "Listening for words…" : "Press the orb to begin."}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {lines.map((line) => (
                <div key={line.id} className="flex gap-4 animate-[slide-up_0.5s_cubic-bezier(0.16,1,0.3,1)]">
                  <span className="font-mono text-[10px] text-muted-foreground/60 pt-1.5 tabular-nums shrink-0 w-16">
                    {line.ts}
                  </span>
                  <p className="font-display text-xl leading-snug text-foreground flex-1">
                    {line.text}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
        <p className="mt-4 text-center text-[11px] font-mono text-muted-foreground/60 uppercase tracking-wider">
          Connects to ws://localhost:8001/ws
        </p>
      </section>
    </main>
  );
}
