import type { Meta, StoryObj } from "@storybook/react";
import { ChevronDownIcon } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./collapsible";

const meta = {
  title: "UI/Collapsible",
  component: Collapsible,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  render: (args) => (
    <div className="w-80 rounded-3xl border bg-card p-4">
      <Collapsible {...args}>
        <CollapsibleTrigger className="flex w-full items-center justify-between text-sm font-medium outline-none focus-visible:ring-3 focus-visible:ring-ring/30">
          <span>Show details</span>
          <ChevronDownIcon className="size-4 transition-transform group-data-open:rotate-180" />
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-3 text-sm text-muted-foreground">
          <p>
            Extra details revealed when the collapsible is open. This content can be anything,
            including lists, forms, or nested components.
          </p>
        </CollapsibleContent>
      </Collapsible>
    </div>
  ),
} satisfies Meta<typeof Collapsible>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const OpenByDefault: Story = {
  args: { defaultOpen: true },
};

export const Disabled: Story = {
  args: { disabled: true },
};
