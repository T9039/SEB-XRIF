import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";
import { Checkbox } from "./checkbox";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldSet,
  FieldTitle,
} from "./field";
import { Input } from "./input";
import { Textarea } from "./textarea";

const meta = {
  title: "UI/Field",
  component: Field,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    orientation: { control: "select", options: ["vertical", "horizontal", "responsive"] },
  },
} satisfies Meta<typeof Field>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <div className="w-96">
      <Field {...args}>
        <FieldLabel htmlFor="field-name">Name</FieldLabel>
        <FieldContent>
          <Input id="field-name" placeholder="Jane Doe" />
          <FieldDescription>Your full name as it appears on your ID.</FieldDescription>
        </FieldContent>
      </Field>
    </div>
  ),
};

export const WithError: Story = {
  render: (args) => (
    <div className="w-96">
      <Field {...args}>
        <FieldLabel htmlFor="field-email">Email</FieldLabel>
        <FieldContent>
          <Input id="field-email" type="email" defaultValue="not-an-email" aria-invalid />
          <FieldError>Please enter a valid email address.</FieldError>
        </FieldContent>
      </Field>
    </div>
  ),
};

export const WithMultipleErrors: Story = {
  render: (args) => (
    <div className="w-96">
      <Field {...args}>
        <FieldLabel htmlFor="field-password">Password</FieldLabel>
        <FieldContent>
          <Input id="field-password" type="password" defaultValue="short" aria-invalid />
          <FieldError
            errors={[
              { message: "Must be at least 8 characters." },
              { message: "Must contain a number." },
            ]}
          />
        </FieldContent>
      </Field>
    </div>
  ),
};

export const Horizontal: Story = {
  args: { orientation: "horizontal" },
  render: (args) => (
    <div className="w-[28rem]">
      <Field {...args}>
        <FieldLabel htmlFor="field-site">Website</FieldLabel>
        <FieldContent>
          <Input id="field-site" type="url" placeholder="https://example.com" />
        </FieldContent>
      </Field>
    </div>
  ),
};

export const CheckboxField: Story = {
  render: (args) => (
    <div className="w-96">
      <Field {...args}>
        <FieldTitle>
          <Checkbox id="field-terms" />
        </FieldTitle>
        <FieldLabel htmlFor="field-terms" className="flex-1">
          <span>I agree to the terms and conditions</span>
        </FieldLabel>
      </Field>
    </div>
  ),
};

export const FieldGroupExample: Story = {
  render: () => (
    <div className="w-[28rem]">
      <FieldGroup>
        <Field>
          <FieldLabel htmlFor="fg-name">Name</FieldLabel>
          <FieldContent>
            <Input id="fg-name" placeholder="Jane Doe" />
          </FieldContent>
        </Field>
        <Field>
          <FieldLabel htmlFor="fg-email">Email</FieldLabel>
          <FieldContent>
            <Input id="fg-email" type="email" placeholder="jane@example.com" />
          </FieldContent>
        </Field>
        <Field>
          <FieldLabel htmlFor="fg-bio">Bio</FieldLabel>
          <FieldContent>
            <Textarea id="fg-bio" placeholder="Tell us about yourself" />
          </FieldContent>
        </Field>
        <div className="flex justify-end gap-2">
          <Button variant="outline">Cancel</Button>
          <Button>Save</Button>
        </div>
      </FieldGroup>
    </div>
  ),
};

export const FieldSetExample: Story = {
  render: () => (
    <div className="w-[28rem]">
      <FieldSet>
        <legend className="text-base font-medium">Account details</legend>
        <Field>
          <FieldLabel htmlFor="fs-name">Name</FieldLabel>
          <FieldContent>
            <Input id="fs-name" placeholder="Jane Doe" />
          </FieldContent>
        </Field>
        <Field>
          <FieldLabel htmlFor="fs-email">Email</FieldLabel>
          <FieldContent>
            <Input id="fs-email" type="email" placeholder="jane@example.com" />
          </FieldContent>
        </Field>
      </FieldSet>
    </div>
  ),
};
