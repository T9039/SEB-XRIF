import type { Meta, StoryObj } from "@storybook/react";
import { PlusIcon } from "lucide-react";
import { Button } from "./button";
import { Kbd } from "./kbd";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./tooltip";

const meta = {
  title: "UI/Tooltip",
  component: Tooltip,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Tooltip>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <TooltipProvider>
      <Tooltip {...args}>
        <TooltipTrigger render={<Button variant="outline" />}>Hover</TooltipTrigger>
        <TooltipContent>Add to library</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  ),
};

export const WithShortcut: Story = {
  render: (args) => (
    <TooltipProvider>
      <Tooltip {...args}>
        <TooltipTrigger render={<Button variant="outline" />}>
          <PlusIcon />
        </TooltipTrigger>
        <TooltipContent>
          New document
          <Kbd>⌘N</Kbd>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  ),
};

export const OpenByDefault: Story = {
  args: { defaultOpen: true },
  render: (args) => (
    <TooltipProvider>
      <Tooltip {...args}>
        <TooltipTrigger render={<Button variant="outline" />}>Hover</TooltipTrigger>
        <TooltipContent>Rendered open by default</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  ),
};
