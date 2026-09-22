import type { Meta, StoryObj } from "@storybook/react";
import { SignUpPage } from "./sign-up";

const meta = {
  title: "Auth/Views/Sign Up",
  component: SignUpPage,
  parameters: { layout: "fullscreen" },
  tags: ["autodocs"],
  argTypes: {
    error: { control: "text" },
    isLoading: { control: "boolean" },
    isSocialLoading: { control: "boolean" },
    defaultName: { control: "text" },
    defaultEmail: { control: "text" },
  },
} satisfies Meta<typeof SignUpPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithDefaults: Story = {
  args: { defaultName: "Alice Johnson", defaultEmail: "alice@example.com" },
};

export const Loading: Story = {
  args: { isLoading: true },
};

export const SocialLoading: Story = {
  args: { isSocialLoading: true, socialProvider: "google" },
};

export const WithError: Story = {
  args: { error: "This email is already registered. Try signing in instead." },
};

export const InvalidField: Story = {
  args: { fieldErrors: { name: "Name must be at least 2 characters" } },
};

export const PasswordsMismatch: Story = {
  args: { fieldErrors: { confirmPassword: "Passwords do not match" } },
};
