import { Button } from "../ui/button";
import { Checkbox } from "../ui/checkbox";
import { Field, FieldContent, FieldError, FieldLabel } from "../ui/field";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { LoaderCircleIcon } from "lucide-react";

interface SignUpFormProps {
  onSubmit?: (e: React.FormEvent) => void;
  error?: string | null;
  isLoading?: boolean;
  defaultName?: string;
  defaultEmail?: string;
  fieldErrors?: Record<string, string>;
}

function SignUpForm({
  onSubmit,
  error,
  isLoading = false,
  defaultName = "",
  defaultEmail = "",
  fieldErrors = {},
}: SignUpFormProps) {
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

      <Field data-invalid={!!fieldErrors.name || undefined}>
        <FieldLabel>Full name</FieldLabel>
        <FieldContent>
          <Input
            type="text"
            placeholder="John Doe"
            defaultValue={defaultName}
            disabled={isLoading}
            required
          />
          {fieldErrors.name && <FieldError>{fieldErrors.name}</FieldError>}
        </FieldContent>
      </Field>

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
          <Input type="password" placeholder="Create a password" disabled={isLoading} required />
          <FieldError
            errors={fieldErrors.password ? [{ message: fieldErrors.password }] : undefined}
          />
        </FieldContent>
      </Field>

      <Field data-invalid={!!fieldErrors.confirmPassword || undefined}>
        <FieldLabel>Confirm password</FieldLabel>
        <FieldContent>
          <Input
            type="password"
            placeholder="Confirm your password"
            disabled={isLoading}
            required
          />
          <FieldError
            errors={
              fieldErrors.confirmPassword ? [{ message: fieldErrors.confirmPassword }] : undefined
            }
          />
        </FieldContent>
      </Field>

      <Label className="flex items-center gap-2 text-sm">
        <Checkbox disabled={isLoading} required />
        <span>
          I agree to the{" "}
          <Button variant="link" className="m-0 p-0 border-none">
            Terms of Service
          </Button>{" "}
          and{" "}
          <Button variant="link" className="m-0 p-0 border-none">
            Privacy Policy
          </Button>
        </span>
      </Label>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading && <LoaderCircleIcon className="size-4 animate-spin" />}
        {isLoading ? "Creating account..." : "Create account"}
      </Button>
    </form>
  );
}

export { SignUpForm };
