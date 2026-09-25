import { useSource } from "../lib/source-context";
import { LearnerTable } from "./LearnerTable";
import { XrLearnerTable } from "./XrLearnerTable";

/** The Data tab follows the active data source. */
export function DataPanel() {
  const { source } = useSource();
  return source.kind === "xr" ? <XrLearnerTable /> : <LearnerTable />;
}
