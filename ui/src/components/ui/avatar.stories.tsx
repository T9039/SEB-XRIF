import type { Meta, StoryObj } from "@storybook/react";
import { BadgeCheckIcon } from "lucide-react";
import {
  Avatar,
  AvatarBadge,
  AvatarFallback,
  AvatarGroup,
  AvatarGroupCount,
  AvatarImage,
} from "./avatar";

const meta = {
  title: "UI/Avatar",
  component: Avatar,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    size: { control: "select", options: ["sm", "default", "lg"] },
  },
} satisfies Meta<typeof Avatar>;

export default meta;
type Story = StoryObj<typeof meta>;

const image =
  "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&crop=faces";

export const Default: Story = {
  render: (args) => (
    <Avatar {...args}>
      <AvatarImage src={image} alt="Jane Doe" />
      <AvatarFallback>JD</AvatarFallback>
    </Avatar>
  ),
};

export const Fallback: Story = {
  render: (args) => (
    <Avatar {...args}>
      <AvatarFallback>JD</AvatarFallback>
    </Avatar>
  ),
};

export const Large: Story = {
  args: { size: "lg" },
  render: (args) => (
    <Avatar {...args}>
      <AvatarImage src={image} alt="Jane Doe" />
      <AvatarFallback>JD</AvatarFallback>
    </Avatar>
  ),
};

export const Small: Story = {
  args: { size: "sm" },
  render: (args) => (
    <Avatar {...args}>
      <AvatarImage src={image} alt="Jane Doe" />
      <AvatarFallback>JD</AvatarFallback>
    </Avatar>
  ),
};

export const WithBadge: Story = {
  render: (args) => (
    <Avatar {...args}>
      <AvatarImage src={image} alt="Jane Doe" />
      <AvatarFallback>JD</AvatarFallback>
      <AvatarBadge>
        <BadgeCheckIcon />
      </AvatarBadge>
    </Avatar>
  ),
};

export const Group: Story = {
  render: () => (
    <AvatarGroup>
      <Avatar>
        <AvatarImage src={image} alt="Jane Doe" />
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>
      <Avatar>
        <AvatarFallback>JM</AvatarFallback>
      </Avatar>
      <Avatar>
        <AvatarFallback>TW</AvatarFallback>
      </Avatar>
      <Avatar>
        <AvatarFallback>AK</AvatarFallback>
      </Avatar>
      <AvatarGroupCount>+12</AvatarGroupCount>
    </AvatarGroup>
  ),
};

export const FallbackColors: Story = {
  render: () => (
    <AvatarGroup>
      <Avatar>
        <AvatarFallback className="bg-primary text-primary-foreground">JD</AvatarFallback>
      </Avatar>
      <Avatar>
        <AvatarFallback className="bg-secondary text-secondary-foreground">JM</AvatarFallback>
      </Avatar>
      <Avatar>
        <AvatarFallback className="bg-muted text-muted-foreground">TW</AvatarFallback>
      </Avatar>
    </AvatarGroup>
  ),
};
