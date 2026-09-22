import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "./drawer";

const meta = {
  title: "UI/Drawer",
  component: Drawer,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Drawer>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Bottom: Story = {
  render: (args) => (
    <Drawer {...args}>
      <DrawerTrigger render={<Button variant="outline" />}>Open Drawer</DrawerTrigger>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Confirm deletion</DrawerTitle>
          <DrawerDescription>This will permanently delete the selected document.</DrawerDescription>
        </DrawerHeader>
        <div className="p-4">
          <p className="text-muted-foreground">
            You can swipe the drawer down or press Escape to dismiss it.
          </p>
        </div>
        <DrawerFooter>
          <Button type="button">Delete</Button>
          <Button type="button" variant="outline">
            Cancel
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  ),
};

export const WithSwipeHandle: Story = {
  args: { showSwipeHandle: true },
  render: (args) => (
    <Drawer {...args}>
      <DrawerTrigger render={<Button variant="outline" />}>Open Drawer</DrawerTrigger>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Bottom sheet</DrawerTitle>
          <DrawerDescription>Includes a swipe handle for touch devices.</DrawerDescription>
        </DrawerHeader>
        <div className="p-4">
          <p className="text-muted-foreground">Drag the handle to expand, snap, or dismiss.</p>
        </div>
      </DrawerContent>
    </Drawer>
  ),
};
