import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { CarrotIcon } from "lucide-react";
import { Label } from "./label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from "./select";

const meta = {
  title: "UI/Select",
  component: Select,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Select>;

export default meta;
type Story = StoryObj<typeof meta>;

const SelectDemo = ({ size }: { size?: "sm" | "default" }) => {
  const [value, setValue] = useState("");
  return (
    <Select value={value} onValueChange={(value) => setValue(value ?? "")}>
      <SelectTrigger size={size}>
        <SelectValue placeholder="Select a fruit" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Fruits</SelectLabel>
          <SelectItem value="apple">Apple</SelectItem>
          <SelectItem value="banana">Banana</SelectItem>
          <SelectItem value="carrot">
            <CarrotIcon />
            Carrot
          </SelectItem>
        </SelectGroup>
        <SelectSeparator />
        <SelectGroup>
          <SelectLabel>Vegetables</SelectLabel>
          <SelectItem value="lettuce">Lettuce</SelectItem>
          <SelectItem value="tomato">Tomato</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  );
};

export const Default: Story = {
  render: () => <SelectDemo />,
};

export const WithLabel: Story = {
  render: () => (
    <div className="flex flex-col gap-2">
      <Label htmlFor="fruit-select">Fruit</Label>
      <SelectDemo />
    </div>
  ),
};

export const Small: Story = {
  render: () => (
    <div className="flex flex-col gap-2">
      <Label htmlFor="fruit-select-sm">Fruit</Label>
      <SelectDemo size="sm" />
    </div>
  ),
};
