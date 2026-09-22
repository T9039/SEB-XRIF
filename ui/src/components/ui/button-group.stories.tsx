import type { Meta, StoryObj } from "@storybook/react";
import { PlusIcon, SearchIcon } from "lucide-react";
import { Button } from "./button";
import { ButtonGroup, ButtonGroupSeparator, ButtonGroupText } from "./button-group";

const meta = {
  title: "UI/ButtonGroup",
  component: ButtonGroup,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    orientation: { control: "select", options: ["horizontal", "vertical"] },
  },
} satisfies Meta<typeof ButtonGroup>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <ButtonGroup {...args}>
      <Button variant="outline">Undo</Button>
      <Button variant="outline">Redo</Button>
      <Button variant="outline">Clear</Button>
    </ButtonGroup>
  ),
};

export const WithPrimaryAction: Story = {
  render: (args) => (
    <ButtonGroup {...args}>
      <Button>Save</Button>
      <Button variant="outline" size="icon">
        <PlusIcon />
      </Button>
    </ButtonGroup>
  ),
};

export const WithTextSegment: Story = {
  render: (args) => (
    <ButtonGroup {...args}>
      <Button variant="outline">
        <SearchIcon />
        Search
      </Button>
      <ButtonGroupText>
        Filtered by: <b>All</b>
      </ButtonGroupText>
    </ButtonGroup>
  ),
};

export const WithSeparator: Story = {
  render: (args) => (
    <ButtonGroup {...args}>
      <Button variant="outline">Edit</Button>
      <ButtonGroupSeparator />
      <Button variant="outline">Delete</Button>
    </ButtonGroup>
  ),
};

export const Vertical: Story = {
  args: { orientation: "vertical" },
  render: (args) => (
    <div className="flex w-40 flex-col gap-4">
      <ButtonGroup {...args}>
        <Button variant="outline">Top</Button>
        <Button variant="outline">Middle</Button>
        <Button variant="outline">Bottom</Button>
      </ButtonGroup>
    </div>
  ),
};
