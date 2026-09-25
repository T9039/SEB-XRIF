import {
  Activity,
  BarChart3,
  Compass,
  Database,
  LayoutDashboard,
  Sparkles,
  Table2,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@humanity-erp/ui";
import { ChartStudio } from "./components/ChartStudio";
import { ClassificationQuality } from "./components/ClassificationQuality";
import { CvSpread } from "./components/CvSpread";
import { DataPanel } from "./components/DataPanel";
import { DatasetManager } from "./components/DatasetManager";
import { ExplorePanel } from "./components/ExplorePanel";
import { HealthBadge } from "./components/HealthBadge";
import { ImportancePanel } from "./components/ImportancePanel";
import { ModelDiagnostics } from "./components/ModelDiagnostics";
import { ModelResultsTable } from "./components/ModelResultsTable";
import { OverviewPanel } from "./components/OverviewPanel";
import { PredictionForm } from "./components/PredictionForm";
import { SourceGate } from "./components/SourceGate";
import { SourceSelector } from "./components/SourceSelector";
import { SourceProvider } from "./lib/source-context";

const NAV = [
  { value: "overview", label: "Overview", icon: LayoutDashboard },
  { value: "predict", label: "Predict", icon: Sparkles },
  { value: "data", label: "Data", icon: Table2 },
  { value: "diagnostics", label: "Diagnostics", icon: Activity },
  { value: "explore", label: "Explore", icon: Compass },
  { value: "studio", label: "Studio", icon: BarChart3 },
  { value: "datasets", label: "Datasets", icon: Database },
] as const;

export default function App() {
  return (
    <SourceProvider>
      <div className="min-h-screen bg-background text-foreground">
        <header className="sticky top-0 z-10 border-b bg-card/80 backdrop-blur">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
            <div>
              <h1 className="font-heading text-xl font-semibold">SEB-XRIF Dashboard</h1>
              <p className="text-sm text-muted-foreground">
                Scalable, Evidence-Based XR Integration Framework
              </p>
            </div>
            <div className="flex flex-wrap items-end gap-4">
              <SourceSelector />
              <HealthBadge />
            </div>
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
            <OverviewPanel />
          </TabsContent>

          <TabsContent value="predict" className="min-w-0 flex-1">
            <SourceGate surface="Prediction">
              <PredictionForm />
            </SourceGate>
          </TabsContent>

          <TabsContent value="data" className="min-w-0 flex-1">
            <DataPanel />
          </TabsContent>

          <TabsContent value="diagnostics" className="min-w-0 flex-1">
            <SourceGate surface="Diagnostics">
              <div className="flex flex-col gap-4">
                <ModelResultsTable />
                <ClassificationQuality />
                <ModelDiagnostics />
                <div className="grid gap-4 lg:grid-cols-2">
                  <CvSpread />
                  <ImportancePanel />
                </div>
              </div>
            </SourceGate>
          </TabsContent>

          <TabsContent value="explore" className="min-w-0 flex-1">
            <ExplorePanel />
          </TabsContent>

          <TabsContent value="studio" className="min-w-0 flex-1">
            <SourceGate surface="Chart Studio">
              <ChartStudio />
            </SourceGate>
          </TabsContent>

          <TabsContent value="datasets" className="min-w-0 flex-1">
            <DatasetManager />
          </TabsContent>
        </Tabs>
      </div>
    </SourceProvider>
  );
}
