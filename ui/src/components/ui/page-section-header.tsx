import { Fragment } from "react";
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "./breadcrumb";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface PageSectionHeaderProps {
  breadcrumb: BreadcrumbItem[];
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

function PageSectionHeader({ breadcrumb, title, description, actions }: PageSectionHeaderProps) {
  return (
    <>
      <Breadcrumb className="mb-6">
        <BreadcrumbList>
          {breadcrumb.map((item, idx) => (
            <Fragment key={idx}>
              {idx > 0 && <BreadcrumbSeparator />}
              <BreadcrumbItem>
                {idx === breadcrumb.length - 1 ? (
                  <BreadcrumbPage className="font-semibold">{item.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink>{item.label}</BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
          {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </>
  );
}

export { PageSectionHeader };
export type { PageSectionHeaderProps };
