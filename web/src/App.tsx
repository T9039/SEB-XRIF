import { Activity, LayoutDashboard, Sparkles, Table2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@humanity-erp/ui";
import { ClassificationQuality } from "./components/ClassificationQuality";
import { CvSpread } from "./components/CvSpread";
import { HealthBadge } from "./components/HealthBadge";
import { ImportancePanel } from "./components/ImportancePanel";
import { LearnerTable } from "./components/LearnerTable";
import { MetricCards } from "./components/MetricCards";
import { PredictionForm } from "./components/PredictionForm";
import { TierDistribution } from "./components/TierDistribution";
import { TrendChart } from "./components/TrendChart";

const NAV = [
  { value: "overview", label: "Overview", icon: LayoutDashboard },
  { value: "predict", label: "Predict", icon: Sparkles },
  { value: "data", label: "Data", icon: Table2 },
  { value: "diagnostics", label: "Diagnostics", icon: Activity },
] as const;

export default function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b bg-card/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <div>
            <h1 className="font-heading text-xl font-semibold">SEB-XRIF Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              Scalable, Evidence-Based XR Integration Framework
            </p>
          </div>
          <HealthBadge />
        </div>
      </header>

      <Tabs
        defaultValue="overview"
        orientation="vertical"
        className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-6 py-6 lg:flex-row"
      >
        <TabsList className="w-full lg:sticky lg:top-24 lg:h-fit lg:w-56 lg:self-start">
          {NAV.map((item) => (
            <TabsTrigger key={item.value} value={item.value} className="gap-2">
              <item.icon />
              <span>{item.label}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="overview" className="min-w-0 flex-1">
          <div className="flex flex-col gap-4">
            <MetricCards />
            <div className="grid gap-4 lg:grid-cols-2">
              <TierDistribution />
              <TrendChart />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="predict" className="min-w-0 flex-1">
          <PredictionForm />
        </TabsContent>

        <TabsContent value="data" className="min-w-0 flex-1">
          <LearnerTable />
        </TabsContent>

        <TabsContent value="diagnostics" className="min-w-0 flex-1">
          <div className="flex flex-col gap-4">
            <ClassificationQuality />
            <div className="grid gap-4 lg:grid-cols-2">
              <CvSpread />
              <ImportancePanel />
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
