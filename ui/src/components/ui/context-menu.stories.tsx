import type { Meta, StoryObj } from "@storybook/react";
import { FileTextIcon, FolderIcon, Trash2Icon } from "lucide-react";
import {
  ContextMenu,
  ContextMenuCheckboxItem,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuSeparator,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from "./context-menu";

const meta = {
  title: "UI/ContextMenu",
  component: ContextMenu,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof ContextMenu>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <ContextMenu {...args}>
      <ContextMenuTrigger className="flex h-48 w-96 items-center justify-center rounded-3xl border border-dashed text-sm text-muted-foreground">
        Right-click inside this area
      </ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem>
          <FileTextIcon />
          New file
        </ContextMenuItem>
        <ContextMenuItem>
          <FolderIcon />
          New folder
        </ContextMenuItem>
        <ContextMenuSub>
          <ContextMenuSubTrigger>Sort by</ContextMenuSubTrigger>
          <ContextMenuSubContent>
            <ContextMenuItem>Name</ContextMenuItem>
            <ContextMenuItem>Date modified</ContextMenuItem>
            <ContextMenuItem>Size</ContextMenuItem>
          </ContextMenuSubContent>
        </ContextMenuSub>
        <ContextMenuSeparator />
        <ContextMenuItem variant="destructive">
          <Trash2Icon />
          Delete
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  ),
};

export const WithCheckboxes: Story = {
  render: (args) => (
    <ContextMenu {...args}>
      <ContextMenuTrigger className="flex h-48 w-96 items-center justify-center rounded-3xl border border-dashed text-sm text-muted-foreground">
        Right-click inside this area
      </ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuLabel>View options</ContextMenuLabel>
        <ContextMenuCheckboxItem checked>Show file extensions</ContextMenuCheckboxItem>
        <ContextMenuCheckboxItem checked>Show hidden files</ContextMenuCheckboxItem>
        <ContextMenuSeparator />
        <ContextMenuRadioGroup value="grid">
          <ContextMenuLabel>Layout</ContextMenuLabel>
          <ContextMenuRadioItem value="grid">Grid</ContextMenuRadioItem>
          <ContextMenuRadioItem value="list">List</ContextMenuRadioItem>
          <ContextMenuRadioItem value="compact">Compact</ContextMenuRadioItem>
        </ContextMenuRadioGroup>
      </ContextMenuContent>
    </ContextMenu>
  ),
};
