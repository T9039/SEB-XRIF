import type { Meta, StoryObj } from "@storybook/react";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "./resizable";

const meta = {
  title: "UI/Resizable",
  component: ResizablePanelGroup,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof ResizablePanelGroup>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Horizontal: Story = {
  render: () => (
    <div className="h-64 w-[36rem]">
      <ResizablePanelGroup orientation="horizontal">
        <ResizablePanel defaultSize={30}>
          <div className="flex h-full items-center justify-center rounded-l-2xl bg-muted/50 p-6">
            <p className="text-sm text-muted-foreground">Panel one</p>
          </div>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={70}>
          <div className="flex h-full items-center justify-center rounded-r-2xl bg-muted/30 p-6">
            <p className="text-sm text-muted-foreground">Panel two</p>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  ),
};

export const Vertical: Story = {
  render: () => (
    <div className="h-64 w-[36rem]">
      <ResizablePanelGroup orientation="vertical">
        <ResizablePanel defaultSize={40}>
          <div className="flex h-full items-center justify-center rounded-t-2xl bg-muted/50 p-6">
            <p className="text-sm text-muted-foreground">Panel one</p>
          </div>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={60}>
          <div className="flex h-full items-center justify-center rounded-b-2xl bg-muted/30 p-6">
            <p className="text-sm text-muted-foreground">Panel two</p>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  ),
};

export const Nested: Story = {
  render: () => (
    <div className="h-64 w-[36rem]">
      <ResizablePanelGroup orientation="horizontal">
        <ResizablePanel defaultSize={25}>
          <div className="flex h-full items-center justify-center rounded-l-2xl bg-muted/50 p-6">
            <p className="text-sm text-muted-foreground">Sidebar</p>
          </div>
        </ResizablePanel>
        <ResizableHandle />
        <ResizablePanel defaultSize={75}>
          <ResizablePanelGroup orientation="vertical">
            <ResizablePanel defaultSize={60}>
              <div className="flex h-full items-center justify-center bg-muted/30 p-6">
                <p className="text-sm text-muted-foreground">Main content</p>
              </div>
            </ResizablePanel>
            <ResizableHandle />
            <ResizablePanel defaultSize={40}>
              <div className="flex h-full items-center justify-center rounded-br-2xl bg-muted/20 p-6">
                <p className="text-sm text-muted-foreground">Inspector</p>
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  ),
};
