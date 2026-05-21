import { Text, Title } from "@mantine/core";

export function NotFoundPage() {
  return (
    <>
      <Title order={2}>Page not found</Title>
      <Text mt="sm">The page you requested does not exist.</Text>
    </>
  );
}
