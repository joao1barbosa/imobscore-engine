import { Outlet } from "react-router-dom";

export function Layout() {
  return (
    <div className="mx-auto flex min-h-svh w-full max-w-5xl flex-col gap-4 px-4 py-6">
      <Outlet />
    </div>
  );
}
