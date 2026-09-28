import { MoonIcon, SunIcon } from "lucide-react";

import { useTheme } from "../../hooks/use-theme";
import { Button } from "./button";

/** A sun/moon button that toggles between light and dark themes. */
function ThemeToggle({ className, ...props }: React.ComponentProps<typeof Button>) {
  const { resolvedTheme, setTheme } = useTheme();
  const isDark = resolvedTheme === "dark";

  return (
    <Button
      data-slot="theme-toggle"
      variant="outline"
      size="icon"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className={className}
      onClick={() => setTheme(isDark ? "light" : "dark")}
      {...props}
    >
      {isDark ? <SunIcon /> : <MoonIcon />}
    </Button>
  );
}

export { ThemeToggle };
