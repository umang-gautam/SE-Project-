import { Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Subjects from './pages/Subjects'
import PerformanceEntry from './pages/PerformanceEntry'
import StudyPlanView from './pages/StudyPlanView'

/**
 * App shell — navigation bar + page routing.
 *
 * The nav bar is always visible. The <Routes> block swaps
 * the page content based on the current URL path.
 */
export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-indigo-600 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-6">
          <Link to="/" className="text-xl font-bold tracking-tight">
            Workload Balancer
          </Link>
          <div className="flex gap-4 text-sm font-medium">
            <Link to="/" className="hover:text-indigo-200">Dashboard</Link>
            <Link to="/subjects" className="hover:text-indigo-200">Subjects</Link>
            <Link to="/performance" className="hover:text-indigo-200">Scores</Link>
            <Link to="/study-plan" className="hover:text-indigo-200">Study Plan</Link>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/subjects" element={<Subjects />} />
          <Route path="/performance" element={<PerformanceEntry />} />
          <Route path="/study-plan" element={<StudyPlanView />} />
        </Routes>
      </main>
    </div>
  )
}
