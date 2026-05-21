import { NavLink as MantineNavLink } from "@mantine/core";
import { Link, useLocation } from "react-router";

/** The application's navigable sections, shown in the left menu. */
const SECTIONS = [
  { label: "Dashboard", to: "/" },
  { label: "Budgets", to: "/budgets" },
  { label: "Categories", to: "/categories" },
  { label: "Reports", to: "/reports" },
];

export function NavMenu() {
  const { pathname } = useLocation();

  return (
    <>
      {SECTIONS.map(({ label, to }) => {
        const active =
          to === "/" ? pathname === "/" : pathname.startsWith(to);
        return (
          <MantineNavLink
            key={to}
            component={Link}
            to={to}
            label={label}
            active={active}
          />
        );
      })}
    </>
  );
}
