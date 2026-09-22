import type { Meta, StoryObj } from "@storybook/react";
import { SocialLoginButtons } from "./social-login-buttons";

const meta = {
  title: "Auth/Blocks/SocialLoginButtons",
  component: SocialLoginButtons,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    isLoading: { control: "boolean" },
    disabledProvider: {
      control: "select",
      options: [null, "google", "github", "microsoft"],
    },
  },
} satisfies Meta<typeof SocialLoginButtons>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const LoadingGoogle: Story = {
  args: { isLoading: true, disabledProvider: "google" },
};
