import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import {
  seedCategory,
  seedTemplate,
} from "../mocks/handlers";
import { TemplatesPage } from "../pages/TemplatesPage";
import { renderWithProviders } from "../test-utils";

describe("TemplatesPage", () => {
  test("shows the empty state when there are no templates", async () => {
    renderWithProviders(<TemplatesPage />);
    expect(
      await screen.findByText(/no templates yet/i),
    ).toBeInTheDocument();
  });

  test("lists existing templates", async () => {
    seedTemplate("Monthly");
    seedTemplate("Annual");
    renderWithProviders(<TemplatesPage />);
    expect(await screen.findByText("Monthly")).toBeInTheDocument();
    expect(screen.getByText("Annual")).toBeInTheDocument();
  });

  test("creates a template", async () => {
    renderWithProviders(<TemplatesPage />);
    await screen.findByText(/no templates yet/i);

    await userEvent.click(
      screen.getByRole("button", { name: /new template/i }),
    );
    await userEvent.type(await screen.findByLabelText(/Name/), "Monthly");
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Create" }),
    );

    expect(await screen.findByText("Monthly")).toBeInTheDocument();
  });

  test("opens a template's detail and shows its items", async () => {
    const food = seedCategory({ name: "Food", kind: "expense" });
    seedTemplate("Monthly", [
      { category_id: food.id, planned_amount: "200.00" },
    ]);
    renderWithProviders(<TemplatesPage />);
    await userEvent.click(await screen.findByRole("button", { name: "Open" }));

    const dialog = await screen.findByRole("dialog");
    expect(
      within(dialog).getByRole("heading", { name: "Monthly" }),
    ).toBeInTheDocument();
    expect(within(dialog).getByText("Food")).toBeInTheDocument();
    expect(within(dialog).getByText("200.00")).toBeInTheDocument();
  });

  test("removes a line item from a template", async () => {
    const food = seedCategory({ name: "Food", kind: "expense" });
    seedTemplate("Monthly", [
      { category_id: food.id, planned_amount: "200.00" },
    ]);
    renderWithProviders(<TemplatesPage />);
    await userEvent.click(await screen.findByRole("button", { name: "Open" }));
    const dialog = await screen.findByRole("dialog");
    await within(dialog).findByText("Food");

    await userEvent.click(
      within(dialog).getByRole("button", { name: "Remove" }),
    );

    await waitFor(() => {
      expect(within(dialog).queryByText("Food")).not.toBeInTheDocument();
    });
    expect(within(dialog).getByText(/no line items yet/i)).toBeInTheDocument();
  });

  test("deletes a template", async () => {
    seedTemplate("Old");
    renderWithProviders(<TemplatesPage />);
    await screen.findByText("Old");

    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Delete" }),
    );

    await waitFor(() =>
      expect(screen.queryByText("Old")).not.toBeInTheDocument(),
    );
  });

  test("refuses an empty name", async () => {
    renderWithProviders(<TemplatesPage />);
    await userEvent.click(
      await screen.findByRole("button", { name: /new template/i }),
    );
    const dialog = await screen.findByRole("dialog");
    // Empty submit: the required input prevents submission; modal stays open.
    fireEvent.submit(dialog.querySelector("form")!);
    expect(
      within(dialog).getByRole("button", { name: "Create" }),
    ).toBeInTheDocument();
  });
});
