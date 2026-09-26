import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { DATA_SOURCES, DEFAULT_SOURCE_ID, type DataSource } from "./sources";

interface SourceContextValue {
  sourceId: string;
  source: DataSource;
  setSourceId: (id: string) => void;
}

const SourceContext = createContext<SourceContextValue | null>(null);

/** Holds the active data source so every panel stays in sync. */
export function SourceProvider({
  children,
  initial = DEFAULT_SOURCE_ID,
}: {
  children: ReactNode;
  initial?: string;
}) {
  const [sourceId, setSourceId] = useState(initial);
  const value = useMemo(() => {
    const known = DATA_SOURCES.find((source) => source.id === sourceId);
    const source: DataSource = known ?? {
      id: sourceId,
      kind: "generic",
      label: sourceId,
      description: "",
    };
    return { sourceId, source, setSourceId };
  }, [sourceId]);
  return <SourceContext.Provider value={value}>{children}</SourceContext.Provider>;
}

export function useSource(): SourceContextValue {
  const value = useContext(SourceContext);
  if (!value) {
    throw new Error("useSource must be used within a SourceProvider");
  }
  return value;
}
