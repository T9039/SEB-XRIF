import type { Meta, StoryObj } from "@storybook/react";
import { Label } from "./label";

const meta = {
  title: "UI/Label",
  component: Label,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  args: { children: "Email address" },
} satisfies Meta<typeof Label>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Required: Story = {
  render: (args) => (
    <Label {...args}>
      <span>Email address</span>
      <span className="text-destructive" aria-hidden="true">
        *
      </span>
    </Label>
  ),
};

export const WithInput: Story = {
  render: (args) => (
    <div className="flex flex-col gap-2">
      <Label htmlFor="label-input" {...args} />
      <input
        id="label-input"
        className="h-9 w-64 rounded-3xl border border-transparent bg-input/50 px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30"
        placeholder="you@example.com"
      />
    </div>
  ),
};
