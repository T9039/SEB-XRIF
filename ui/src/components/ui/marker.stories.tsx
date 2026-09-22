import type { Meta, StoryObj } from "@storybook/react";
import { AlertCircleIcon } from "lucide-react";
import { Marker, MarkerIcon, MarkerContent } from "./marker";

const meta = {
  title: "UI/Marker",
  component: Marker,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    variant: { control: "select", options: ["default", "separator", "border"] },
  },
} satisfies Meta<typeof Marker>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <Marker {...args}>
      <MarkerContent>Default marker content</MarkerContent>
    </Marker>
  ),
};

export const WithIcon: Story = {
  render: (args) => (
    <Marker {...args}>
      <MarkerIcon>
        <AlertCircleIcon />
      </MarkerIcon>
      <MarkerContent>A marker with an icon</MarkerContent>
    </Marker>
  ),
};

export const Separator: Story = {
  args: { variant: "separator" },
  render: (args) => (
    <Marker {...args}>
      <MarkerContent>Separator marker</MarkerContent>
    </Marker>
  ),
};

export const Border: Story = {
  args: { variant: "border" },
  render: (args) => (
    <Marker {...args}>
      <MarkerContent>Border marker</MarkerContent>
    </Marker>
  ),
};
