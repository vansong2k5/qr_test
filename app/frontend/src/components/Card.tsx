import { PropsWithChildren } from "react";

export const Card = ({ children }: PropsWithChildren) => (
  <div className="border rounded-lg shadow-sm bg-white dark:bg-slate-900 p-4">{children}</div>
);

export const CardHeader = ({ children }: PropsWithChildren) => (
  <div className="mb-2 text-muted-foreground">{children}</div>
);

export const CardTitle = ({ children }: PropsWithChildren) => (
  <h2 className="text-xl font-semibold">{children}</h2>
);

export const CardContent = ({ children }: PropsWithChildren) => <div>{children}</div>;
