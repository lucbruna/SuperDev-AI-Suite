import type { StreamingChunk } from "./types";

/** Callback types for the stream processor. */
type ChunkCallback = (chunk: StreamingChunk) => void;
type CompleteCallback = (usage: Record<string, number>) => void;
type ErrorCallback = (error: Error) => void;

/**
 * Processes streaming chunks from the SuperDev API.
 *
 * @example
 * ```ts
 * const processor = new StreamProcessor();
 * processor
 *   .onChunk((chunk) => process.stdout.write(chunk.delta))
 *   .onComplete((usage) => console.log("\nTokens:", usage));
 *
 * for await (const chunk of client.chat.stream("Tell me a story")) {
 *   processor.process(chunk);
 * }
 * ```
 */
export class StreamProcessor {
  private onChunkCb: ChunkCallback | null = null;
  private onCompleteCb: CompleteCallback | null = null;
  private onErrorCb: ErrorCallback | null = null;
  private buffer: string[] = [];
  private usage: Record<string, number> = {};

  /** Register a callback for each incoming chunk. */
  onChunk(callback: ChunkCallback): this {
    this.onChunkCb = callback;
    return this;
  }

  /** Register a callback invoked when the stream completes. */
  onComplete(callback: CompleteCallback): this {
    this.onCompleteCb = callback;
    return this;
  }

  /** Register a callback for stream errors. */
  onError(callback: ErrorCallback): this {
    this.onErrorCb = callback;
    return this;
  }

  /** Process a single streaming chunk. */
  process(chunk: StreamingChunk): void {
    if (chunk.delta) {
      this.buffer.push(chunk.delta);
    }
    if (chunk.usage && Object.keys(chunk.usage).length > 0) {
      this.usage = { ...this.usage, ...chunk.usage };
    }
    if (this.onChunkCb) {
      this.onChunkCb(chunk);
    }
    if (chunk.finishReason && this.onCompleteCb) {
      this.onCompleteCb(this.usage);
    }
  }

  /** Process a stream error. */
  processError(error: Error): void {
    if (this.onErrorCb) {
      this.onErrorCb(error);
    }
  }

  /** The fully reassembled text from all processed chunks. */
  get fullText(): string {
    return this.buffer.join("");
  }

  /** The accumulated token usage. */
  get totalUsage(): Record<string, number> {
    return { ...this.usage };
  }

  /** Reset internal state. */
  reset(): void {
    this.buffer = [];
    this.usage = {};
  }
}

/**
 * Buffers streaming output for reassembly with a max size cap.
 */
export class StreamBuffer {
  private chunks: string[] = [];
  private totalChars = 0;
  private readonly maxSize: number;

  constructor(maxSize = 10_000) {
    this.maxSize = maxSize;
  }

  /** Append a delta string to the buffer. */
  add(delta: string): void {
    if (this.totalChars + delta.length > this.maxSize) {
      const overflow = this.totalChars + delta.length - this.maxSize;
      const removed = this.chunks.shift();
      if (removed) {
        this.totalChars -= removed.length;
      }
      this.totalChars = Math.max(0, this.totalChars - overflow);
    }
    this.chunks.push(delta);
    this.totalChars += delta.length;
  }

  /** Get the full buffered text. */
  getText(): string {
    return this.chunks.join("");
  }

  /** Clear the buffer. */
  clear(): void {
    this.chunks = [];
    this.totalChars = 0;
  }

  /** Current buffer size in characters. */
  get size(): number {
    return this.totalChars;
  }
}
