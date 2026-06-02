import { Combobox, InputBase, useCombobox } from "@mantine/core";
import { type KeyboardEvent, useEffect, useState } from "react";

import { ApiError } from "../api/client";
import type { Category, CategoryCreate, CategoryKind } from "../api/types";

interface Props {
  /** The full global category list; filtered to `kind` internally. */
  categories: Category[];
  /** The active kind gate. While `null`, the picker is disabled. */
  kind: CategoryKind | null;
  /** Selected category id, or `null` when nothing is chosen. */
  value: number | null;
  onChange: (categoryId: number | null) => void;
  /** Creates a category and resolves with it; used for inline creation. */
  onCreateCategory: (data: CategoryCreate) => Promise<Category>;
  label?: string;
  error?: string;
}

/** Sentinel option value for the "create" row. */
const CREATE_VALUE = "$create";

/**
 * Searchable, creatable category picker built on Mantine's `Combobox`.
 *
 * The picker is gated by `kind`: it is disabled until a kind is chosen, and
 * only ever offers categories of that kind, so a wrong-kind category is never
 * selectable. Type to filter; **Tab** accepts the best match; **Enter** selects
 * an exact match or creates when none exists; the "＋ Create" row is the mouse
 * path. A new category inherits the active kind.
 */
export function CategoryCombobox({
  categories,
  kind,
  value,
  onChange,
  onCreateCategory,
  label = "Category",
  error,
}: Props) {
  const combobox = useCombobox({
    onDropdownClose: () => combobox.resetSelectedOption(),
    onDropdownOpen: () => combobox.selectFirstOption(),
  });

  const disabled = kind == null;
  const options = categories.filter((c) => c.kind === kind);
  const selected = options.find((c) => c.id === value) ?? null;

  const [search, setSearch] = useState(selected?.name ?? "");
  const [createError, setCreateError] = useState<string>();

  const query = search.trim();
  const filtered = options.filter((c) =>
    c.name.toLowerCase().includes(query.toLowerCase()),
  );
  const exactMatch = options.find(
    (c) => c.name.trim().toLowerCase() === query.toLowerCase(),
  );
  const showCreate = query !== "" && !exactMatch;

  // Clear a selection whose kind no longer matches the active kind — e.g. after
  // the kind gate is flipped, or a legacy mismatched record is opened for edit.
  // Only act on a *known* category with the wrong kind; an unknown id may be a
  // freshly created category not yet present in the reloaded list.
  useEffect(() => {
    const known = categories.find((c) => c.id === value);
    if (value != null && known && known.kind !== kind) {
      onChange(null);
      setSearch("");
    }
  }, [kind, categories, value, onChange]);

  function selectCategory(categoryId: number) {
    onChange(categoryId);
    setSearch(options.find((c) => c.id === categoryId)?.name ?? "");
    setCreateError(undefined);
    combobox.closeDropdown();
  }

  async function createCategory() {
    if (kind == null || query === "") {
      return;
    }
    setCreateError(undefined);
    try {
      const created = await onCreateCategory({ name: query, kind });
      onChange(created.id);
      setSearch(created.name);
      combobox.closeDropdown();
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Unexpected error");
    }
  }

  function handleOptionSubmit(val: string) {
    if (val === CREATE_VALUE) {
      void createCategory();
      return;
    }
    selectCategory(Number(val));
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (disabled) {
      return;
    }
    if (event.key === "Enter") {
      event.preventDefault();
      if (exactMatch) {
        selectCategory(exactMatch.id);
      } else if (query !== "") {
        void createCategory();
      } else if (filtered[0]) {
        selectCategory(filtered[0].id);
      }
    } else if (event.key === "Tab" && query !== "" && filtered[0]) {
      // Accept the highlighted (best) match and let focus advance. No creation
      // on Tab — an unmatched query just leaves the field.
      selectCategory(filtered[0].id);
    }
  }

  return (
    <Combobox store={combobox} onOptionSubmit={handleOptionSubmit}>
      {/* We own the keyboard contract (Tab = best match, Enter = exact-or-
          create) in `handleKeyDown`. Mantine's built-in navigation is disabled
          so Enter is not also handled as "submit the active option", which
          would fire a second create and 409 on the duplicate. */}
      <Combobox.Target withKeyboardNavigation={false}>
        <InputBase
          label={label}
          placeholder={
            disabled ? "Choose a kind first" : "Search or create a category"
          }
          value={search}
          disabled={disabled}
          error={error ?? createError}
          rightSection={<Combobox.Chevron />}
          rightSectionPointerEvents="none"
          onChange={(event) => {
            combobox.openDropdown();
            setSearch(event.currentTarget.value);
            setCreateError(undefined);
            combobox.selectFirstOption();
          }}
          onClick={() => combobox.openDropdown()}
          onFocus={() => combobox.openDropdown()}
          onBlur={() => {
            combobox.closeDropdown();
            setSearch(selected?.name ?? "");
          }}
          onKeyDown={handleKeyDown}
        />
      </Combobox.Target>
      <Combobox.Dropdown>
        <Combobox.Options>
          {filtered.map((category) => (
            <Combobox.Option value={String(category.id)} key={category.id}>
              {category.name}
            </Combobox.Option>
          ))}
          {showCreate && (
            <Combobox.Option value={CREATE_VALUE}>
              ＋ Create “{query}”
            </Combobox.Option>
          )}
          {!showCreate && filtered.length === 0 && (
            <Combobox.Empty>No categories</Combobox.Empty>
          )}
        </Combobox.Options>
      </Combobox.Dropdown>
    </Combobox>
  );
}
