import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "./input";

const meta = {
  title: "UI/Input",
  component: Input,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    type: {
      control: "select",
      options: ["text", "email", "password", "number", "search", "tel", "url", "file"],
    },
  },
  args: { placeholder: "Type something…" },
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithValue: Story = {
  args: { defaultValue: "Hello world", "aria-label": "Input" },
};

export const Password: Story = {
  args: { type: "password", defaultValue: "hunter2", "aria-label": "Password" },
};

export const Email: Story = {
  args: { type: "email", placeholder: "you@example.com" },
};

export const Disabled: Story = {
  args: { disabled: true, defaultValue: "Disabled input" },
};

export const ReadOnly: Story = {
  args: { readOnly: true, defaultValue: "Read only value" },
};

export const Invalid: Story = {
  args: { "aria-invalid": true, defaultValue: "Invalid value" },
};

export const WithFile: Story = {
  args: { type: "file" },
};
