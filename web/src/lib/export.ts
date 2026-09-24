/** Export helpers for the Chart Studio. */

/** Serialise rows to CSV, unioning keys and escaping values. */
export function toCsv(rows: Record<string, unknown>[]): string {
  if (rows.length === 0) return "";
  const headers = [...new Set(rows.flatMap((row) => Object.keys(row)))];
  const escape = (value: unknown) => {
    const text = value === null || value === undefined ? "" : String(value);
    return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  };
  return [
    headers.join(","),
    ...rows.map((row) => headers.map((header) => escape(row[header])).join(",")),
  ].join("\n");
}

export function download(filename: string, content: string, mime: string): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function downloadCsv(filename: string, rows: Record<string, unknown>[]): void {
  download(filename, toCsv(rows), "text/csv");
}

export function downloadJson(filename: string, data: unknown): void {
  download(filename, JSON.stringify(data, null, 2), "application/json");
}

export function downloadSvg(filename: string, svg: SVGSVGElement): void {
  download(filename, new XMLSerializer().serializeToString(svg), "image/svg+xml");
}

/** Rasterise an SVG chart to a PNG download. */
export async function downloadPng(filename: string, svg: SVGSVGElement): Promise<void> {
  const source = new XMLSerializer().serializeToString(svg);
  const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const image = new Image();
  await new Promise<void>((resolve, reject) => {
    image.onload = () => resolve();
    image.onerror = () => reject(new Error("Could not rasterise the chart"));
    image.src = url;
  });
  const rect = svg.getBoundingClientRect();
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, rect.width * 2);
  canvas.height = Math.max(1, rect.height * 2);
  const context = canvas.getContext("2d");
  if (context) {
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
  }
  URL.revokeObjectURL(url);
  await new Promise<void>((resolve) => {
    canvas.toBlob((result) => {
      if (result) {
        const link = document.createElement("a");
        link.href = URL.createObjectURL(result);
        link.download = filename;
        link.click();
        URL.revokeObjectURL(link.href);
      }
      resolve();
    }, "image/png");
  });
}
