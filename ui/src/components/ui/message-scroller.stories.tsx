import type { Meta, StoryObj } from "@storybook/react";
import { Avatar, AvatarFallback } from "./avatar";
import { Bubble, BubbleContent } from "./bubble";
import { Message, MessageAvatar, MessageContent } from "./message";
import {
  MessageScroller,
  MessageScrollerButton,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from "./message-scroller";

const meta = {
  title: "UI/MessageScroller",
  component: MessageScroller,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof MessageScroller>;

export default meta;
type Story = StoryObj<typeof meta>;

const threads = [
  {
    id: 1,
    name: "Jane Doe",
    messages: [
      "Morning! The release is looking good.",
      "Can we ship it this week?",
      "I've updated the QA checklist too.",
    ],
    align: "start" as const,
  },
  {
    id: 2,
    name: "Me",
    messages: [
      "Yes, everything looks on track.",
      "I'll run the final smoke tests tonight.",
      "Let's target Thursday for the rollout.",
    ],
    align: "end" as const,
  },
  {
    id: 3,
    name: "Jane Doe",
    messages: ["Perfect. I'll prepare the changelog.", "One more thing — update the docs link."],
    align: "start" as const,
  },
  {
    id: 4,
    name: "Me",
    messages: ["Done! Docs are live."],
    align: "end" as const,
  },
];

export const Default: Story = {
  render: (args) => (
    <MessageScrollerProvider>
      <MessageScroller {...args} className="h-96 w-96 rounded-3xl border">
        <MessageScrollerViewport>
          <MessageScrollerContent>
            {threads.map((thread) => (
              <MessageScrollerItem key={thread.id} scrollAnchor={thread.id === threads.length}>
                <Message align={thread.align}>
                  {thread.align === "start" && (
                    <MessageAvatar>
                      <Avatar size="sm">
                        <AvatarFallback>JD</AvatarFallback>
                      </Avatar>
                    </MessageAvatar>
                  )}
                  <MessageContent>
                    {thread.messages.map((message, index) => (
                      <Bubble key={index} variant={thread.align === "end" ? "default" : "muted"}>
                        <BubbleContent>{message}</BubbleContent>
                      </Bubble>
                    ))}
                  </MessageContent>
                </Message>
              </MessageScrollerItem>
            ))}
          </MessageScrollerContent>
        </MessageScrollerViewport>
        <MessageScrollerButton />
      </MessageScroller>
    </MessageScrollerProvider>
  ),
};
