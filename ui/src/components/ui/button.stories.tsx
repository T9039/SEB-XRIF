import type { Meta, StoryObj } from "@storybook/react";
import { Loader2Icon, PlusIcon, Trash2Icon, MailIcon } from "lucide-react";
import { Button } from "./button";

const meta = {
  title: "UI/Button",
  component: Button,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "outline", "secondary", "ghost", "destructive", "link"],
    },
    size: {
      control: "select",
      options: ["default", "xs", "sm", "lg", "icon", "icon-xs", "icon-sm", "icon-lg"],
    },
  },
  args: { children: "Button" },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Outline: Story = {
  args: { variant: "outline" },
};

export const Secondary: Story = {
  args: { variant: "secondary" },
};

export const Ghost: Story = {
  args: { variant: "ghost" },
};

export const Destructive: Story = {
  args: { variant: "destructive" },
};

export const Link: Story = {
  args: { variant: "link" },
};

export const Small: Story = {
  args: { size: "sm" },
};

export const ExtraSmall: Story = {
  args: { size: "xs" },
};

export const Large: Story = {
  args: { size: "lg" },
};

export const WithIconStart: Story = {
  args: {
    children: (
      <>
        <PlusIcon data-icon="inline-start" />
        New document
      </>
    ),
  },
};

export const WithIconEnd: Story = {
  args: {
    children: (
      <>
        Send
        <MailIcon data-icon="inline-end" />
      </>
    ),
  },
};

export const IconOnly: Story = {
  args: {
    size: "icon",
    children: <Trash2Icon />,
    "aria-label": "Delete",
  },
};

export const Disabled: Story = {
  args: { disabled: true },
};

export const Loading: Story = {
  args: {
    children: (
      <>
        <Loader2Icon className="animate-spin" />
        Saving…
      </>
    ),
  },
};
