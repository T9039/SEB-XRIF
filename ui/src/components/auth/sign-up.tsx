import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { SignUpForm } from "./sign-up-form";
import { SocialLoginButtons } from "./social-login-buttons";
import { FileIcon } from "lucide-react";

interface SignUpPageProps {
  error?: string | null;
  isLoading?: boolean;
  isSocialLoading?: boolean;
  socialProvider?: string | null;
  defaultName?: string;
  defaultEmail?: string;
  fieldErrors?: Record<string, string>;
}

function SignUpPage({
  error,
  isLoading,
  isSocialLoading,
  socialProvider,
  defaultName,
  defaultEmail,
  fieldErrors,
}: SignUpPageProps) {
  if (isLoading) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-muted/50 p-4">
        <Card className="w-full max-w-sm">
          <CardHeader className="items-center text-center">
            <Skeleton className="mx-auto size-12 rounded-3xl" />
            <Skeleton className="mx-auto mt-2 h-6 w-44" />
            <Skeleton className="mx-auto mt-1 h-4 w-52" />
          </CardHeader>
          <CardContent className="flex flex-col gap-6">
            <div className="flex flex-col gap-4">
              <div className="space-y-2">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-10 w-full rounded-xl" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-12" />
                <Skeleton className="h-10 w-full rounded-xl" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-10 w-full rounded-xl" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-28" />
                <Skeleton className="h-10 w-full rounded-xl" />
              </div>
              <Skeleton className="h-5 w-full" />
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
            <Skeleton className="h-4 w-44" />
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
          <CardTitle className="text-xl">Create an account</CardTitle>
          <CardDescription>Enter your details to get started</CardDescription>
        </CardHeader>

        <CardContent className="flex flex-col gap-6">
          <SignUpForm
            error={error}
            isLoading={isLoading}
            defaultName={defaultName}
            defaultEmail={defaultEmail}
            fieldErrors={fieldErrors}
          />

          <SocialLoginButtons isLoading={isSocialLoading} disabledProvider={socialProvider} />
        </CardContent>

        <CardFooter className="justify-center">
          <p className="text-sm text-muted-foreground">
            Already have an account?{" "}
            <a href="#" className="font-medium text-foreground underline-offset-4 hover:underline">
              Sign in
            </a>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}

export { SignUpPage };
