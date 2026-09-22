import type { Meta, StoryObj } from "@storybook/react";
import { Avatar, AvatarFallback } from "./avatar";
import {
  Message,
  MessageAvatar,
  MessageContent,
  MessageFooter,
  MessageGroup,
  MessageHeader,
} from "./message";

const meta = {
  title: "UI/Message",
  component: Message,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    align: { control: "select", options: ["start", "end"] },
  },
} satisfies Meta<typeof Message>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Chat: Story = {
  render: () => (
    <div className="w-96 rounded-3xl border p-4">
      <MessageGroup>
        <Message align="start">
          <MessageAvatar>
            <Avatar size="sm">
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
          </MessageAvatar>
          <MessageContent>
            <MessageHeader>Jane Doe · 09:41</MessageHeader>
            <div className="w-fit rounded-3xl rounded-bl-md bg-muted px-3.5 py-2.5 text-sm">
              Hey, did you get a chance to review the contract draft?
            </div>
            <MessageFooter>Sent</MessageFooter>
          </MessageContent>
        </Message>
        <Message align="end">
          <MessageContent>
            <div className="w-fit self-end rounded-3xl rounded-br-md bg-primary px-3.5 py-2.5 text-sm text-primary-foreground">
              Yes! Just finished. A couple of clauses need clarification though.
            </div>
            <MessageFooter>Read 09:43</MessageFooter>
          </MessageContent>
        </Message>
        <Message align="start">
          <MessageAvatar>
            <Avatar size="sm">
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
          </MessageAvatar>
          <MessageContent>
            <MessageHeader>Jane Doe · 09:44</MessageHeader>
            <div className="w-fit rounded-3xl rounded-bl-md bg-muted px-3.5 py-2.5 text-sm">
              Let's go through them on the call tomorrow.
            </div>
          </MessageContent>
        </Message>
      </MessageGroup>
    </div>
  ),
};
