'use client';

/**
 * Placeholder when a chart has no data to display.
 * Keeps layout consistent and avoids Recharts errors on empty data.
 */
export function ChartEmptyState({
  message = 'No data',
  className = '',
}: {
  message?: string;
  className?: string;
}) {
  return (
    <div
      className={`flex items-center justify-center h-full min-h-[120px] text-gray-500 text-sm ${className}`}
      role="img"
      aria-label={message}
    >
      <span className="border border-dashed border-white/20 rounded-lg px-4 py-3">
        {message}
      </span>
    </div>
  );
}
