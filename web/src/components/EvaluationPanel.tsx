import {
  Alert,
  AlertDescription,
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Skeleton,
} from "@humanity-erp/ui";
import { useEvaluation } from "../api/hooks";

function value(input: number | null | undefined, digits = 2): string {
  return input === null || input === undefined ? "—" : input.toFixed(digits);
}

function Stat({ label, value: shown }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs tracking-wide text-muted-foreground uppercase">{label}</div>
      <div className="font-heading text-lg">{shown}</div>
    </div>
  );
}

/** Longitudinal T0/T1/T2 impact, or an explicit empty state. */
export function EvaluationPanel() {
  const { data, isLoading, isError } = useEvaluation();

  if (isLoading) return <Skeleton className="h-40 w-full" />;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Longitudinal impact</CardTitle>
        <CardDescription>
          The fixed protocol every adopter reports: SUS usability and T0/T1/T2 learning effect
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isError || !data || !data.available ? (
          <Alert>
            <AlertDescription>
              {data?.reason ?? "Evaluation unavailable."} Import a pilot with `make eval-report
              ARGS="--input pilot.json --store --source pilot"`.
            </AlertDescription>
          </Alert>
        ) : (
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <Badge variant="secondary">{data.sources?.join(", ") ?? "unknown source"}</Badge>
              <span className="text-muted-foreground">{data.records ?? 0} measurements</span>
            </div>
            {data.usability ? (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <Stat label="SUS mean" value={value(data.usability.mean)} />
                <Stat label="SUS benchmark" value={value(data.usability.benchmark)} />
                <Stat label="SUS participants" value={String(data.usability.n)} />
                <Stat label="Meets SUS" value={data.usability.meets_benchmark ? "yes" : "no"} />
              </div>
            ) : null}
            {data.learning ? (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <Stat label="Mean T0" value={value(data.learning.mean_t0)} />
                <Stat label="Mean T1" value={value(data.learning.mean_t1)} />
                <Stat label="Immediate gain" value={value(data.learning.gain_immediate)} />
                <Stat label="Cohen's d (T1–T0)" value={value(data.learning.d_immediate, 3)} />
                {data.learning.mean_t2 !== undefined ? (
                  <>
                    <Stat label="Mean T2" value={value(data.learning.mean_t2)} />
                    <Stat label="Delayed gain" value={value(data.learning.gain_delayed)} />
                    <Stat label="Cohen's d (T2–T0)" value={value(data.learning.d_delayed, 3)} />
                    <Stat label="Retention ratio" value={value(data.learning.retention_ratio)} />
                  </>
                ) : null}
              </div>
            ) : null}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
