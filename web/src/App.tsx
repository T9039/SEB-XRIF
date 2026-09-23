import { HealthBadge } from "./components/HealthBadge";
import { ImportancePanel } from "./components/ImportancePanel";
import { ClassificationQuality } from "./components/ClassificationQuality";
import { CvSpread } from "./components/CvSpread";
import { LearnerTable } from "./components/LearnerTable";
import { MetricCards } from "./components/MetricCards";
import { PredictionForm } from "./components/PredictionForm";
import { TierDistribution } from "./components/TierDistribution";
import { TrendChart } from "./components/TrendChart";

export default function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b bg-card">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <div>
            <h1 className="font-heading text-xl font-semibold">SEB-XRIF Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              Scalable, Evidence-Based XR Integration Framework
            </p>
          </div>
          <HealthBadge />
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl grid-cols-1 gap-4 px-6 py-6 lg:grid-cols-2">
        <div className="lg:col-span-2">
          <MetricCards />
        </div>
        <div className="lg:col-span-2">
          <PredictionForm />
        </div>
        <TierDistribution />
        <ImportancePanel />
        <div className="lg:col-span-2">
          <TrendChart />
        </div>
        <div className="lg:col-span-2">
          <LearnerTable />
        </div>
        <div className="lg:col-span-2">
          <ClassificationQuality />
        </div>
        <div className="lg:col-span-2">
          <CvSpread />
        </div>
      </main>

      <footer className="mx-auto max-w-6xl px-6 pb-8 text-center text-xs text-muted-foreground">
        Dashboard built on the SEB-XRIF component library (shadcn/ui + Tailwind v4).
      </footer>
    </div>
  );
}
