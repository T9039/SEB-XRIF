import type { Meta, StoryObj } from "@storybook/react";
import { Slider } from "./slider";

const meta = {
  title: "UI/Slider",
  component: Slider,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  render: (args) => (
    <div className="w-72">
      <Slider {...args} />
    </div>
  ),
} satisfies Meta<typeof Slider>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithValue: Story = {
  args: { defaultValue: [50] },
};

export const Range: Story = {
  args: { defaultValue: [25, 75] },
};

export const Disabled: Story = {
  args: { defaultValue: [40], disabled: true },
};

export const Vertical: Story = {
  render: (args) => (
    <div className="h-48 w-72">
      <Slider defaultValue={[60]} orientation="vertical" {...args} />
    </div>
  ),
};
