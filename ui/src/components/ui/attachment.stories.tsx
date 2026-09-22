import type { Meta, StoryObj } from "@storybook/react";
import { DownloadIcon, FileTextIcon, Trash2Icon, XIcon } from "lucide-react";
import { Spinner } from "./spinner";
import {
  Attachment,
  AttachmentAction,
  AttachmentActions,
  AttachmentContent,
  AttachmentDescription,
  AttachmentGroup,
  AttachmentMedia,
  AttachmentTitle,
} from "./attachment";

const meta = {
  title: "UI/Attachment",
  component: Attachment,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    state: { control: "select", options: ["idle", "uploading", "processing", "error", "done"] },
    size: { control: "select", options: ["default", "sm", "xs"] },
    orientation: { control: "select", options: ["horizontal", "vertical"] },
  },
} satisfies Meta<typeof Attachment>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Done: Story = {
  render: (args) => (
    <Attachment {...args}>
      <AttachmentMedia>
        <FileTextIcon />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>quarterly-report.pdf</AttachmentTitle>
        <AttachmentDescription>2.4 MB · PDF</AttachmentDescription>
      </AttachmentContent>
      <AttachmentActions>
        <AttachmentAction aria-label="Download">
          <DownloadIcon />
        </AttachmentAction>
        <AttachmentAction aria-label="Remove">
          <Trash2Icon />
        </AttachmentAction>
      </AttachmentActions>
    </Attachment>
  ),
};

export const Idle: Story = {
  args: { state: "idle" },
  render: (args) => (
    <Attachment {...args}>
      <AttachmentMedia>
        <FileTextIcon />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>Ready to upload</AttachmentTitle>
        <AttachmentDescription>Click to choose a file</AttachmentDescription>
      </AttachmentContent>
    </Attachment>
  ),
};

export const Uploading: Story = {
  args: { state: "uploading" },
  render: (args) => (
    <Attachment {...args}>
      <AttachmentMedia>
        <Spinner />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>quarterly-report.pdf</AttachmentTitle>
        <AttachmentDescription>Uploading… 45%</AttachmentDescription>
      </AttachmentContent>
      <AttachmentActions>
        <AttachmentAction aria-label="Cancel">
          <XIcon />
        </AttachmentAction>
      </AttachmentActions>
    </Attachment>
  ),
};

export const Processing: Story = {
  args: { state: "processing" },
  render: (args) => (
    <Attachment {...args}>
      <AttachmentMedia>
        <FileTextIcon />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>Extracting text…</AttachmentTitle>
        <AttachmentDescription>Processing file</AttachmentDescription>
      </AttachmentContent>
    </Attachment>
  ),
};

export const Error: Story = {
  args: { state: "error" },
  render: (args) => (
    <Attachment {...args}>
      <AttachmentMedia>
        <FileTextIcon />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>quarterly-report.pdf</AttachmentTitle>
        <AttachmentDescription>Upload failed. File is too large.</AttachmentDescription>
      </AttachmentContent>
      <AttachmentActions>
        <AttachmentAction variant="destructive" aria-label="Remove">
          <Trash2Icon />
        </AttachmentAction>
      </AttachmentActions>
    </Attachment>
  ),
};

export const Vertical: Story = {
  args: { orientation: "vertical" },
  render: (args) => (
    <Attachment {...args}>
      <AttachmentMedia>
        <FileTextIcon />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>cover.png</AttachmentTitle>
        <AttachmentDescription>3.1 MB · PNG</AttachmentDescription>
      </AttachmentContent>
    </Attachment>
  ),
};

export const Small: Story = {
  args: { size: "sm" },
  render: (args) => (
    <Attachment {...args}>
      <AttachmentMedia>
        <FileTextIcon />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>readme.md</AttachmentTitle>
        <AttachmentDescription>18 KB · Markdown</AttachmentDescription>
      </AttachmentContent>
      <AttachmentActions>
        <AttachmentAction aria-label="Remove">
          <Trash2Icon />
        </AttachmentAction>
      </AttachmentActions>
    </Attachment>
  ),
};

export const Group: Story = {
  render: (args) => (
    <div className="w-[28rem]">
      <AttachmentGroup {...args}>
        <Attachment>
          <AttachmentMedia>
            <FileTextIcon />
          </AttachmentMedia>
          <AttachmentContent>
            <AttachmentTitle>report.pdf</AttachmentTitle>
            <AttachmentDescription>2.4 MB</AttachmentDescription>
          </AttachmentContent>
        </Attachment>
        <Attachment>
          <AttachmentMedia>
            <FileTextIcon />
          </AttachmentMedia>
          <AttachmentContent>
            <AttachmentTitle>budget.xlsx</AttachmentTitle>
            <AttachmentDescription>1.1 MB</AttachmentDescription>
          </AttachmentContent>
        </Attachment>
        <Attachment>
          <AttachmentMedia>
            <FileTextIcon />
          </AttachmentMedia>
          <AttachmentContent>
            <AttachmentTitle>notes.txt</AttachmentTitle>
            <AttachmentDescription>4 KB</AttachmentDescription>
          </AttachmentContent>
        </Attachment>
      </AttachmentGroup>
    </div>
  ),
};
