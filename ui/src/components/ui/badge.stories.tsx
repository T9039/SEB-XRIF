import type { Meta, StoryObj } from "@storybook/react";
import { CheckIcon, XIcon } from "lucide-react";
import { Badge } from "./badge";

const meta = {
  title: "UI/Badge",
  component: Badge,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "secondary", "destructive", "outline", "ghost", "link"],
    },
  },
  args: { children: "Badge" },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Secondary: Story = {
  args: { variant: "secondary" },
};

export const Destructive: Story = {
  args: { variant: "destructive" },
};

export const Outline: Story = {
  args: { variant: "outline" },
};

export const Ghost: Story = {
  args: { variant: "ghost" },
};

export const Link: Story = {
  args: { variant: "link", children: <a href="#">Anchor badge</a> },
};

export const WithIconStart: Story = {
  args: {
    children: (
      <>
        <CheckIcon data-icon="inline-start" />
        Approved
      </>
    ),
  },
};

export const WithIconEnd: Story = {
  args: {
    variant: "destructive",
    children: (
      <>
        Rejected
        <XIcon data-icon="inline-end" />
      </>
    ),
  },
};
