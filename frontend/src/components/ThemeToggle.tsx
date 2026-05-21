import {
  ActionIcon,
  useComputedColorScheme,
  useMantineColorScheme,
} from "@mantine/core";

/** Header control that switches between the light and dark themes. */
export function ThemeToggle() {
  const { setColorScheme } = useMantineColorScheme();
  const computed = useComputedColorScheme("light", {
    getInitialValueInEffect: true,
  });

  return (
    <ActionIcon
      variant="default"
      size="lg"
      aria-label="Toggle color scheme"
      onClick={() => setColorScheme(computed === "dark" ? "light" : "dark")}
    >
      {computed === "dark" ? "☀" : "☾"}
    </ActionIcon>
  );
}
