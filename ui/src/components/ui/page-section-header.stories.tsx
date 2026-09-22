import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";
import { Plus } from "lucide-react";
import { PageSectionHeader } from "./page-section-header";

const meta = {
  title: "UI/PageSectionHeader",
  component: PageSectionHeader,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof PageSectionHeader>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    breadcrumb: [{ label: "Content" }, { label: "Storage" }],
    title: "Storage",
    description: "Manage corporate documents across the workspace.",
  },
};

export const WithActions: Story = {
  args: {
    breadcrumb: [{ label: "Security" }, { label: "Audit Logs" }],
    title: "Audit Logs",
    description: "Track security events and document access.",
    actions: (
      <Button size="sm">
        <Plus className="size-4" /> Export
      </Button>
    ),
  },
};
