import type { Meta, StoryObj } from "@storybook/react";
import { NativeSelect, NativeSelectOptGroup, NativeSelectOption } from "./native-select";

const meta = {
  title: "UI/NativeSelect",
  component: NativeSelect,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    size: { control: "select", options: ["sm", "default"] },
  },
} satisfies Meta<typeof NativeSelect>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <NativeSelect defaultValue="option-1" {...args}>
      <NativeSelectOption value="option-1">Option 1</NativeSelectOption>
      <NativeSelectOption value="option-2">Option 2</NativeSelectOption>
      <NativeSelectOption value="option-3">Option 3</NativeSelectOption>
    </NativeSelect>
  ),
};

export const WithGroups: Story = {
  render: (args) => (
    <NativeSelect defaultValue="apple" {...args}>
      <NativeSelectOptGroup label="Fruit">
        <NativeSelectOption value="apple">Apple</NativeSelectOption>
        <NativeSelectOption value="banana">Banana</NativeSelectOption>
        <NativeSelectOption value="orange">Orange</NativeSelectOption>
      </NativeSelectOptGroup>
      <NativeSelectOptGroup label="Vegetable">
        <NativeSelectOption value="carrot">Carrot</NativeSelectOption>
        <NativeSelectOption value="broccoli">Broccoli</NativeSelectOption>
      </NativeSelectOptGroup>
    </NativeSelect>
  ),
};

export const Small: Story = {
  args: { size: "sm" },
  render: (args) => (
    <NativeSelect defaultValue="option-1" {...args}>
      <NativeSelectOption value="option-1">Small</NativeSelectOption>
      <NativeSelectOption value="option-2">Option 2</NativeSelectOption>
    </NativeSelect>
  ),
};

export const Disabled: Story = {
  render: (args) => (
    <NativeSelect defaultValue="option-1" disabled {...args}>
      <NativeSelectOption value="option-1">Disabled</NativeSelectOption>
      <NativeSelectOption value="option-2">Option 2</NativeSelectOption>
    </NativeSelect>
  ),
};
