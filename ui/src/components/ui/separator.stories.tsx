import type { Meta, StoryObj } from "@storybook/react";
import { Separator } from "./separator";

const meta = {
  title: "UI/Separator",
  component: Separator,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    orientation: { control: "select", options: ["horizontal", "vertical"] },
  },
  args: { orientation: "horizontal" },
} satisfies Meta<typeof Separator>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Horizontal: Story = {
  args: { orientation: "horizontal", className: "w-64" },
};

export const Vertical: Story = {
  args: { orientation: "vertical", className: "h-16" },
};

export const WithText: Story = {
  render: (args) => (
    <div className="w-80">
      <p className="text-sm text-muted-foreground">Content above the separator.</p>
      <Separator className="my-4" {...args} />
      <p className="text-sm text-muted-foreground">Content below the separator.</p>
    </div>
  ),
};
