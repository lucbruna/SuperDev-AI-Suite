export default function Playhead({ currentTime, pxPerSecond }: { currentTime: number; pxPerSecond: number }) {
  return (
    <div className="pointer-events-none absolute inset-y-0 z-20 w-px bg-red-500" style={{ left: currentTime * pxPerSecond }}>
      <div className="absolute -left-[5px] top-0 h-0 w-0 border-x-[5px] border-t-[6px] border-x-transparent border-t-red-500" />
    </div>
  );
}
