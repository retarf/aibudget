import { useCallback, useEffect, useState } from "react";

import { ApiError } from "../api/client";

export interface ApiResource<T> {
  data: T | undefined;
  loading: boolean;
  error: string | undefined;
  reload: () => void;
}

/**
 * Fetches a resource and tracks loading/error state.
 *
 * `deps` controls when the fetch re-runs (e.g. an id or a filter); `reload()`
 * refetches on demand, typically after a mutation.
 */
export function useApiResource<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
): ApiResource<T> {
  const [data, setData] = useState<T>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const load = useCallback(() => {
    setLoading(true);
    setError(undefined);
    fetcher()
      .then((result) => setData(result))
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Unexpected error"),
      )
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}
