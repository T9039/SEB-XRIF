import type { Meta, StoryObj } from "@storybook/react";
import { AlertTriangleIcon, CheckCircle2Icon, InfoIcon, XIcon } from "lucide-react";
import { Button } from "./button";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "./alert";

const meta = {
  title: "UI/Alert",
  component: Alert,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    variant: { control: "select", options: ["default", "destructive"] },
  },
} satisfies Meta<typeof Alert>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <div className="w-96">
      <Alert {...args}>
        <InfoIcon />
        <AlertTitle>Heads up!</AlertTitle>
        <AlertDescription>You can add components to your app using the CLI.</AlertDescription>
      </Alert>
    </div>
  ),
};

export const Destructive: Story = {
  args: { variant: "destructive" },
  render: (args) => (
    <div className="w-96">
      <Alert {...args}>
        <AlertTriangleIcon />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Your session has expired. Please sign in again to continue.
        </AlertDescription>
      </Alert>
    </div>
  ),
};

export const Success: Story = {
  render: (args) => (
    <div className="w-96">
      <Alert {...args} className="border-primary/30">
        <CheckCircle2Icon />
        <AlertTitle>Saved</AlertTitle>
        <AlertDescription>Your changes have been saved successfully.</AlertDescription>
      </Alert>
    </div>
  ),
};

export const WithAction: Story = {
  render: (args) => (
    <div className="w-96">
      <Alert {...args}>
        <InfoIcon />
        <AlertTitle>Update available</AlertTitle>
        <AlertDescription>A new version of the app is available.</AlertDescription>
        <AlertAction>
          <Button variant="ghost" size="icon-sm" aria-label="Dismiss">
            <XIcon />
          </Button>
        </AlertAction>
      </Alert>
    </div>
  ),
};
