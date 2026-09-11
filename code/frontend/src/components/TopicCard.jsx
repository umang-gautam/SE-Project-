/**
 * Returns color tokens and labels based on priority score:
 * - Priority > 70  → Red / Urgent (study this first)
 * - 30 to 70       → Yellow / Moderate
 * - Priority < 30  → Green / Strong
 */
function getPriorityMeta(priority = 0) {
  const score = Number(priority) || 0;
  if (score > 70) {
    return {
      level: 'Urgent',
      badgeClass: 'bg-red-100 text-red-800 border-red-300',
      accentBorder: 'border-l-red-500',
      progressBg: 'bg-red-500',
      textColor: 'text-red-700',
      description: 'Study this first',
    };
  }
  if (score >= 30) {
    return {
      level: 'Moderate',
      badgeClass: 'bg-amber-100 text-amber-800 border-amber-300',
      accentBorder: 'border-l-amber-500',
      progressBg: 'bg-amber-500',
      textColor: 'text-amber-700',
      description: 'Review as scheduled',
    };
  }
  return {
    level: 'Strong',
    badgeClass: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    accentBorder: 'border-l-emerald-500',
    progressBg: 'bg-emerald-500',
    textColor: 'text-emerald-700',
    description: 'Good comprehension',
  };
}

/**
 * TopicCard — one scored topic: rank, subject, priority/mastery/urgency bars.
 */
export default function TopicCard({ topic, rank }) {
  const priority = Number(topic.priority) || 0;
  const masteryPct = Math.round((Number(topic.mastery) || 0) * 100);
  const urgencyPct = Math.round((Number(topic.urgency) || 0) * 100);
  const meta = getPriorityMeta(priority);

  return (
    <div
      className={`bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-200 border-l-4 ${meta.accentBorder} p-5 flex flex-col justify-between`}
    >
      <div>
        {/* Header: Rank + Subject + Priority Badge */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-gray-100 text-gray-600">
              #{rank} Priority
            </span>
            <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
              {topic.subject_name || topic.subject || 'General'}
            </span>
          </div>

          <span
            className={`text-xs font-bold px-2.5 py-1 rounded-full border ${meta.badgeClass} whitespace-nowrap`}
          >
            {meta.level} • {priority.toFixed(1)}
          </span>
        </div>

        {/* Topic Name */}
        <h3 className="text-base font-bold text-gray-900 mb-4 leading-snug line-clamp-2">
          {topic.topic_name || topic.name || 'Untitled Topic'}
        </h3>

        {/* Metrics Grid */}
        <div className="space-y-3 pt-1 border-t border-gray-100">
          {/* Priority Score Bar */}
          <div>
            <div className="flex justify-between text-xs font-medium text-gray-600 mb-1">
              <span>Priority Score</span>
              <span className={`font-bold ${meta.textColor}`}>
                {priority.toFixed(1)} / 100
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 rounded-full ${meta.progressBg} transition-all duration-300`}
                style={{ width: `${Math.min(Math.max(priority, 0), 100)}%` }}
              />
            </div>
          </div>

          {/* Mastery % */}
          <div>
            <div className="flex justify-between text-xs font-medium text-gray-600 mb-1">
              <span>Mastery</span>
              <span className="font-semibold text-gray-900">{masteryPct}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div
                className="h-2 rounded-full bg-blue-600 transition-all duration-300"
                style={{ width: `${Math.min(Math.max(masteryPct, 0), 100)}%` }}
              />
            </div>
          </div>

          {/* Urgency % */}
          <div>
            <div className="flex justify-between text-xs font-medium text-gray-600 mb-1">
              <span>Urgency</span>
              <span className="font-semibold text-gray-900">{urgencyPct}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div
                className="h-2 rounded-full bg-orange-500 transition-all duration-300"
                style={{ width: `${Math.min(Math.max(urgencyPct, 0), 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Footer Note */}
      <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
        <span>Action:</span>
        <span className={`font-medium ${meta.textColor}`}>{meta.description}</span>
      </div>
    </div>
  );
}
