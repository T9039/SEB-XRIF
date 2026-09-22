import type { Meta, StoryObj } from "@storybook/react";
import { MailIcon, SearchIcon } from "lucide-react";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
  InputGroupText,
  InputGroupTextarea,
} from "./input-group";

const meta = {
  title: "UI/InputGroup",
  component: InputGroup,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  render: (args) => (
    <div className="w-80">
      <InputGroup {...args} />
    </div>
  ),
} satisfies Meta<typeof InputGroup>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <InputGroup {...args}>
      <InputGroupInput placeholder="Search…" aria-label="Search" />
      <InputGroupAddon align="inline-end">
        <InputGroupButton aria-label="Search">
          <SearchIcon />
        </InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  ),
};

export const WithLeadingAddon: Story = {
  render: (args) => (
    <InputGroup {...args}>
      <InputGroupAddon>
        <MailIcon />
      </InputGroupAddon>
      <InputGroupInput type="email" placeholder="you@example.com" aria-label="Email" />
    </InputGroup>
  ),
};

export const WithTextAddon: Story = {
  render: (args) => (
    <InputGroup {...args}>
      <InputGroupInput placeholder="Amount" aria-label="Amount" />
      <InputGroupAddon align="inline-end">
        <InputGroupText>USD</InputGroupText>
      </InputGroupAddon>
    </InputGroup>
  ),
};

export const WithButtonBothSides: Story = {
  render: (args) => (
    <InputGroup {...args}>
      <InputGroupAddon>
        <InputGroupButton aria-label="Decrease">-</InputGroupButton>
      </InputGroupAddon>
      <InputGroupInput defaultValue="12" aria-label="Quantity" />
      <InputGroupAddon align="inline-end">
        <InputGroupButton aria-label="Increase">+</InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  ),
};

export const WithTextarea: Story = {
  render: (args) => (
    <InputGroup {...args}>
      <InputGroupTextarea placeholder="Write a comment…" aria-label="Comment" />
      <InputGroupAddon align="block-end">
        <InputGroupButton>Post</InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  ),
};
