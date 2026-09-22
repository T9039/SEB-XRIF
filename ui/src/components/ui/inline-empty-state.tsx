import { Empty, EmptyHeader, EmptyTitle, EmptyDescription, EmptyMedia } from "./empty";

interface InlineEmptyStateProps {
  icon?: React.ComponentType<{ className?: string }>;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

function InlineEmptyState({ icon: Icon, title, description, action }: InlineEmptyStateProps) {
  return (
    <Empty>
      <EmptyHeader>
        {Icon && (
          <EmptyMedia variant="icon">
            <Icon className="size-5" />
          </EmptyMedia>
        )}
        <EmptyTitle>{title}</EmptyTitle>
        {description && <EmptyDescription>{description}</EmptyDescription>}
      </EmptyHeader>
      {action}
    </Empty>
  );
}

export { InlineEmptyState };
export type { InlineEmptyStateProps };
