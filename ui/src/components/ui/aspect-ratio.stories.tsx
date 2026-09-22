import type { Meta, StoryObj } from "@storybook/react";
import { AspectRatio } from "./aspect-ratio";

const meta = {
  title: "UI/AspectRatio",
  component: AspectRatio,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  args: { ratio: 16 / 9 },
} satisfies Meta<typeof AspectRatio>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <AspectRatio {...args} className="w-80 overflow-hidden rounded-4xl bg-muted">
      <img
        src="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
        alt="Mountains"
        className="size-full object-cover"
      />
    </AspectRatio>
  ),
};

export const Square: Story = {
  args: { ratio: 1 },
  render: (args) => (
    <AspectRatio {...args} className="w-48 overflow-hidden rounded-4xl bg-muted">
      <img
        src="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800"
        alt="Forest"
        className="size-full object-cover"
      />
    </AspectRatio>
  ),
};
