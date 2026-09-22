import type { Meta, StoryObj } from "@storybook/react";
import { LoginForm } from "./login-form";

const meta = {
  title: "Auth/Blocks/LoginForm",
  component: LoginForm,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    isLoading: { control: "boolean" },
    error: { control: "text" },
    defaultEmail: { control: "text" },
    defaultRemember: { control: "boolean" },
  },
} satisfies Meta<typeof LoginForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithEmail: Story = {
  args: { defaultEmail: "alice@example.com", defaultRemember: true },
};

export const Loading: Story = {
  args: { isLoading: true, defaultEmail: "alice@example.com" },
};

export const WithError: Story = {
  args: { error: "Invalid email or password. Please try again." },
};
