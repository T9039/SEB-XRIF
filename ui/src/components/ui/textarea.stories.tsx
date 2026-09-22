import type { Meta, StoryObj } from "@storybook/react";
import { Textarea } from "./textarea";

const meta = {
  title: "UI/Textarea",
  component: Textarea,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  args: { placeholder: "Write a description…" },
} satisfies Meta<typeof Textarea>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithValue: Story = {
  args: {
    defaultValue:
      "This is a longer piece of text. The textarea grows automatically as the content expands thanks to field-sizing.",
  },
};

export const Disabled: Story = {
  args: { disabled: true, defaultValue: "Disabled textarea" },
};

export const Invalid: Story = {
  args: { "aria-invalid": true, defaultValue: "This field has an error." },
};
