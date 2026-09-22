import type { Meta, StoryObj } from "@storybook/react";
import { ScrollArea, ScrollBar } from "./scroll-area";

const meta = {
  title: "UI/ScrollArea",
  component: ScrollArea,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof ScrollArea>;

export default meta;
type Story = StoryObj<typeof meta>;

const tags = Array.from({ length: 50 }, (_, index) => `v1.2.0-beta.${index}`);

export const Vertical: Story = {
  render: (args) => (
    <ScrollArea {...args} className="h-64 w-72 rounded-3xl border">
      <div className="p-4">
        {tags.map((tag) => (
          <p key={tag} className="py-0.5 text-sm text-muted-foreground">
            {tag}
          </p>
        ))}
      </div>
    </ScrollArea>
  ),
};

export const Horizontal: Story = {
  render: (args) => (
    <ScrollArea {...args} className="w-80 whitespace-nowrap rounded-3xl border">
      <div className="flex w-max gap-4 p-4">
        {tags.slice(0, 12).map((tag) => (
          <div key={tag} className="flex w-40 shrink-0 flex-col gap-1">
            <div className="aspect-video rounded-2xl bg-muted" />
            <p className="truncate text-sm text-muted-foreground">{tag}</p>
          </div>
        ))}
      </div>
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  ),
};
