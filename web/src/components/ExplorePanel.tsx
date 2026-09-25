import { useState } from "react";
import type { ReactNode } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Label,
  NativeSelect,
  NativeSelectOption,
} from "@humanity-erp/ui";
import { useCorrelation, useEmbedding, useLearners, usePdp } from "../api/hooks";
import { ChartRenderer } from "../charts/ChartRenderer";
import { BoxPlot } from "../charts/BoxPlot";
import { EmbeddingScatter } from "../charts/EmbeddingScatter";
import { Heatmap } from "../charts/Heatmap";
import { ParallelCoordinates } from "../charts/ParallelCoordinates";
import type { Row } from "../charts/data";
import { PanelMessage, PanelSkeleton } from "./panel-states";
import { XrTrendsPanel } from "./XrTrendsPanel";

const BEHAVIOURS = ["raisedhands", "VisITedResources", "AnnouncementsView", "Discussion"];

function Panel({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function CorrelationPanel() {
  const { data, isLoading, isError } = useCorrelation();
  if (isLoading) return <PanelSkeleton title="Correlation matrix" />;
  if (isError || !data) {
    return <PanelMessage title="Correlation matrix" message="Unavailable." />;
  }
  return (
    <Panel title="Correlation matrix" description="Pearson correlation of behavioural predictors">
      <Heatmap
        spec={{
          type: "heatmap",
          rows: [],
          series: [],
          extra: { matrix: data.matrix, rowLabels: data.columns, colLabels: data.columns },
        }}
      />
    </Panel>
  );
}

function BoxPanel() {
  const { data, isLoading, isError } = useLearners({ limit: 1000, offset: 0 });
  const [metric, setMetric] = useState("raisedhands");
  if (isLoading) return <PanelSkeleton title="Distribution by tier" />;
  if (isError || !data) {
    return <PanelMessage title="Distribution by tier" message="Unavailable." />;
  }
  return (
    <Panel
      title="Distribution by tier"
      description="Box-and-whisker of a behavioural metric across performance tiers"
    >
      <div className="mb-3 flex flex-col gap-1">
        <Label htmlFor="box-metric">Metric</Label>
        <NativeSelect
          id="box-metric"
          value={metric}
          onChange={(event) => setMetric(event.target.value)}
        >
          {BEHAVIOURS.map((option) => (
            <NativeSelectOption key={option} value={option}>
              {option}
            </NativeSelectOption>
          ))}
        </NativeSelect>
      </div>
      <BoxPlot spec={{ type: "box", rows: data.rows as Row[], series: [metric], xKey: "Class" }} />
    </Panel>
  );
}

function ParallelPanel() {
  const { data, isLoading, isError } = useLearners({ limit: 1000, offset: 0 });
  if (isLoading) return <PanelSkeleton title="Parallel coordinates" />;
  if (isError || !data) {
    return <PanelMessage title="Parallel coordinates" message="Unavailable." />;
  }
  return (
    <Panel
      title="Parallel coordinates"
      description="Every learner across the behavioural predictors, coloured by tier"
    >
      <ParallelCoordinates
        spec={{
          type: "parallel",
          rows: data.rows as Row[],
          series: BEHAVIOURS,
          extra: { axes: BEHAVIOURS, colorKey: "Class" },
        }}
      />
    </Panel>
  );
}

function EmbeddingPanel() {
  const { data, isLoading, isError } = useEmbedding(3);
  if (isLoading) return <PanelSkeleton title="Learner embedding" />;
  if (isError || !data) {
    return <PanelMessage title="Learner embedding" message="Unavailable." />;
  }
  return (
    <Panel
      title="Learner embedding (PCA)"
      description={`PC1+PC2 explain ${(data.explained_variance.reduce((a, b) => a + b, 0) * 100).toFixed(0)}% of variance`}
    >
      <EmbeddingScatter points={data.points} tiers={["L", "M", "H"]} />
    </Panel>
  );
}

function ClusterPanel() {
  const { data, isLoading, isError } = useEmbedding(3);
  if (isLoading) return <PanelSkeleton title="Cluster profiles" />;
  if (isError || !data) {
    return <PanelMessage title="Cluster profiles" message="Unavailable." />;
  }
  return (
    <Panel title="Cluster profiles" description="Mean behaviour per KMeans cluster">
      <ChartRenderer
        spec={{ type: "radar", rows: data.profiles as Row[], series: data.clusters, xKey: "x" }}
        className="h-72 w-full"
      />
    </Panel>
  );
}

function PdpPanel() {
  const [feature, setFeature] = useState("raisedhands");
  const { data, isLoading, isError } = usePdp(feature);
  return (
    <Panel
      title="Partial dependence"
      description="How the predicted class probability moves as a feature changes"
    >
      <div className="mb-3 flex flex-col gap-1">
        <Label htmlFor="pdp-feature">Feature</Label>
        <NativeSelect
          id="pdp-feature"
          value={feature}
          onChange={(event) => setFeature(event.target.value)}
        >
          {BEHAVIOURS.map((option) => (
            <NativeSelectOption key={option} value={option}>
              {option}
            </NativeSelectOption>
          ))}
        </NativeSelect>
      </div>
      {isLoading ? (
        <p className="py-12 text-center text-sm text-muted-foreground">Loading…</p>
      ) : isError || !data ? (
        <PanelMessage title="" message="Train a model to compute partial dependence." />
      ) : (
        <ChartRenderer
          spec={{
            type: "line",
            rows: data.rows as Row[],
            series: data.classes,
            xKey: "x",
            curve: "linear",
          }}
          className="h-56 w-full"
        />
      )}
    </Panel>
  );
}

export function ExplorePanel() {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <XrTrendsPanel />
      <CorrelationPanel />
      <BoxPanel />
      <ParallelPanel />
      <EmbeddingPanel />
      <ClusterPanel />
      <PdpPanel />
    </div>
  );
}
