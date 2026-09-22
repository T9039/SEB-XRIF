import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { LoginForm } from "./login-form";
import { SocialLoginButtons } from "./social-login-buttons";
import { FileIcon } from "lucide-react";

interface LoginPageProps {
  error?: string | null;
  isLoading?: boolean;
  isSocialLoading?: boolean;
  socialProvider?: string | null;
  defaultEmail?: string;
  defaultRemember?: boolean;
  fieldErrors?: Record<string, string>;
}

function LoginPage({
  error,
  isLoading,
  isSocialLoading,
  socialProvider,
  defaultEmail,
  defaultRemember,
  fieldErrors,
}: LoginPageProps) {
  if (isLoading) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-muted/50 p-4">
        <Card className="w-full max-w-sm">
          <CardHeader className="items-center text-center">
            <Skeleton className="mx-auto size-12 rounded-3xl" />
            <Skeleton className="mx-auto mt-2 h-6 w-40" />
            <Skeleton className="mx-auto mt-1 h-4 w-56" />
          </CardHeader>
          <CardContent className="flex flex-col gap-6">
            <div className="flex flex-col gap-4">
              <div className="space-y-2">
                <Skeleton className="h-4 w-12" />
                <Skeleton className="h-10 w-full rounded-xl" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-10 w-full rounded-xl" />
              </div>
              <div className="flex items-center justify-between">
                <Skeleton className="h-5 w-28" />
                <Skeleton className="h-4 w-28" />
              </div>
              <Skeleton className="h-10 w-full rounded-xl" />
            </div>
            <div className="flex flex-col gap-4">
              <Skeleton className="h-px w-full" />
              <Skeleton className="mx-auto h-4 w-28" />
              <div className="flex flex-col gap-1.5">
                <Skeleton className="h-10 w-full rounded-xl" />
                <Skeleton className="h-10 w-full rounded-xl" />
                <Skeleton className="h-10 w-full rounded-xl" />
              </div>
            </div>
          </CardContent>
          <CardFooter className="justify-center">
            <Skeleton className="h-4 w-48" />
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-muted/50 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="items-center text-center">
          <div className="w-full mb-2 flex size-12 items-center justify-center rounded-3xl text-primary">
            <FileIcon className="size-6" />
          </div>
          <CardTitle className="text-xl">Welcome back</CardTitle>
          <CardDescription>Sign in to your account to continue</CardDescription>
        </CardHeader>

        <CardContent className="flex flex-col gap-6">
          <LoginForm
            error={error}
            isLoading={isLoading}
            defaultEmail={defaultEmail}
            defaultRemember={defaultRemember}
            fieldErrors={fieldErrors}
          />

          <SocialLoginButtons isLoading={isSocialLoading} disabledProvider={socialProvider} />
        </CardContent>

        <CardFooter className="justify-center">
          <p className="text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <a href="#" className="font-medium text-foreground underline-offset-4 hover:underline">
              Sign up
            </a>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}

export { LoginPage };
