/**
 * ScoreBadge — shared badge component displaying a score with color-coding:
 *   >= 80: green
 *   50-79: yellow
 *   < 50:  red
 */
export default function ScoreBadge({ score }) {
  let colorClasses = 'bg-red-100 text-red-800 border-red-200';

  if (score >= 80) {
    colorClasses = 'bg-green-100 text-green-800 border-green-200';
  } else if (score >= 50) {
    colorClasses = 'bg-yellow-100 text-yellow-800 border-yellow-200';
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colorClasses}`}
    >
      {score}%
    </span>
  );
}
