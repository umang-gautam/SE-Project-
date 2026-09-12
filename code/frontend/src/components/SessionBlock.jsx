/**
 * Status badge styling helper according to project requirements:
 * pending = blue, done = green, missed = red.
 */
function getStatusBadgeConfig(status) {
  const normalized = (status || 'pending').toLowerCase();
  switch (normalized) {
    case 'done':
      return {
        label: 'Done',
        badgeClass: 'bg-green-100 text-green-800 border-green-300',
        dotClass: 'bg-green-500',
      };
    case 'missed':
      return {
        label: 'Missed',
        badgeClass: 'bg-red-100 text-red-800 border-red-300',
        dotClass: 'bg-red-500',
      };
    case 'pending':
    default:
      return {
        label: 'Pending',
        badgeClass: 'bg-blue-100 text-blue-800 border-blue-300',
        dotClass: 'bg-blue-500',
      };
  }
}

/**
 * SessionBlock — one study session showing topic name, date, duration,
 * status badge, and status toggle buttons (pending/done/missed).
 */
export default function SessionBlock({
  session,
  topicName,
  isUpdating,
  onStatusChange,
}) {
  const badgeConfig = getStatusBadgeConfig(session.status);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 transition-all hover:shadow-md flex flex-col justify-between">
      <div>
        {/* Header: Status badge & Duration */}
        <div className="flex items-center justify-between gap-2 mb-2.5">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeConfig.badgeClass}`}
          >
            <span className={`w-2 h-2 rounded-full ${badgeConfig.dotClass}`} />
            {badgeConfig.label}
          </span>

          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100">
            <svg
              className="w-3.5 h-3.5 text-indigo-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {session.duration_minutes} min
          </span>
        </div>

        {/* Topic Name */}
        <h4 className="text-sm font-bold text-gray-900 mb-1 leading-snug">
          {topicName}
        </h4>

        {/* Date string */}
        <p className="text-xs text-gray-500 flex items-center gap-1 mb-3">
          <svg
            className="w-3.5 h-3.5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          {session.date}
        </p>
      </div>

      {/* Status Toggle Control */}
      <div className="pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between gap-1">
          <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">
            Status:
          </span>
          <div className="inline-flex rounded-lg p-0.5 bg-gray-100 border border-gray-200">
            {['pending', 'done', 'missed'].map((statusOption) => {
              const isActive = session.status === statusOption;
              let activeClasses = '';

              if (isActive) {
                if (statusOption === 'pending') {
                  activeClasses = 'bg-blue-600 text-white shadow-sm';
                } else if (statusOption === 'done') {
                  activeClasses = 'bg-green-600 text-white shadow-sm';
                } else {
                  activeClasses = 'bg-red-600 text-white shadow-sm';
                }
              } else {
                activeClasses =
                  'text-gray-600 hover:text-gray-900 hover:bg-gray-200/70';
              }

              return (
                <button
                  key={statusOption}
                  type="button"
                  disabled={isUpdating}
                  onClick={() => onStatusChange(session.id, statusOption)}
                  className={`px-2 py-1 text-xs font-semibold rounded-md capitalize transition-all ${activeClasses} ${
                    isUpdating
                      ? 'opacity-50 cursor-not-allowed'
                      : 'cursor-pointer'
                  }`}
                  title={`Mark as ${statusOption}`}
                >
                  {statusOption}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
