import type { Meta, StoryObj } from "@storybook/react";
import { Calendar } from "./calendar";

const meta = {
  title: "UI/Calendar",
  component: Calendar,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Calendar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { mode: "single" },
  render: (args) => <Calendar {...args} className="rounded-3xl border" />,
};

export const Single: Story = {
  args: { mode: "single", selected: new Date() },
  render: (args) => <Calendar {...args} className="rounded-3xl border" />,
};

export const Range: Story = {
  args: {
    mode: "range",
    selected: {
      from: new Date(),
      to: new Date(new Date().setDate(new Date().getDate() + 6)),
    },
  },
  render: (args) => <Calendar {...args} className="rounded-3xl border" />,
};

export const Multiple: Story = {
  args: { mode: "multiple", min: 1, max: 5 },
  render: (args) => <Calendar {...args} className="rounded-3xl border" />,
};

export const WithDropdowns: Story = {
  args: {
    mode: "single",
    captionLayout: "dropdown",
    startMonth: new Date(2020, 0),
    endMonth: new Date(2030, 11),
  },
  render: (args) => <Calendar {...args} className="rounded-3xl border" />,
};
