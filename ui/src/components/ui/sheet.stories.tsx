import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";
import { Input } from "./input";
import { Label } from "./label";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "./sheet";

const meta = {
  title: "UI/Sheet",
  component: Sheet,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Sheet>;

export default meta;
type Story = StoryObj<typeof meta>;

const SheetForm = () => (
  <>
    <SheetHeader>
      <SheetTitle>Edit profile</SheetTitle>
      <SheetDescription>Make changes to your profile here.</SheetDescription>
    </SheetHeader>
    <div className="flex flex-col gap-4 p-6">
      <div className="flex flex-col gap-2">
        <Label htmlFor="sheet-name">Name</Label>
        <Input id="sheet-name" defaultValue="Jane Doe" />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="sheet-email">Email</Label>
        <Input id="sheet-email" type="email" defaultValue="jane@example.com" />
      </div>
    </div>
    <SheetFooter>
      <Button type="button">Save changes</Button>
    </SheetFooter>
  </>
);

export const Right: Story = {
  render: (args) => (
    <Sheet {...args}>
      <SheetTrigger render={<Button variant="outline" />}>Open Sheet</SheetTrigger>
      <SheetContent>
        <SheetForm />
      </SheetContent>
    </Sheet>
  ),
};

export const Left: Story = {
  args: { defaultOpen: true },
  render: (args) => (
    <Sheet {...args}>
      <SheetTrigger render={<Button variant="outline" />}>Open Sheet</SheetTrigger>
      <SheetContent side="left">
        <SheetForm />
      </SheetContent>
    </Sheet>
  ),
};

export const Top: Story = {
  render: (args) => (
    <Sheet {...args}>
      <SheetTrigger render={<Button variant="outline" />}>Open Sheet</SheetTrigger>
      <SheetContent side="top">
        <SheetHeader>
          <SheetTitle>Notifications</SheetTitle>
          <SheetDescription>You have 3 unread notifications.</SheetDescription>
        </SheetHeader>
      </SheetContent>
    </Sheet>
  ),
};

export const Bottom: Story = {
  render: (args) => (
    <Sheet {...args}>
      <SheetTrigger render={<Button variant="outline" />}>Open Sheet</SheetTrigger>
      <SheetContent side="bottom">
        <SheetHeader>
          <SheetTitle>Confirm action</SheetTitle>
          <SheetDescription>Sheet slides up from the bottom edge.</SheetDescription>
        </SheetHeader>
        <SheetFooter>
          <Button type="button">Confirm</Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  ),
};
