import type { Meta, StoryObj } from "@storybook/react";
import { Spinner } from "./spinner";

const meta = {
  title: "UI/Spinner",
  component: Spinner,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  args: { className: "size-4" },
} satisfies Meta<typeof Spinner>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Large: Story = {
  args: { className: "size-8" },
};

export const WithText: Story = {
  render: (args) => (
    <span className="flex items-center gap-2 text-sm text-muted-foreground">
      <Spinner {...args} />
      Loading…
    </span>
  ),
};
