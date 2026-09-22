import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { DirectionProvider, useDirection } from "./direction";
import { Button } from "./button";

const DirectionChild = () => {
  const direction = useDirection();
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-muted-foreground">Reading direction:</span>
      <span className="font-medium text-foreground">{direction}</span>
    </div>
  );
};

const DirectionDemo = () => {
  const [direction, setDirection] = useState<"ltr" | "rtl">("ltr");
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex gap-2">
        <Button variant="outline" onClick={() => setDirection("ltr")}>
          LTR
        </Button>
        <Button variant="outline" onClick={() => setDirection("rtl")}>
          RTL
        </Button>
      </div>
      <DirectionProvider direction={direction}>
        <DirectionChild />
      </DirectionProvider>
    </div>
  );
};

const meta = {
  title: "UI/Direction",
  component: DirectionProvider,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof DirectionProvider>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => <DirectionDemo />,
};
