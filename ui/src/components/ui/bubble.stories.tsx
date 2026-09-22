import type { Meta, StoryObj } from "@storybook/react";
import { ThumbsUpIcon } from "lucide-react";
import { Bubble, BubbleContent, BubbleGroup, BubbleReactions } from "./bubble";
import { Message, MessageContent } from "./message";

const meta = {
  title: "UI/Bubble",
  component: Bubble,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "secondary", "muted", "tinted", "outline", "ghost", "destructive"],
    },
  },
} satisfies Meta<typeof Bubble>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <div className="w-96 rounded-3xl border p-4">
      <Message align="end">
        <MessageContent>
          <Bubble {...args}>
            <BubbleContent>This is a default bubble.</BubbleContent>
          </Bubble>
        </MessageContent>
      </Message>
    </div>
  ),
};

export const Variants: Story = {
  render: (args) => (
    <div className="flex w-96 flex-col gap-3 rounded-3xl border p-4">
      <Bubble {...args}>
        <BubbleContent>Default</BubbleContent>
      </Bubble>
      <Bubble variant="secondary">
        <BubbleContent>Secondary</BubbleContent>
      </Bubble>
      <Bubble variant="muted">
        <BubbleContent>Muted</BubbleContent>
      </Bubble>
      <Bubble variant="tinted">
        <BubbleContent>Tinted</BubbleContent>
      </Bubble>
      <Bubble variant="outline">
        <BubbleContent>Outline</BubbleContent>
      </Bubble>
      <Bubble variant="destructive">
        <BubbleContent>Destructive</BubbleContent>
      </Bubble>
    </div>
  ),
};

export const WithReactions: Story = {
  render: (args) => (
    <div className="w-96 rounded-3xl border p-4">
      <Message align="end">
        <MessageContent>
          <BubbleGroup>
            <Bubble {...args}>
              <BubbleContent>Sounds good, let's sync tomorrow.</BubbleContent>
              <BubbleReactions>
                <span className="px-1 text-xs">👍 2</span>
              </BubbleReactions>
            </Bubble>
            <Bubble variant="muted">
              <BubbleContent>
                <ThumbsUpIcon className="size-4" />
              </BubbleContent>
            </Bubble>
          </BubbleGroup>
        </MessageContent>
      </Message>
    </div>
  ),
};
