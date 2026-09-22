import { Button } from "../ui/button";
import { Checkbox } from "../ui/checkbox";
import { Field, FieldContent, FieldError, FieldLabel } from "../ui/field";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { LoaderCircleIcon } from "lucide-react";

interface LoginFormProps {
  onSubmit?: (e: React.FormEvent) => void;
  error?: string | null;
  isLoading?: boolean;
  defaultEmail?: string;
  defaultRemember?: boolean;
  fieldErrors?: Record<string, string>;
}

function LoginForm({
  onSubmit,
  error,
  isLoading = false,
  defaultEmail = "",
  defaultRemember = false,
  fieldErrors = {},
}: LoginFormProps) {
  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      {error && (
        <div
          role="alert"
          className="rounded-2xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive"
        >
          {error}
        </div>
      )}

      <Field data-invalid={!!fieldErrors.email || undefined}>
        <FieldLabel>Email</FieldLabel>
        <FieldContent>
          <Input
            type="email"
            placeholder="you@example.com"
            defaultValue={defaultEmail}
            disabled={isLoading}
            required
          />
          {fieldErrors.email && <FieldError>{fieldErrors.email}</FieldError>}
        </FieldContent>
      </Field>

      <Field data-invalid={!!fieldErrors.password || undefined}>
        <FieldLabel>Password</FieldLabel>
        <FieldContent>
          <Input type="password" placeholder="Enter your password" disabled={isLoading} required />
          <FieldError
            errors={fieldErrors.password ? [{ message: fieldErrors.password }] : undefined}
          />
        </FieldContent>
      </Field>

      <div className="flex items-center justify-between">
        <Label className="flex items-center gap-2 text-sm">
          <Checkbox defaultChecked={defaultRemember} disabled={isLoading} />
          Remember me
        </Label>
        <a
          href="#"
          className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
        >
          Forgot password?
        </a>
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading && <LoaderCircleIcon className="size-4 animate-spin" />}
        {isLoading ? "Signing in..." : "Sign in"}
      </Button>
    </form>
  );
}

export { LoginForm };
