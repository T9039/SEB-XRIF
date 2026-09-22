import type { Meta, StoryObj } from "@storybook/react";
import { SignUpForm } from "./sign-up-form";

const meta = {
  title: "Auth/Blocks/SignUpForm",
  component: SignUpForm,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    isLoading: { control: "boolean" },
    error: { control: "text" },
    defaultName: { control: "text" },
    defaultEmail: { control: "text" },
  },
} satisfies Meta<typeof SignUpForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithDefaults: Story = {
  args: { defaultName: "Alice Johnson", defaultEmail: "alice@example.com" },
};

export const Loading: Story = {
  args: { isLoading: true, defaultName: "Alice Johnson", defaultEmail: "alice@example.com" },
};

export const WithError: Story = {
  args: { error: "This email is already registered. Try signing in instead." },
};
