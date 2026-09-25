import type { ReactNode } from "react";
import {
  Alert,
  AlertDescription,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@humanity-erp/ui";
import { useSource } from "../lib/source-context";

/** Renders children only for the LMS source; otherwise explains why not. */
export function SourceGate({ children, surface }: { children: ReactNode; surface: string }) {
  const { source } = useSource();
  if (source.kind !== "xr") return <>{children}</>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{surface} uses the LMS model</CardTitle>
      </CardHeader>
      <CardContent>
        <Alert>
          <AlertDescription>
            This surface is built on the Kalboard LMS model. Switch the data source to “Kalboard 360
            (LMS, non-XR)” in the header to use it, or open Explore for the XR engagement and risk
            panels.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
}
