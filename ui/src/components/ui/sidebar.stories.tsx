import type { Meta, StoryObj } from "@storybook/react";
import {
  AudioWaveformIcon,
  BookOpenIcon,
  BotIcon,
  GalleryVerticalEndIcon,
  HomeIcon,
  Settings2Icon,
  ShoppingCartIcon,
} from "lucide-react";
import { Sidebar as ShadcnSidebar } from "./sidebar";
import {
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarSeparator,
} from "./sidebar";

const meta = {
  title: "UI/Sidebar",
  component: ShadcnSidebar,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof ShadcnSidebar>;

export default meta;
type Story = StoryObj<typeof meta>;

const navItems = [
  { title: "Home", icon: HomeIcon, isActive: true },
  { title: "Orders", icon: ShoppingCartIcon, badge: "12" },
  { title: "Documentation", icon: BookOpenIcon },
  { title: "Settings", icon: Settings2Icon },
];

export const Default: Story = {
  render: (args) => (
    <div className="w-80 rounded-3xl border p-4">
      <SidebarProvider {...args} defaultOpen>
        <ShadcnSidebar collapsible="none" className="w-full">
          <SidebarHeader>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton size="lg">
                  <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <AudioWaveformIcon className="size-4" />
                  </div>
                  <div className="flex flex-col gap-0.5 leading-none">
                    <span className="font-heading text-sm font-medium">Acme Inc.</span>
                    <span className="text-xs text-sidebar-foreground/70">Enterprise</span>
                  </div>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>Platform</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton isActive={item.isActive} tooltip={item.title}>
                        <item.icon />
                        <span>{item.title}</span>
                        {item.badge && <SidebarMenuBadge>{item.badge}</SidebarMenuBadge>}
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
            <SidebarSeparator />
            <SidebarGroup>
              <SidebarGroupLabel>Projects</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton>
                      <BotIcon />
                      <span>AI Assistant</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton>
                      <GalleryVerticalEndIcon />
                      <span>Design System</span>
                    </SidebarMenuButton>
                    <SidebarMenuBadge>3</SidebarMenuBadge>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
          <SidebarFooter>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton>
                  <Settings2Icon />
                  <span>Settings</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarFooter>
          <SidebarRail />
        </ShadcnSidebar>
      </SidebarProvider>
    </div>
  ),
};
