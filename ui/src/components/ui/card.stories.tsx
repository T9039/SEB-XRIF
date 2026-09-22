import type { Meta, StoryObj } from "@storybook/react";
import { MoreHorizontalIcon } from "lucide-react";
import { Button } from "./button";
import { Badge } from "./badge";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./card";

const meta = {
  title: "UI/Card",
  component: Card,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    size: { control: "select", options: ["default", "sm"] },
  },
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <div className="w-80">
      <Card {...args}>
        <CardHeader>
          <CardTitle>Card title</CardTitle>
          <CardDescription>Supporting text that explains the card in more detail.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            The main body of the card. Content goes here and can be any node.
          </p>
        </CardContent>
      </Card>
    </div>
  ),
};

export const WithAction: Story = {
  render: (args) => (
    <div className="w-80">
      <Card {...args}>
        <CardHeader>
          <CardTitle>Team members</CardTitle>
          <CardDescription>Manage who has access to this project.</CardDescription>
          <CardAction>
            <Button variant="ghost" size="icon-sm" aria-label="More options">
              <MoreHorizontalIcon />
            </Button>
          </CardAction>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">4 members have access to this project.</p>
        </CardContent>
      </Card>
    </div>
  ),
};

export const WithFooter: Story = {
  render: (args) => (
    <div className="w-80">
      <Card {...args}>
        <CardHeader>
          <CardTitle>Delete project</CardTitle>
          <CardDescription>This action cannot be undone.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            All associated documents and audit history will be permanently removed.
          </p>
        </CardContent>
        <CardFooter className="justify-end gap-2 border-t pt-4">
          <Button variant="outline">Cancel</Button>
          <Button variant="destructive">Delete</Button>
        </CardFooter>
      </Card>
    </div>
  ),
};

export const Small: Story = {
  args: { size: "sm" },
  render: (args) => (
    <div className="w-72">
      <Card {...args}>
        <CardHeader>
          <CardTitle>Compact card</CardTitle>
          <CardDescription>Uses tighter spacing.</CardDescription>
        </CardHeader>
        <CardContent>
          <Badge>Example</Badge>
        </CardContent>
      </Card>
    </div>
  ),
};

export const WithImage: Story = {
  render: (args) => (
    <div className="w-80">
      <Card {...args}>
        <img
          src="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800"
          alt="Landscape"
          className="h-40 w-full object-cover"
        />
        <CardHeader>
          <CardTitle>Nature</CardTitle>
          <CardDescription>An image card with a full-bleed media header.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Cards automatically crop the media to match corners.
          </p>
        </CardContent>
      </Card>
    </div>
  ),
};
