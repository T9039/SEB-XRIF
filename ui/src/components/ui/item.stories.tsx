import type { Meta, StoryObj } from "@storybook/react";
import { FileTextIcon, MoreHorizontalIcon, Trash2Icon } from "lucide-react";
import { Button } from "./button";
import { Badge } from "./badge";
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemMedia,
  ItemTitle,
} from "./item";

const meta = {
  title: "UI/Item",
  component: Item,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    variant: { control: "select", options: ["default", "outline", "muted"] },
    size: { control: "select", options: ["default", "sm", "xs"] },
  },
} satisfies Meta<typeof Item>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <div className="w-96">
      <Item {...args}>
        <ItemMedia variant="icon">
          <FileTextIcon />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Quarterly report.pdf</ItemTitle>
          <ItemDescription>Uploaded by Jane Doe · 2.4 MB</ItemDescription>
        </ItemContent>
        <ItemActions>
          <Button variant="ghost" size="icon-sm" aria-label="More options">
            <MoreHorizontalIcon />
          </Button>
        </ItemActions>
      </Item>
    </div>
  ),
};

export const WithBadge: Story = {
  render: (args) => (
    <div className="w-96">
      <Item {...args}>
        <ItemContent>
          <ItemTitle>Project Alpha</ItemTitle>
          <ItemDescription>12 documents · Last updated today</ItemDescription>
        </ItemContent>
        <Badge variant="secondary">Active</Badge>
      </Item>
    </div>
  ),
};

export const Outline: Story = {
  args: { variant: "outline" },
  render: (args) => (
    <div className="w-96">
      <Item {...args}>
        <ItemContent>
          <ItemTitle>Outline variant</ItemTitle>
          <ItemDescription>Bordered item used in lists and tables.</ItemDescription>
        </ItemContent>
      </Item>
    </div>
  ),
};

export const Muted: Story = {
  args: { variant: "muted", size: "sm" },
  render: (args) => (
    <div className="w-96">
      <Item {...args}>
        <ItemContent>
          <ItemTitle>Muted variant</ItemTitle>
          <ItemDescription>A quieter background for secondary rows.</ItemDescription>
        </ItemContent>
        <Button variant="ghost" size="icon-xs" aria-label="Delete">
          <Trash2Icon />
        </Button>
      </Item>
    </div>
  ),
};

export const Group: Story = {
  render: (args) => (
    <div className="w-96">
      <ItemGroup {...args}>
        <Item>
          <ItemMedia variant="icon">
            <FileTextIcon />
          </ItemMedia>
          <ItemContent>
            <ItemTitle>Invoice 2026-001</ItemTitle>
            <ItemDescription>Draft · 1.1 MB</ItemDescription>
          </ItemContent>
        </Item>
        <Item>
          <ItemMedia variant="icon">
            <FileTextIcon />
          </ItemMedia>
          <ItemContent>
            <ItemTitle>Invoice 2026-002</ItemTitle>
            <ItemDescription>Approved · 820 KB</ItemDescription>
          </ItemContent>
        </Item>
        <Item>
          <ItemMedia variant="icon">
            <FileTextIcon />
          </ItemMedia>
          <ItemContent>
            <ItemTitle>Invoice 2026-003</ItemTitle>
            <ItemDescription>Paid · 1.4 MB</ItemDescription>
          </ItemContent>
        </Item>
      </ItemGroup>
    </div>
  ),
};
