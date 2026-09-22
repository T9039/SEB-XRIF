import type { Meta, StoryObj } from "@storybook/react";
import { LoginPage } from "./login";

const meta = {
  title: "Auth/Views/Login",
  component: LoginPage,
  parameters: { layout: "fullscreen" },
  tags: ["autodocs"],
  argTypes: {
    error: { control: "text" },
    isLoading: { control: "boolean" },
    isSocialLoading: { control: "boolean" },
    defaultEmail: { control: "text" },
    defaultRemember: { control: "boolean" },
  },
} satisfies Meta<typeof LoginPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithPrefilledEmail: Story = {
  args: { defaultEmail: "alice@example.com", defaultRemember: true },
};

export const Loading: Story = {
  args: { isLoading: true },
};

export const SocialLoading: Story = {
  args: { isSocialLoading: true, socialProvider: "google" },
};

export const WithError: Story = {
  args: { error: "Invalid email or password. Please try again." },
};

export const InvalidField: Story = {
  args: { fieldErrors: { email: "Please enter a valid email address" } },
};

export const PasswordRequired: Story = {
  args: { fieldErrors: { password: "Password is required" } },
};
