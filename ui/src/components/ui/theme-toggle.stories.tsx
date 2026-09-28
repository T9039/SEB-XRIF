import type { Meta, StoryObj } from "@storybook/react";
import { ThemeProvider } from "../../hooks/use-theme";
import { ThemeToggle } from "./theme-toggle";

const meta = {
  title: "UI/ThemeToggle",
  component: ThemeToggle,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <ThemeProvider defaultTheme="light" storageKey="storybook-theme-toggle">
        <Story />
      </ThemeProvider>
    ),
  ],
} satisfies Meta<typeof ThemeToggle>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Outline: Story = {
  args: { variant: "outline" },
};
