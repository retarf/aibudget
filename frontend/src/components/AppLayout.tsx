import { AppShell, Burger, Group, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Outlet } from "react-router";

import { NavMenu } from "./NavMenu";
import { ThemeToggle } from "./ThemeToggle";

/** The application shell: a header, a left navigation menu, and the content. */
export function AppLayout() {
  const [opened, { toggle }] = useDisclosure();

  return (
    <AppShell
      header={{ height: 56 }}
      navbar={{
        width: 240,
        breakpoint: "sm",
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger
              opened={opened}
              onClick={toggle}
              hiddenFrom="sm"
              size="sm"
              aria-label="Toggle navigation"
            />
            <Title order={3}>aibudget</Title>
          </Group>
          <ThemeToggle />
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <NavMenu />
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
