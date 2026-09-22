import type { Meta, StoryObj } from "@storybook/react";
import { UserIcon } from "lucide-react";
import { Badge } from "./badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./tabs";

const meta = {
  title: "UI/Tabs",
  component: Tabs,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Tabs>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { defaultValue: "account" },
  render: (args) => (
    <div className="w-96">
      <Tabs {...args}>
        <TabsList className="w-full">
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="password">Password</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        <TabsContent value="account">Make changes to your account here.</TabsContent>
        <TabsContent value="password">Change your password here.</TabsContent>
        <TabsContent value="settings">Adjust your preferences here.</TabsContent>
      </Tabs>
    </div>
  ),
};

export const LineVariant: Story = {
  args: { defaultValue: "overview" },
  render: (args) => (
    <div className="w-96">
      <Tabs {...args}>
        <TabsList variant="line">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>
        <TabsContent value="overview">An underline indicator marks the active tab.</TabsContent>
        <TabsContent value="activity">Your recent activity lives here.</TabsContent>
        <TabsContent value="reports">Downloadable reports live here.</TabsContent>
      </Tabs>
    </div>
  ),
};

export const Vertical: Story = {
  args: { defaultValue: "account", orientation: "vertical" },
  render: (args) => (
    <div className="flex gap-6">
      <Tabs {...args}>
        <TabsList>
          <TabsTrigger value="account">
            <UserIcon />
            Account
          </TabsTrigger>
          <TabsTrigger value="password">Password</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        <TabsContent value="account">Account settings panel.</TabsContent>
        <TabsContent value="password">Password settings panel.</TabsContent>
        <TabsContent value="settings">General settings panel.</TabsContent>
      </Tabs>
    </div>
  ),
};

export const WithBadge: Story = {
  args: { defaultValue: "inbox" },
  render: (args) => (
    <div className="w-96">
      <Tabs {...args}>
        <TabsList className="w-full">
          <TabsTrigger value="inbox">
            Inbox <Badge variant="secondary">3</Badge>
          </TabsTrigger>
          <TabsTrigger value="sent">Sent</TabsTrigger>
          <TabsTrigger value="drafts">Drafts</TabsTrigger>
        </TabsList>
        <TabsContent value="inbox">You have 3 unread messages.</TabsContent>
        <TabsContent value="sent">Messages you have sent.</TabsContent>
        <TabsContent value="drafts">Saved but not sent.</TabsContent>
      </Tabs>
    </div>
  ),
};
