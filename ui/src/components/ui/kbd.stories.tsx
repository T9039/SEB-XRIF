import type { Meta, StoryObj } from "@storybook/react";
import { Kbd, KbdGroup } from "./kbd";

const meta = {
  title: "UI/Kbd",
  component: Kbd,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  args: { children: "⌘K" },
} satisfies Meta<typeof Kbd>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Letter: Story = {
  args: { children: "K" },
};

export const Long: Story = {
  args: { children: "Ctrl" },
};

export const Group: Story = {
  render: (args) => (
    <KbdGroup>
      <Kbd {...args}>⌘</Kbd>
      <Kbd>⇧</Kbd>
      <Kbd>P</Kbd>
    </KbdGroup>
  ),
};
