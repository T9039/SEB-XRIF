import type { Meta, StoryObj } from "@storybook/react";
import { Skeleton } from "./skeleton";

const meta = {
  title: "UI/Skeleton",
  component: Skeleton,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  args: { className: "h-4 w-64" },
} satisfies Meta<typeof Skeleton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Circle: Story = {
  args: { className: "size-12 rounded-full" },
};

export const Card: Story = {
  render: (args) => (
    <div className="flex w-72 flex-col gap-3 rounded-4xl border bg-card p-4 shadow-md">
      <Skeleton className="h-32 w-full" {...args} />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  ),
};

export const TextLines: Story = {
  render: (args) => (
    <div className="flex w-72 flex-col gap-2">
      <Skeleton className="h-4 w-full" {...args} />
      <Skeleton className="h-4 w-11/12" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  ),
};
