import type { Meta, StoryObj } from "@storybook/react";
import { Label } from "./label";
import { Checkbox } from "./checkbox";

const meta = {
  title: "UI/Checkbox",
  component: Checkbox,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  render: (args) => (
    <div className="flex items-center gap-2">
      <Checkbox id="checkbox" {...args} />
      <Label htmlFor="checkbox">Accept terms and conditions</Label>
    </div>
  ),
} satisfies Meta<typeof Checkbox>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Checked: Story = {
  args: { defaultChecked: true },
};

export const Indeterminate: Story = {
  args: { indeterminate: true, "aria-label": "Indeterminate" },
};

export const Disabled: Story = {
  args: { disabled: true },
};

export const DisabledChecked: Story = {
  args: { disabled: true, defaultChecked: true },
};

export const Invalid: Story = {
  args: { "aria-invalid": true },
};
