import type { Meta, StoryObj } from "@storybook/react";
import { Label } from "./label";
import { InputOTP, InputOTPGroup, InputOTPSeparator, InputOTPSlot } from "./input-otp";

const meta = {
  title: "UI/InputOTP",
  component: InputOTP,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  args: { maxLength: 6 },
} satisfies Meta<typeof InputOTP>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <div className="flex flex-col gap-2">
      <Label htmlFor="otp-default">One-time password</Label>
      <InputOTP id="otp-default" maxLength={6}>
        <InputOTPGroup>
          {Array.from({ length: 6 }, (_, index) => (
            <InputOTPSlot key={index} index={index} />
          ))}
        </InputOTPGroup>
      </InputOTP>
    </div>
  ),
};

export const Separated: Story = {
  render: () => (
    <div className="flex flex-col gap-2">
      <Label htmlFor="otp-separated">One-time password</Label>
      <InputOTP id="otp-separated" maxLength={6}>
        <InputOTPGroup>
          {Array.from({ length: 3 }, (_, index) => (
            <InputOTPSlot key={index} index={index} />
          ))}
        </InputOTPGroup>
        <InputOTPSeparator />
        <InputOTPGroup>
          {Array.from({ length: 3 }, (_, index) => (
            <InputOTPSlot key={index + 3} index={index + 3} />
          ))}
        </InputOTPGroup>
      </InputOTP>
    </div>
  ),
};

export const WithValue: Story = {
  render: () => (
    <div className="flex flex-col gap-2">
      <Label htmlFor="otp-value">Prefilled code</Label>
      <InputOTP id="otp-value" maxLength={6} value="123456">
        <InputOTPGroup>
          {Array.from({ length: 6 }, (_, index) => (
            <InputOTPSlot key={index} index={index} />
          ))}
        </InputOTPGroup>
      </InputOTP>
    </div>
  ),
};
