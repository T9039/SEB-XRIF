import type { Meta, StoryObj } from "@storybook/react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./carousel";

const meta = {
  title: "UI/Carousel",
  component: Carousel,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Carousel>;

export default meta;
type Story = StoryObj<typeof meta>;

const cards = [
  { id: 1, title: "Design tokens", description: "Colors, spacing, and type scale." },
  { id: 2, title: "Components", description: "Reusable UI building blocks." },
  { id: 3, title: "Foundations", description: "Accessibility and motion guidance." },
  { id: 4, title: "Patterns", description: "Common flows and compositions." },
  { id: 5, title: "Resources", description: "Downloads, links, and templates." },
];

export const Default: Story = {
  render: (args) => (
    <div className="w-96">
      <Carousel {...args}>
        <CarouselContent>
          {cards.map((card) => (
            <CarouselItem key={card.id} className="sm:basis-1/2">
              <div className="flex aspect-video flex-col justify-between rounded-3xl border p-4">
                <p className="text-sm font-medium">{card.title}</p>
                <p className="text-xs text-muted-foreground">{card.description}</p>
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  ),
};

export const MultiplePerView: Story = {
  args: { opts: { align: "start", loop: true } },
  render: (args) => (
    <div className="w-[36rem]">
      <Carousel {...args}>
        <CarouselContent>
          {cards.map((card) => (
            <CarouselItem key={card.id} className="basis-1/3">
              <div className="flex aspect-video flex-col justify-between rounded-3xl border p-4">
                <p className="text-sm font-medium">{card.title}</p>
                <p className="text-xs text-muted-foreground">{card.description}</p>
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  ),
};
