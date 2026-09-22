import type { Meta, StoryObj } from "@storybook/react";
import { InboxIcon } from "lucide-react";
import { Button } from "./button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "./empty";

const meta = {
  title: "UI/Empty",
  component: Empty,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Empty>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <div className="w-96">
      <Empty {...args}>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <InboxIcon />
          </EmptyMedia>
          <EmptyTitle>No documents yet</EmptyTitle>
          <EmptyDescription>
            Documents you upload will appear here. Get started by uploading your first file.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button>Upload document</Button>
        </EmptyContent>
      </Empty>
    </div>
  ),
};

export const Minimal: Story = {
  render: (args) => (
    <div className="w-96">
      <Empty {...args}>
        <EmptyHeader>
          <EmptyTitle>Nothing here</EmptyTitle>
          <EmptyDescription>There are no results matching your search.</EmptyDescription>
        </EmptyHeader>
      </Empty>
    </div>
  ),
};

export const WithMediaOnly: Story = {
  render: (args) => (
    <div className="w-96">
      <Empty {...args}>
        <EmptyMedia>
          <InboxIcon className="size-10 text-muted-foreground" />
        </EmptyMedia>
      </Empty>
    </div>
  ),
};
