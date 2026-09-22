import type { Meta, StoryObj } from "@storybook/react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "./accordion";

const meta = {
  title: "UI/Accordion",
  component: Accordion,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Accordion>;

export default meta;
type Story = StoryObj<typeof meta>;

const items = [
  {
    value: "item-1",
    title: "Is it accessible?",
    content: "Yes. It adheres to the WAI-ARIA design pattern and is fully keyboard navigable.",
  },
  {
    value: "item-2",
    title: "How do I style it?",
    content:
      "You can use the variant prop or pass Tailwind classes through className on each part.",
  },
  {
    value: "item-3",
    title: "Is it animated?",
    content:
      "Yes. Panels animate open and closed using CSS transitions powered by data attributes.",
  },
];

export const Single: Story = {
  args: { defaultValue: ["item-1"] },
  render: (args) => (
    <div className="w-96">
      <Accordion {...args}>
        {items.map((item) => (
          <AccordionItem key={item.value} value={item.value}>
            <AccordionTrigger>{item.title}</AccordionTrigger>
            <AccordionContent>{item.content}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  ),
};

export const Multiple: Story = {
  args: { multiple: true, defaultValue: ["item-1"] },
  render: (args) => (
    <div className="w-96">
      <Accordion {...args}>
        {items.map((item) => (
          <AccordionItem key={item.value} value={item.value}>
            <AccordionTrigger>{item.title}</AccordionTrigger>
            <AccordionContent>{item.content}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  ),
};
