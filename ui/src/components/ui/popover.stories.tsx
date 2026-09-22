import type { Meta, StoryObj } from "@storybook/react";
import { Settings2Icon } from "lucide-react";
import { Button } from "./button";
import { Input } from "./input";
import { Label } from "./label";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "./popover";

const meta = {
  title: "UI/Popover",
  component: Popover,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Popover>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <Popover {...args}>
      <PopoverTrigger render={<Button variant="outline" />}>Open popover</PopoverTrigger>
      <PopoverContent>
        <PopoverHeader>
          <PopoverTitle>Dimensions</PopoverTitle>
          <PopoverDescription>Set the dimensions for the layer.</PopoverDescription>
        </PopoverHeader>
        <div className="flex items-center gap-2">
          <Label htmlFor="popover-width" className="sr-only">
            Width
          </Label>
          <Input id="popover-width" defaultValue="100%" />
          <Label htmlFor="popover-height" className="sr-only">
            Height
          </Label>
          <Input id="popover-height" defaultValue="25%" />
        </div>
      </PopoverContent>
    </Popover>
  ),
};

export const OpenByDefault: Story = {
  args: { defaultOpen: true },
  render: (args) => (
    <Popover {...args}>
      <PopoverTrigger render={<Button variant="outline" />}>Open popover</PopoverTrigger>
      <PopoverContent className="w-64">
        <PopoverHeader>
          <PopoverTitle>Account</PopoverTitle>
          <PopoverDescription>jane@example.com</PopoverDescription>
        </PopoverHeader>
        <div className="flex gap-2">
          <Button variant="outline" className="flex-1">
            Sign out
          </Button>
          <Button className="flex-1">
            <Settings2Icon />
            Settings
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  ),
};
