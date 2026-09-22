import { HealthBadge } from "./components/HealthBadge";
import { ImportancePanel } from "./components/ImportancePanel";
import { MetricCards } from "./components/MetricCards";
import { TierDistribution } from "./components/TierDistribution";
import { TrendChart } from "./components/TrendChart";

/**
 * Placeholder dashboard shell.
 *
 * The production UI kit replaces the markup and CSS here. All data access is
 * owned by the hooks in src/api, so swapping presentation never touches data
 * logic.
 */
export default function App() {
  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>SEB-XRIF Dashboard</h1>
          <p className="muted">
            Scalable, Evidence-Based XR Integration Framework
          </p>
        </div>
        <HealthBadge />
      </header>

      <main className="grid">
        <section className="span-2">
          <MetricCards />
        </section>
        <section>
          <TierDistribution />
        </section>
        <section>
          <ImportancePanel />
        </section>
        <section className="span-2">
          <TrendChart />
        </section>
      </main>

      <footer className="footer">
        Placeholder UI — replace with the production design system.
      </footer>
    </div>
  );
}
