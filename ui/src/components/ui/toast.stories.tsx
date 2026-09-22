import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";
import { toast, Toaster } from "./toast";

const meta = {
  title: "UI/Toast",
  component: Toaster,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Toaster>;

export default meta;
type Story = StoryObj<typeof meta>;

export const AllTypes: Story = {
  render: (args) => (
    <div className="flex w-96 flex-col gap-2">
      <div className="flex flex-wrap gap-2">
        <Button
          onClick={() =>
            toast.add({ title: "Saved", description: "Your document was saved.", type: "success" })
          }
        >
          Success
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.add({ title: "Info", description: "A new version is available.", type: "info" })
          }
        >
          Info
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.add({
              title: "Warning",
              description: "Your session is about to expire.",
              type: "warning",
            })
          }
        >
          Warning
        </Button>
        <Button
          variant="destructive"
          onClick={() =>
            toast.add({
              title: "Error",
              description: "Something went wrong. Try again.",
              type: "error",
            })
          }
        >
          Error
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.add({ title: "Uploading…", description: "Uploading your file.", type: "loading" })
          }
        >
          Loading
        </Button>
      </div>
      <p className="text-xs text-muted-foreground">
        Click a button to render a toast at the bottom of the page.
      </p>
      <Toaster {...args} />
    </div>
  ),
};

export const WithAction: Story = {
  render: (args) => (
    <div className="flex w-96 flex-col gap-2">
      <Button
        onClick={() =>
          toast.add({
            title: "Undo",
            description: "3 files deleted.",
            type: "info",
            actionProps: {
              children: "Undo",
              onClick: () => toast.close(),
            },
          })
        }
      >
        Delete files
      </Button>
      <p className="text-xs text-muted-foreground">Shows a toast with an inline action button.</p>
      <Toaster {...args} />
    </div>
  ),
};
