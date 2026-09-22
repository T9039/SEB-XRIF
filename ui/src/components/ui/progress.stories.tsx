import type { Meta, StoryObj } from "@storybook/react";
import { Progress, ProgressLabel, ProgressValue } from "./progress";

const meta = {
  title: "UI/Progress",
  component: Progress,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  render: (args) => (
    <div className="w-80">
      <Progress {...args} />
    </div>
  ),
} satisfies Meta<typeof Progress>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { value: 50 },
};

export const Partial: Story = {
  args: { value: 25 },
};

export const Complete: Story = {
  args: { value: 100 },
};

export const WithLabel: Story = {
  args: { value: 65 },
  render: (args) => (
    <div className="w-80">
      <Progress {...args}>
        <ProgressLabel>Uploading…</ProgressLabel>
        <ProgressValue />
      </Progress>
    </div>
  ),
};
