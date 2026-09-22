import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { UserIcon } from "lucide-react";
import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "./combobox";

const meta = {
  title: "UI/Combobox",
  component: Combobox,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof Combobox>;

export default meta;
type Story = StoryObj<typeof meta>;

const frameworks = ["Next.js", "SvelteKit", "Nuxt.js", "Remix", "Astro", "Angular"];

export const SingleSelect: Story = {
  render: () => {
    const [value, setValue] = useState<string | null>("Next.js");
    return (
      <div className="w-72">
        <Combobox items={frameworks} value={value} onValueChange={setValue}>
          <ComboboxInput placeholder="Select a framework…" />
          <ComboboxContent>
            <ComboboxList>
              {(framework) => (
                <ComboboxItem key={framework} value={framework}>
                  {framework}
                </ComboboxItem>
              )}
            </ComboboxList>
            <ComboboxEmpty>No framework found.</ComboboxEmpty>
          </ComboboxContent>
        </Combobox>
      </div>
    );
  },
};

export const WithIcons: Story = {
  render: () => {
    const users = ["Jane Doe", "John Smith", "Alice Kim", "Tom Walker"];
    const [value, setValue] = useState<string | null>(null);
    return (
      <div className="w-72">
        <Combobox items={users} value={value} onValueChange={setValue}>
          <ComboboxInput placeholder="Assign to a user…" />
          <ComboboxContent>
            <ComboboxList>
              {(user) => (
                <ComboboxItem key={user} value={user}>
                  <UserIcon />
                  {user}
                </ComboboxItem>
              )}
            </ComboboxList>
            <ComboboxEmpty>No user found.</ComboboxEmpty>
          </ComboboxContent>
        </Combobox>
      </div>
    );
  },
};
