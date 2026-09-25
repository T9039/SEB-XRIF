import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@humanity-erp/ui";
import { FEATURE_MAPPING } from "../lib/sources";

/** Shows how the LMS feature set maps onto XR behaviour. */
export function XrMappingPanel() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>LMS to XR feature mapping</CardTitle>
        <CardDescription>
          How the same analytics transfers to XR by swapping the feature set
        </CardDescription>
      </CardHeader>
      <CardContent>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-muted-foreground">
              <th className="py-2 pr-4 font-medium">Kalboard (LMS)</th>
              <th className="py-2 pr-4 font-medium">XR analogue</th>
              <th className="py-2 font-medium">ARETE verbs</th>
            </tr>
          </thead>
          <tbody>
            {FEATURE_MAPPING.map((row) => (
              <tr key={row.lms} className="border-t">
                <td className="py-2 pr-4 font-mono text-xs">{row.lms}</td>
                <td className="py-2 pr-4">{row.xr}</td>
                <td className="py-2 text-muted-foreground">{row.verbs.join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
